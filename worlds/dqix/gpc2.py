"""Read, modify, and rebuild Dragon Quest IX European GPC2 archives.

Python 3.10+; no third-party dependencies.

The :class:`GPC2` API exposes decompressed members through ``files`` and
preserves original compressed regions for members that have not changed.
``save()`` verifies the rebuilt archive by default. The command-line interface
is available through ``python gpc2.py --help``.

Compatibility: tested on the supplied European archive corpus. This module is
not a general Nintendo DS ROM editor and does not validate game asset formats.
"""
import argparse
import json
import sys
import struct
import zlib
import heapq
import itertools
import warnings
from pathlib import Path


def read_u32_le(data, offset):
    """Read an unsigned little-endian 32-bit integer with bounds checking."""
    b, p = data, offset
    if p < 0 or p + 4 > len(b): raise ValueError('Truncated 32-bit field')
    return struct.unpack_from('<I', b, p)[0]
def align4(size):
    """Round a byte count up to the next four-byte boundary."""
    return (size + 3) & ~3


# Compatibility alias for older scripts importing the original helper.
u32 = read_u32_le


def huffman(data, size, bits, encode=False, raw=None):
    """Decode or encode a headerless DS Huffman stream using its embedded tree.

    ``bits`` is 4 or 8; ``size`` is the expected decompressed byte count.
    Encoding requires ``raw`` and may fail when the tree lacks a symbol.
    """
    if not data: raise ValueError('Empty Huffman stream')
    n=(data[0]+1)*2
    if n > len(data) or n < 2: raise ValueError('Truncated Huffman tree')
    tree=data[:n]
    def children(pos):
        if pos < 0 or pos >= n: raise ValueError('Huffman node outside tree')
        v=tree[pos]; base=(pos&~1)+((v&63)+1)*2
        if base + 1 >= n: raise ValueError('Huffman child outside tree')
        return ((base, bool(v&128)),(base+1,bool(v&64)))
    if encode:
        codes={}
        def visit(pos, leaf, code):
            if leaf: codes[tree[pos]]=code; return
            for bit,(p,l) in enumerate(children(pos)): visit(p,l,code+(bit,))
        visit(1,False,())
        symbols=[]
        for byte in raw:
            if bits==4: symbols.extend((byte&15,byte>>4))
            else: symbols.append(byte)
        words=[]; word=0; count=0
        for sym in symbols:
            if sym not in codes: raise ValueError(f'Original Huffman tree lacks symbol {sym}')
            for bit in codes[sym]:
                word=(word<<1)|bit;count+=1
                if count==32: words.append(struct.pack('<I',word));word=count=0
        if count: words.append(struct.pack('<I',word<<(32-count)))
        return tree+b''.join(words)
    out=bytearray();pos=1; p=n;word=0;left=0;half=None
    steps=0;max_steps=max(64,size*64)
    while len(out)<size:
        steps+=1
        if steps>max_steps: raise ValueError('Huffman stream did not terminate')
        if left==0:
            if p+4>len(data): raise ValueError('Truncated Huffman bitstream')
            word=u32(data,p);p+=4;left=32
        bit=(word>>(left-1))&1;left-=1
        child,leaf=children(pos)[bit]
        if leaf:
            sym=tree[child]
            if bits==8:out.append(sym)
            elif half is None:half=sym
            else:out.append(half|(sym<<4));half=None
            pos=1
        else:pos=child
    return bytes(out)



