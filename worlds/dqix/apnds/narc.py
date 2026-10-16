# apnds/narc.py
#
# Copyright (C) 2025-2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

"""
:synopsis: Manipulation of NARC files.

The ``narc`` package contains a single structure, whose purpose is to handle `NARC` files.
"""

from .rom import get_filename_id_map, path_key_to_path, path_key

from collections.abc import Mapping, MutableMapping, MutableSequence
from dataclasses import dataclass
from struct import pack, pack_into, unpack_from
from typing import Optional, Tuple

HEADER_MAGIC = 0x4352414E
HEADER_LE_BOM = 0xFFFE
HEADER_VERSION_MARKER = 0x100

def construct_fntb_forced_ids(filename_id_map: Mapping[str, int]) -> bytes:
    header = bytes()
    contents = bytes()

    cur_dir = tuple()
    dir_map: MutableMapping[Tuple[str, ...], Tuple[int, MutableSequence[Tuple[str, Optional[int]]]]] = {}
    dir_map[()] = (0xF000, [])

    # within a directory, this will sort files by their id.
    def path_key_for_sorted(pk: Tuple[str, ...]) -> Tuple[str, ...]:
        return (*pk[:-1], f"\0{filename_id_map[path_key_to_path(*pk)]:04X}")

    paths = sorted(map(path_key, filename_id_map), key=path_key_for_sorted)

    for pk in paths:
        parent_dir = pk[:-1]
        for i, (l, r) in enumerate(zip(cur_dir, parent_dir)):
            if l != r:
                break
        else:
            i = min(len(cur_dir), len(parent_dir))
        for j in range(i + 1, len(parent_dir) + 1):
            dir_map[parent_dir[:j - 1]][1].append((parent_dir[j - 1], len(dir_map) | 0xF000))
            dir_map[parent_dir[:j]] = (len(dir_map) | 0xF000, [])
        cur_dir = parent_dir
        dir_map[parent_dir][1].append((pk[-1], None))

    header_len = len(dir_map) * 8
    for pk, (_, children) in dir_map.items():
        parent_id = dir_map[pk[:-1]][0] if len(pk) > 0 else len(dir_map)
        base_file_id = 0
        last_file_id = None
        len_contents_before = len(contents)
        for name, id_if_dir in children:
            contents += int.to_bytes(len(name) | (0x00 if id_if_dir is None else 0x80), 1)
            contents += name.encode('ascii')
            if id_if_dir is not None:
                contents += int.to_bytes(id_if_dir, 2, 'little')
            else:
                if last_file_id is None:
                    base_file_id = last_file_id = filename_id_map[path_key_to_path(*pk, name)]
                else:
                    this_file_id = filename_id_map[path_key_to_path(*pk, name)]
                    if this_file_id != last_file_id + 1:
                        raise ValueError("canont build fnt: nonconsecutive file ids within a directory (" + path_key_to_path(*pk, name) + ")")
                    last_file_id = this_file_id
        header += pack("<I2H", len_contents_before + header_len, base_file_id, parent_id)
        contents += b'\0'

    return header + contents

@dataclass
class Narc:
    """
    :synopsis: An unpacked NARC file.

    This class represents the contents of a NARC file in an accessible way.
    The original structure of a NARC file is documented below, in a C-like structure format.

    .. code-block:: c

       struct Narc {
           struct NarcHeader header;
           struct Fatb fatb;
           struct Fntb fntb;
           struct Fimg fimg;
       };

       struct NarcHeader {
           // 'NARC'
           u8 magic[4];
           // byte order mark. value of 0xFFFE. This package requires little-endian.
           u16 bom;
           // NARC version? Always expect 0x100.
           u16 version;
           // the size of the archive.
           u32 size;
           // (always 0x10)
           u16 header_size;
           // (always 3)
           u16 num_sections;
       };

       struct Fatb {
           // 'FATB' in little-endian
           u32 magic;
           // total length of FATB, including magic.
           u32 length;
           u32 num_file_entries;
           struct {
               // offsets within the file_contents of the FIMG.
               u32 start_off, end_off;
           } file_entries[num_file_entries];
       };

       struct Fntb {
           // 'FNTB' in little-endian
           u32 magic;
           // total length of FNTB, including magic.
           u32 length;
           struct {
               struct {
                   // offset of contents from start of header
                   u32 contents_offset;
                   // the file id of the first file in the directory
                   // following file ids are consecutive within the directory
                   u16 first_file_id;
                   // the id of the parent directory. for the root, this is
                   // the number of directory entries.
                   u16 parent_id;
               } directory_entries[number of directory entries];
           } header;
           struct {
               struct {
                   // children are null-terminated

                   // this union is not padded. i.e., the size is simply
                   // that of its value. so, a directory with no children
                   // would just be a single byte, with value 0.
                   union {
                       struct {
                           u8 name_length:7;
                           u8 is_dir:1;
                           u8 name[name_length];
                           // there is a dir_id if is_dir == 1.
                           union {
                               struct {
                                   u32 dir_id:24;
                                   u32 always_0xF:8;
                               } dir_id;
                               struct {} nothing;
                           } dir_id_or_nothing;
                       } child;
                       u8 null_terminator;
                   } children[number of children];
               } directory_contents[number of directory entries];
           } contents;
       };

       struct Fimg {
           // 'FIMG' in little-endian
           u32 magic;
           // total length of FIMG, including magic.
           u32 length;
           struct {
               u8 contents[length of file];
               // padded to a 4-byte boundary.
               u8 padding[];
           } file_contents[number of files];
       };
    """
    files: MutableSequence[bytes]
    """
    The files within the NARC.
    """
    filename_id_map: MutableMapping[str, int]
    """
    A map of file paths to indices within the array of files.
    """

    @staticmethod
    def from_bytes(data: bytes) -> "Narc":
        """
        Decompose the bytes of a NARC file.

        :param data: The bytes to decompose.
        :return: The decomposed NARC.
        :raises ValueError: If the data is not a valid NARC file.
        """
        magic, bom, version, size, header_size = unpack_from("<IHHIH", data, 0)
        
        if magic != HEADER_MAGIC:
            raise ValueError("data is not valid NARC. magic does not match")
        if bom != HEADER_LE_BOM:
            raise ValueError("data is not valid NARC. bom does not match")
        if version != HEADER_VERSION_MARKER:
            raise ValueError("data is not valid NARC. version does not match")
        if size != len(data):
            raise ValueError("data is not valid NARC. size does not match")

        fatb_pos = header_size
        if data[fatb_pos:fatb_pos + 4] != b'BTAF':
            raise ValueError("data is not valid NARC. FATB magic does not match")
        fatb_length, num_file_entries = unpack_from("<2I", data, fatb_pos + 4)
        fatb_ints = unpack_from(f"<{num_file_entries * 2}I", data, fatb_pos + 12)

        fntb_pos = fatb_pos + fatb_length
        if data[fntb_pos:fntb_pos + 4] != b'BTNF':
            raise ValueError("data is not valid NARC. FNTB magic does not match")
        fntb_len, = unpack_from("<I", data, fntb_pos + 4)

        fimg_pos = fntb_pos + fntb_len
        if data[fimg_pos:fimg_pos + 4] != b'GMIF':
            raise ValueError("data is not valid NARC. FIMG magic does not match")
        off = fimg_pos + 8

        file_data = data[off:]

        files = [file_data[fatb_ints[i]:fatb_ints[i + 1]] for i in range(0, 2 * num_file_entries, 2)]
        filename_id_map = get_filename_id_map(data[fntb_pos + 8:fntb_pos + fntb_len])

        return Narc(files, filename_id_map)

    def to_bytes(self) -> bytes:
        """
        Pack the archive into NARC format.

        :return: The packed NARC.
        :raises ValueError: If there is a directory within which the file ids cannot
                            be arranged in consecutive order.
        """
        fatb_contents = bytearray(8 * len(self.files))
        coff = 0
        for i, file in enumerate(self.files):
            pack_into("<2I", fatb_contents, 8 * i, coff, coff + len(file))
            coff += len(file)
            coff += -coff & 3
        fatb = pack("<4sII", b'BTAF', 12 + 8 * len(self.files), len(self.files)) + fatb_contents
        def padded_file(file: bytes, pad=b'\0') -> bytes:
            return file + pad * (-len(file) & 3)
        fimg = pack("<4sI", b'GMIF', coff + 8) + b''.join(padded_file(file) for file in self.files)
        fntb = padded_file(construct_fntb_forced_ids(self.filename_id_map), pad=b'\xFF')
        fntb = pack("<4sI", b'BTNF', 8 + len(fntb)) + fntb

        post_header = fatb + fntb + fimg

        header = pack("<IHHIHH", HEADER_MAGIC, HEADER_LE_BOM, HEADER_VERSION_MARKER, 0x10 + len(post_header), 0x10, 3)

        return header + post_header

__all__: list[str] = ['Narc']