def generate_huffman_tree(raw: bytes, bits: int) -> bytes:
    """Build Nintendo DS Huffman tree bytes (no BIOS header).

    Raises ValueError when the Nintendo 6-bit child-offset encoding cannot
    represent the generated tree; never silently emits a corrupt tree.
    """
    if bits not in (4, 8):
        raise ValueError("Huffman symbols must be 4 or 8 bits")
    symbols = ([n for byte in raw for n in (byte & 15, byte >> 4)]
               if bits == 4 else list(raw))
    from collections import Counter, deque
    freq = Counter(symbols)
    if not freq:
        freq[0] = 1
    if len(freq) == 1:
        extra = 0 if 0 not in freq else 1
        freq[extra] = 0
    seq = itertools.count()
    heap = [(count, symbol, next(seq), symbol) for symbol, count in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        heapq.heappush(heap, (a[0] + b[0], min(a[1], b[1]), next(seq), (a[3], b[3])))
    root = heap[0][3]
    tree = bytearray(2)
    queue = deque([(1, root)])
    while queue:
        pos, node = queue.popleft()
        if isinstance(node, int):
            tree[pos] = node
            continue
        left, right = node
        childpos = len(tree)
        if childpos > 511:
            raise ValueError("Huffman tree exceeds 512-byte DS limit")
        distance = childpos - (pos & ~1)
        if distance < 2 or distance % 2 or distance // 2 - 1 > 63:
            raise ValueError("Huffman tree cannot fit DS 6-bit relative offsets")
        flags = (0x80 if isinstance(left, int) else 0) | (0x40 if isinstance(right, int) else 0)
        tree[pos] = (distance // 2 - 1) | flags
        tree.extend(b"\0\0")
        queue.append((childpos, left))
        queue.append((childpos + 1, right))
    if len(tree) % 2:
        tree.append(0)
    tree[0] = len(tree) // 2 - 1
    return bytes(tree)


def lz_decode(data,size):
    """Decode headerless Nintendo LZ10 bytes to the declared output size."""
    out=bytearray();p=0
    while len(out)<size:
        if p>=len(data): raise ValueError('Truncated LZ flags')
        flags=data[p];p+=1
        for bit in range(7,-1,-1):
            if len(out)>=size:break
            if flags>>bit&1:
                if p+2>len(data): raise ValueError('Truncated LZ back-reference')
                a,b=data[p:p+2];p+=2;count=(a>>4)+3;dist=(((a&15)<<8)|b)+1
                if dist>len(out):raise ValueError('Invalid LZ reference')
                for _ in range(min(count,size-len(out))):out.append(out[-dist])
            else:
                if p>=len(data): raise ValueError('Truncated LZ literal')
                out.append(data[p]);p+=1
    return bytes(out)


def rle_decode(data,size):
    """Decode headerless Nintendo RLE bytes to the declared output size."""
    out=bytearray();p=0
    while len(out)<size:
        if p>=len(data): raise ValueError('Truncated RLE control')
        flag=data[p];p+=1
        if flag&128:
            if p>=len(data): raise ValueError('Truncated RLE repeat')
            run=(flag&127)+3
            if len(out)+run>size:raise ValueError('RLE repeat exceeds declared size')
            out.extend(data[p:p+1]*run);p+=1
        else:
            n=(flag&127)+1
            if p+n>len(data): raise ValueError('Truncated RLE literals')
            if len(out)+n>size:raise ValueError('RLE literals exceed declared size')
            out.extend(data[p:p+n]);p+=n
    return bytes(out[:size])


def decode_region(region):
    """Decode a GPC2 member region; return (uncompressed_bytes, codec_id)."""
    prefix=u32(region,0);codec=prefix&7;size=prefix>>3;payload=region[4:]
    if codec==0:
        if len(payload)<size:raise ValueError('Truncated stored region')
        out=payload[:size]
    elif codec==1:out=lz_decode(payload,size)
    elif codec in (2,3):out=huffman(payload,size,4 if codec==2 else 8)
    elif codec==4:out=rle_decode(payload,size)
    else:raise ValueError(f'Unsupported codec {codec}')
    if len(out)!=size:raise ValueError('Decoded size mismatch')
    return out,codec


def lz_encode(data):
    """Encode headerless Nintendo LZ10 with a bounded greedy match search."""
    out=bytearray()
    i=0
    while i<len(data):
        flag_pos=len(out);out.append(0)
        for bit in range(7,-1,-1):
            if i>=len(data):break
            best_len=0;best_dist=0
            start=max(0,i-4096)
            # Search recent occurrences first; overlap is valid for LZ10.
            for j in range(i-1,start-1,-1):
                if data[j]!=data[i]:continue
                n=1
                while n<18 and i+n<len(data) and data[j+n]==data[i+n]:n+=1
                if n>best_len:
                    best_len=n;best_dist=i-j
                    if n==18:break
            if best_len>=3:
                out[flag_pos]|=1<<bit
                d=best_dist-1
                out.extend((((best_len-3)<<4)|(d>>8),d&255))
                i+=best_len
            else:
                out.append(data[i]);i+=1
    return bytes(out)


def rle_encode(data):
    """Encode bytes using headerless Nintendo RLE."""
    out=bytearray();i=0
    while i<len(data):
        run=1
        while i+run<len(data) and data[i+run]==data[i] and run<130:
            run+=1
        if run>=3:
            out.extend((0x80 | (run-3),data[i]));i+=run
            continue
        start=i
        while i<len(data) and i-start<128:
            look=1
            while i+look<len(data) and data[i+look]==data[i] and look<3:
                look+=1
            if look>=3:
                break
            i+=1
        out.append(i-start-1)
        out.extend(data[start:i])
    return bytes(out)


def encode_region(raw, codec, original_region=None):
    """Encode a GPC2 region, optionally reusing an existing Huffman tree."""
    if len(raw)>=1<<29:raise ValueError('Region exceeds size limit')
    if codec==0:payload=raw
    elif codec==1:payload=lz_encode(raw)
    elif codec==4:payload=rle_encode(raw)
    elif codec in (2,3):
        bits = 4 if codec == 2 else 8
        tree = original_region[4:] if original_region is not None else None
        try:
            if tree is None:
                raise ValueError('No existing tree')
            payload = huffman(tree, len(raw), bits, True, raw)
        except ValueError:
            payload = huffman(generate_huffman_tree(raw, bits), len(raw), bits, True, raw)
    else:raise ValueError(f'Unsupported codec {codec}')
    return struct.pack('<I',(len(raw)<<3)|codec)+payload


class GPC2:
    """Mutable GPC2 archive with decoded member data.

    Construct from archive bytes or use :meth:`open` for a filesystem path.
    ``files`` maps case-sensitive member paths to decompressed bytes. Use
    :meth:`replace`, :meth:`add`, and :meth:`remove` to mark edits, then
    :meth:`to_bytes` or :meth:`save` to rebuild. Direct mutation of ``files`` is not tracked.

    ``whole`` indicates the stored-whole layout. ``index_codec`` and
    ``name_codec`` describe the original archive's table encodings.
    """
    def __init__(self, data):
        """Parse an archive and decode its index, filename table, and members."""
        self.original=bytes(data)
        b=self.original
        if len(b)<24:raise ValueError('Truncated GPC2 header')
        if b[:4]!=b'GPC2':raise ValueError('Not GPC2')
        self.header=b[:24];self.count=b[4]|((b[5]&15)<<8)
        self.name_start=struct.unpack_from('<H',b,8)[0]*4
        self.data_start=struct.unpack_from('<H',b,10)[0]*4
        self.whole=bool(u32(b,16)&(1<<28))
        if not (24<=self.name_start<self.data_start<=len(b)):
            raise ValueError('Invalid GPC2 section boundaries')
        if not 1<=self.count<=4095: raise ValueError('Invalid member count (expected 1..4095)')
        self.index_codec=None;self.index_tree=None
        index_bytes=b[24:self.name_start]
        expected=self.count*12
        candidates=[]
        if len(index_bytes)==expected:candidates.append(('plain',index_bytes))
        for codec,bits in [('huff4',4),('huff8',8)]:
            try:candidates.append((codec,huffman(index_bytes,expected,bits)))
            except (ValueError,IndexError):pass
        try:candidates.append(('lz',lz_decode(index_bytes,expected)))
        except (ValueError,IndexError):pass
        for codec,raw in candidates:
            if len(raw)!=expected:continue
            entries=[]
            for i in range(self.count):
                crc,a,c=struct.unpack_from('<III',raw,i*12)
                off=self.data_start+(a&0xffffff)*4
                length=c&0xffffff
                nameoff=(a>>24)|((c>>24)<<8)
                entries.append((crc,off,length,nameoff))
            spans=sorted((o,o+l) for _,o,l,_ in entries)
            valid_spans=all(self.data_start<=a<bnd<=len(b) for a,bnd in spans)
            no_overlap=all(spans[j-1][1]<=spans[j][0] for j in range(1,len(spans)))
            if (all(entries[i][0]<entries[i+1][0] for i in range(len(entries)-1))
                and valid_spans and no_overlap):
                self.index_codec=codec;self.entries=entries
                if codec.startswith('huff'):self.index_tree=index_bytes[:(index_bytes[0]+1)*2]
                break
        if self.index_codec is None:raise ValueError('Cannot decode index')
        names_blob=b[self.name_start:self.data_start]
        self.names_raw,self.name_codec=decode_region(names_blob)
        if self.names_raw and not self.names_raw.endswith(b'\0'):
            raise ValueError('Unterminated filename table')
        self.name_region=names_blob
        self.files={};self.raw_regions={}
        # ArchiveTool-produced stored-whole archives can use ordinal filename
        # indices instead of byte offsets. Select the interpretation only if
        # every index CRC matches its corresponding filename.
        try:
            name_list=[x.decode('ascii') for x in self.names_raw.split(b'\0') if x]
        except UnicodeDecodeError as exc:
            raise ValueError('Invalid ASCII filename table') from exc
        def decode_names(ordinal):
            found=[]
            for crc,off,length,nameoff in self.entries:
                if ordinal:
                    if nameoff>=len(name_list):return None
                    name=name_list[nameoff]
                else:
                    if nameoff>=len(self.names_raw):return None
                    name=self.names_raw[nameoff:].split(b'\0',1)[0].decode('ascii')
                try: self._check_name(name)
                except (ValueError,UnicodeError): return None
                if zlib.crc32(name.encode('ascii'))&0xffffffff!=crc:return None
                found.append(name)
            return found if len(set(found))==len(found) else None
        decoded=decode_names(False)
        self.ordinal_names=False
        if decoded is None and self.whole:
            decoded=decode_names(True)
            self.ordinal_names=decoded is not None
        if decoded is None:raise ValueError('Filename index/CRC mismatch')
        for (crc,off,length,nameoff),name in zip(self.entries,decoded):
            region=b[off:off+length]
            self.files[name]=region if self.whole else decode_region(region)[0]
            self.raw_regions[name]=region
        self.names=list(self.files)
        self.modified=set();self.new_codecs={}

    @classmethod
    def open(cls,path):
        """Load a GPC2 archive from a filesystem path."""
        return cls(Path(path).read_bytes())
    def list(self):
        """Return member names in CRC-index order."""
        return list(self.files)
    def add(self,name,data,codec=None):
        """Add an uncompressed member, choosing a codec if none is supplied.

        Codec IDs: 0 stored, 1 LZ77, 2 Huffman-4, 3 Huffman-8, 4 RLE.
        """
        self._check_name(name)
        if name in self.files: raise ValueError("Member already exists: "+name)
        if len(self.files)>=4095: raise ValueError("GPC2 member count limit")
        if codec is None:
            codec=0 if self.whole or not self.names else (u32(self.raw_regions[self.names[0]],0)&7)
        if not self.whole and codec not in (0,1,2,3,4):
            raise ValueError("New members require codec 0 through 4")
        self.files[name]=bytes(data);self.names.append(name);self.modified.add(name)
        self.new_codecs[name]=codec

    def remove(self,name):
        """Remove an existing member; raise KeyError if it is absent."""
        if name not in self.files:raise KeyError(name)
        del self.files[name];self.names.remove(name);self.modified.discard(name)
        self.new_codecs.pop(name,None)

    @staticmethod
    def _check_name(name):
        """Validate an ASCII member path and reject unsafe path components."""
        if not isinstance(name,str) or not name or "\x00" in name or "\\" in name:
            raise ValueError("Invalid member name")
        if name.startswith("/") or any(part in ("", ".", "..") for part in name.split("/")):
            raise ValueError("Unsafe member name")
        name.encode("ascii")

    def replace(self, name, data):
        """Replace an existing member with raw uncompressed bytes."""
        if name not in self.files:raise KeyError(name)
        self.files[name]=bytes(data);self.modified.add(name)
    def extract_all(self, path):
        """Write decoded members to a directory, preserving relative paths."""
        root=Path(path);root.mkdir(parents=True,exist_ok=True)
        for name,data in self.files.items():
            dest=root/name
            if not dest.resolve().is_relative_to(root.resolve()):raise ValueError('Unsafe path')
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    def _encode_member(self, name, codec, original, allow_fallback):
        """Encode a modified member and optionally fall back to LZ77."""
        try:
            return encode_region(self.files[name], codec, original)
        except ValueError as exc:
            if not (allow_fallback and codec in (2, 3)):
                raise
            fallback = encode_region(self.files[name], 1)
            if decode_region(fallback)[0] != self.files[name]:
                raise ValueError("LZ77 fallback validation failed") from exc
            self.last_fallbacks.append((name, codec, 1, str(exc)))
            warnings.warn(f"{name}: Huffman-{4 if codec == 2 else 8} encoding failed; using LZ77", RuntimeWarning)
            return fallback

    def to_bytes(self, *, allow_codec_fallback=True, verify=True):
        """Build and return the complete GPC2 archive as ``bytes``.

        Unchanged members retain their original compressed data. Modified
        Huffman members may fall back to LZ77 when ``allow_codec_fallback``
        is true; such changes are recorded in ``last_fallbacks``. Index and
        filename-table codecs are never silently changed.

        With ``verify=True`` (the default), reparse the output and compare
        all decoded members before returning bytes. Raises ValueError for
        malformed or unrepresentable archives and NotImplementedError for
        unsupported index encodings.
        """
        self.last_fallbacks = []
        for name in self.files: self._check_name(name)
        if not 1<=len(self.files)<=4095:
            raise ValueError('GPC2 requires between 1 and 4095 members')
        crcs=[zlib.crc32(name.encode('ascii'))&0xffffffff for name in self.files]
        if len(set(crcs))!=len(crcs):
            raise ValueError('Member filename CRC32 collision')
        if set(self.names) != set(self.files) or len(self.names) != len(self.files):
            raise ValueError('Member name inventory inconsistent')
        # This original-style writer currently supports the stored-whole EU archives.
        if self.index_codec not in ('huff4','huff8','plain'):
            raise NotImplementedError('Index codec '+self.index_codec)
        # Preserve the original name table when names are unchanged.
        changed_names=set(self.files)!=set(self.raw_regions)
        if changed_names:
            name_offsets={};name_raw=bytearray()
            # ArchiveTool expects the filename table in alphabetical order.
            # The CRC-sorted index is a separate ordering.
            for name in sorted(self.files):
                self._check_name(name)
                if len(name_raw)>65535:raise ValueError("Name table offset limit")
                name_offsets[name]=len(name_offsets) if self.ordinal_names else len(name_raw)
                name_raw.extend(name.encode("ascii")+b"\0")
            name_region=encode_region(bytes(name_raw),self.name_codec,self.name_region)
        else:
            name_region=self.name_region
        # Rebuild offsets and lengths while retaining the original index Huffman tree.
        region=bytearray();rows=[]
        if not changed_names:
            name_offsets={}
            for _,_,_,noff in self.entries:
                name=self.names_raw.split(b'\0')[noff].decode('ascii') if self.ordinal_names else self.names_raw[noff:].split(b'\0',1)[0].decode('ascii');name_offsets[name]=noff
        # ArchiveTool consumes member payloads in filename order, even though
        # the entry table is sorted by CRC32. Keep these orderings separate.
        for name in sorted(self.files):
            if self.whole:
                blob=self.files[name]
            elif name not in self.modified:
                blob=self.raw_regions[name]
            elif name in self.new_codecs:
                blob=self._encode_member(name, self.new_codecs[name], None, allow_codec_fallback)
            else:
                old=self.raw_regions[name]
                codec=u32(old,0)&7
                blob=self._encode_member(name,codec,old,allow_codec_fallback)
            rel=len(region)//4
            if rel>0xffffff or len(blob)>0xffffff:raise ValueError('GPC2 entry limit exceeded')
            crc=zlib.crc32(name.encode('ascii'))&0xffffffff
            noff=name_offsets[name]
            if noff>65535:raise ValueError('Filename index exceeds 16-bit limit')
            rows.append((crc,rel|(noff&255)<<24,len(blob)|((noff>>8)<<24)))
            region.extend(blob);region.extend(b'\0'*(align4(len(region))-len(region)))
        rows.sort()
        index=b''.join(struct.pack('<III',*r) for r in rows)
        if self.index_codec=='plain':encoded=index
        else:
            bits = 4 if self.index_codec == 'huff4' else 8
            try:
                encoded = huffman(self.index_tree,len(index),bits,True,index)
            except ValueError:
                encoded = huffman(generate_huffman_tree(index,bits),len(index),bits,True,index)
        # Header stores name and data starts in 4-byte units, max 0xffff.
        name_start=align4(24+len(encoded))
        data_start=align4(name_start+len(name_region))
        if data_start//4>0xffff:raise ValueError('Header offset limit exceeded')
        hdr=bytearray(self.header)
        hdr[4]=(len(self.files)&255)
        hdr[5]=(hdr[5]&240)|((len(self.files)>>8)&15)
        struct.pack_into('<HH',hdr,8,name_start//4,data_start//4)
        # Redundant header metadata is consumed by the native ArchiveTool.
        # Keeping the original values when adding/removing members can hang it.
        struct.pack_into('<HH',hdr,12,len(self.files)*3,align4(len(self.names_raw if not changed_names else name_raw))//4)
        data_units=align4(len(region))//4
        original_data_field=u32(self.header,16)
        struct.pack_into('<I',hdr,16,(original_data_field & 0xf0000000)|data_units)
        original_count_field=u32(self.header,20)
        count_flags=original_count_field-self.count*96
        if not (0<=count_flags<96):
            raise ValueError('Unsupported count metadata flags')
        struct.pack_into('<I',hdr,20,len(self.files)*96+count_flags)
        output=bytes(hdr)+encoded
        output+=b'\0'*(name_start-len(output))+name_region
        output+=b'\0'*(data_start-len(output))+region
        if verify:
            check = GPC2(output)
            if check.files != self.files:
                raise ValueError("Rebuilt archive failed independent reopen/content comparison")
        return output

    def save(self, path, *, allow_codec_fallback=True, verify=True):
        """Rebuild the archive and write it to ``path`` after verification.

        See :meth:`to_bytes` for in-memory serialization and codec options.
        """
        output = self.to_bytes(
            allow_codec_fallback=allow_codec_fallback, verify=verify
        )
        Path(path).write_bytes(output)


CODEC_NAMES = {'stored': 0, 'lz77': 1, 'huff4': 2, 'huff8': 3, 'rle': 4}


def _cli_files(directory):
    """Read a directory recursively as member-name-to-bytes mappings."""
    root = Path(directory)
    if not root.is_dir():
        raise ValueError(f'Not a directory: {root}')
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(root.rglob('*')) if p.is_file()}


def _cli_save(archive, output, args):
    """Write a CLI archive, enforcing input/output separation and verification."""
    if Path(output).resolve() == Path(args.archive).resolve():
        raise ValueError('Refusing to overwrite input archive; choose a different output path')
    archive.save(output, verify=not args.no_verify,
                 allow_codec_fallback=not args.no_codec_fallback)
    print(f'Wrote {output} ({len(archive.files)} members)')
    if archive.last_fallbacks:
        print(f'Warning: {len(archive.last_fallbacks)} Huffman members fell back to LZ77', file=sys.stderr)


def main(argv=None):
    """Run the command-line interface; return a process exit status."""
    parser = argparse.ArgumentParser(description='Dragon Quest IX European GPC2 archive tool')
    sub = parser.add_subparsers(dest='cmd', required=True)

    command_parser = sub.add_parser('list', help='List members and archive properties')
    command_parser.add_argument('archive')
    command_parser.add_argument('--json', action='store_true', help='Machine-readable JSON output')

    command_parser = sub.add_parser('extract', help='Extract members to a directory')
    command_parser.add_argument('archive')
    command_parser.add_argument('destination')
    command_parser.add_argument('--force', action='store_true', help='Overwrite existing extracted files')

    command_parser = sub.add_parser('verify', help='Parse and decompress every member')
    command_parser.add_argument('archive')

    def add_save_flags(command_parser):
        """Register shared safety and codec-fallback flags."""
        command_parser.add_argument('--no-verify', action='store_true', help='Skip post-build reopen/content verification (not recommended)')
        command_parser.add_argument('--no-codec-fallback', action='store_true', help='Fail instead of switching failed Huffman encodes to LZ77')

    command_parser = sub.add_parser('rebuild', help='Rebuild with optional replacements, additions and removals')
    command_parser.add_argument('archive')
    command_parser.add_argument('destination')
    command_parser.add_argument('--replacements', help='Directory with replacement files (relative member paths)')
    command_parser.add_argument('--add-new', action='store_true', help='Allow unknown names in --replacements')
    command_parser.add_argument('--codec', choices=CODEC_NAMES, default=None, help='Codec for newly added members')
    command_parser.add_argument('--remove', action='append', default=[], metavar='MEMBER', help='Remove member (repeatable)')
    add_save_flags(command_parser)

    command_parser = sub.add_parser('replace', help='Replace one existing member')
    command_parser.add_argument('archive'); command_parser.add_argument('member'); command_parser.add_argument('file'); command_parser.add_argument('destination')
    add_save_flags(command_parser)

    command_parser = sub.add_parser('add', help='Add one new member')
    command_parser.add_argument('archive'); command_parser.add_argument('member'); command_parser.add_argument('file'); command_parser.add_argument('destination')
    command_parser.add_argument('--codec', choices=CODEC_NAMES, default=None)
    add_save_flags(command_parser)

    command_parser = sub.add_parser('remove', help='Remove one or more members')
    command_parser.add_argument('archive'); command_parser.add_argument('destination'); command_parser.add_argument('members', nargs='+')
    add_save_flags(command_parser)

    command_parser = sub.add_parser('pack', help='Pack a directory using an existing archive as a format template')
    command_parser.add_argument('archive', help='Original GPC2 template')
    command_parser.add_argument('directory', help='Directory of unpacked member files')
    command_parser.add_argument('destination')
    command_parser.add_argument('--sync', action='store_true', help='Add new files and remove template members absent from directory')
    command_parser.add_argument('--codec', choices=CODEC_NAMES, default=None, help='Codec for added members with --sync')
    add_save_flags(command_parser)

    args = parser.parse_args(argv)
    try:
        archive = GPC2.open(args.archive)
        if args.cmd == 'list':
            if args.json:
                print(json.dumps({'members': len(archive.files), 'index_codec': archive.index_codec,
                                  'stored_whole': archive.whole,
                                  'files': [{'name': member_name, 'size': len(archive.files[member_name])} for member_name in archive.list()]}, indent=2))
            else:
                print(f'Members: {len(archive.files)} | Index: {archive.index_codec} | Stored whole: {archive.whole}')
                for member_name in archive.list(): print(f'{len(archive.files[member_name]):>10}  {member_name}')
        elif args.cmd == 'verify':
            print(f'OK: {args.archive} ({len(archive.files)} members; all decompressed successfully)')
        elif args.cmd == 'extract':
            root = Path(args.destination)
            if root.exists() and not root.is_dir():
                raise ValueError(f'Extraction destination is not a directory: {root}')
            if not args.force:
                existing = [member_name for member_name in archive.files if (root / member_name).exists()]
                if existing: raise ValueError(f'Extraction would overwrite {existing[0]!r}; use --force')
            archive.extract_all(root)
            print(f'Extracted {len(archive.files)} members to {root}')
        else:
            if args.cmd == 'replace':
                archive.replace(args.member, Path(args.file).read_bytes())
            elif args.cmd == 'add':
                archive.add(args.member, Path(args.file).read_bytes(),
                      codec=CODEC_NAMES[args.codec] if args.codec else None)
            elif args.cmd == 'remove':
                for member_name in args.members:
                    archive.remove(member_name)
            elif args.cmd == 'rebuild':
                if args.replacements:
                    for member_name, member_data in _cli_files(args.replacements).items():
                        if member_name in archive.files:
                            archive.replace(member_name, member_data)
                        elif args.add_new:
                            archive.add(member_name, member_data, codec=CODEC_NAMES[args.codec] if args.codec else None)
                        else:
                            raise ValueError(f'Unknown member {member_name!r}; use --add-new')
                for member_name in args.remove:
                    archive.remove(member_name)
            elif args.cmd == 'pack':
                incoming = _cli_files(args.directory)
                if not args.sync:
                    missing = set(archive.files) - set(incoming)
                    extra = set(incoming) - set(archive.files)
                    if missing or extra:
                        raise ValueError(f'Pack directory differs from template: {len(missing)} missing, {len(extra)} extra (use --sync to add/remove)')
                else:
                    for member_name in list(archive.files):
                        if member_name not in incoming:
                            archive.remove(member_name)
                for member_name, member_data in incoming.items():
                    if member_name in archive.files:
                        if member_data != archive.files[member_name]:
                            archive.replace(member_name, member_data)
                    else:
                        archive.add(member_name, member_data, codec=CODEC_NAMES[args.codec] if args.codec else None)
            _cli_save(archive, args.destination, args)
        return 0
    except (ValueError, KeyError, OSError, NotImplementedError, UnicodeError) as exc:
        print(f'gpc2: error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
