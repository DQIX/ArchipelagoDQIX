# apnds/code.py
#
# Copyright (C) 2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

"""
:synopsis: Structures involving ARM9, ARM9i, ARM7, and ARM7i code.

The ``code`` package contains structures to parse the start params used within
the C runtimes of the ARM9 and ARM7 code. Using this data, it can then decompress the code
and split it into its automatically loaded sections. These can then be manipulated and reconstituted.
"""

from collections import defaultdict
from collections.abc import Mapping, MutableSequence, Sequence
from dataclasses import dataclass
from struct import pack, pack_into, unpack_from
from typing import Literal, Optional, Tuple

from .lz import decompress_code, compress_code

START_INFO_SIGNATURE_DS: bytes = bytes.fromhex("2106C0DEDEC00621")
START_INFO_SIGNATURE_DSI: bytes = bytes.fromhex("6314C0DEDEC01463")
CODE_HEADER_LEN_MAP: Mapping[Literal["7"] | Literal["9"], int] = {
    "7": 0x1000,
    "9": 0x4000,
}

@dataclass
class AutoloadSectionInfo:
    """
    :synopsis: Information about a single automatically-loaded code section.

    Certain sections of the code are automatically loaded
    to other memory addresses when the game starts.
    This class contains the information about one of these
    sections.

    This structure is found in two formats. The first is present in DS ROMs,
    and the second is present in some DSi ROMs.

    .. code-block:: c

       struct DSAutoloadSectionInfo {
           void *destination;
           u32 size;
           u32 bss_size;
       };

       struct DSiAutoloadSectionInfo {
           void *destination;
           u32 size;
           void *static_init_func_ptr;
           u32 bss_size;
       };
    """

    destination: int
    """
    To which address this section should be copied.
    """
    size: int
    """
    How much data should be copied to this section.
    """
    bss_size: int
    """
    How large the BSS data after this section's code is.
    The BSS data will be zeroed.
    """
    static_init_fun_ptr: Optional[int] = None
    """
    A pointer to the static initialization function called
    after for this section, after all sections are loaded.

    This field is only present on DSi-compatible ROMs.
    It will be ignored if set on DS ROMs.
    """
    
    @staticmethod
    def from_bytes_ds(code: bytes, offset: int = 0) -> "AutoloadSectionInfo":
        """
        Parse the autoload section info from bytes, assuming they are in the DS structure format.

        :param code: The data which contains the autoload section info.
        :param offset: The offset within the data at which the section info is.
        :return: The parsed autoload section info.
        """
        return AutoloadSectionInfo(*unpack_from("<3I", code, offset))

    @staticmethod
    def from_bytes_dsi(code: bytes, offset: int = 0) -> "AutoloadSectionInfo":
        """
        Parse the autoload section info from bytes, assuming they are in the DSi structure format.

        :param code: The data which contains the autoload section info.
        :param offset: The offset within the data at which the section info is.
        :return: The parsed autoload section info.
        """
        return AutoloadSectionInfo(**{
            k:v
            for k, v in zip(
                ["destination", "size", "static_init_fun_ptr", "bss_size"],
                unpack_from("<4I", code, offset),
            )
        })

    def to_bytes_ds(self, size: Optional[int] = None) -> bytes:
        """
        Pack the autoload section info into a DS-format structure.

        :param size: The size of the section. If not supplied, the size present in the class will be used.
        :return: The packed structure.
        """
        if size is None:
            size = self.size
        return pack("<3I", self.destination, size, self.bss_size)

    def to_bytes_dsi(self, size: Optional[int] = None) -> bytes:
        """
        Pack the autoload section info into a DSi-format structure.

        :param size: The size of the section. If not supplied, the size present in the class will be used.
        :return: The packed structure.
        """
        if size is None:
            size = self.size
        if self.static_init_fun_ptr is None:
            static_init_fun_ptr = 0
        else:
            static_init_fun_ptr = self.static_init_fun_ptr
        return pack("<4I", self.destination, size, static_init_fun_ptr, self.bss_size)

@dataclass
class CodeStartParams:
    """
    :synopsis: The start parameters of ARM9 or ARM7 code.

    This class contains the start parameters of the code.
    The start parameters are a structure present in ARM9 and ARM7
    code, within officially released DS and DSi games.
    It is located within the C runtime, so it will never be compressed. I have
    found two versions of it.

    .. code-block:: c
       
       struct DSNoCompressionStartParams {
           struct DSAutoloadSectionInfo *au_sec_info_start, *au_sec_info_end;
           void *au_secs_start;
           void *bss_start, *bss_end;
       };

       struct DSStartParams {
           // if the DSiStartParams structure is present, then
           // these are instead pointers to DSiAutoloadSectionInfo.
           struct DSAutoloadSectionInfo *au_sec_info_start, *au_sec_info_end;
           void *au_secs_start;
           void *bss_start, *bss_end;
           void *compressed_data_end;
           u32 sdk_version_id;
           // magic0, magic1 together make the hex byte sequence 2106C0DEDEC00621
           u32 magic0, magic1;
       };

    Within some (all?) DSi ROMs, the following structure may also be present. If it is,
    then the autoload section information will be in the DSi format for both
    the DS and DSi structures. The DSi structure is only relating to the
    ARM9i or ARM7i code.

    .. code-block:: c
       
       struct DSiStartParams {
           struct DSiAutoloadSectionInfo *au_sec_info_start, *au_sec_info_end;
           void *au_secs_start;
           void *compressed_data_end;
           // magic0, magic1 together make the hex byte sequence 6314C0DEDEC01463
           u32 magic0, magic1;
       };
    """

    autoload_sections: Tuple[int, int]
    """
    The address range containing the autoload section info.
    """
    autoload_start: int
    """
    The starting address to copy into the autoload sections.
    """
    bss_bounds: Tuple[int, int]
    """
    The bounds of the BSS segment of this code.
    This region is zeroed during the C runtime, before main is called.
    The endpoint is excluded. These must be on 4-byte boundaries.
    """
    compressed_end: Optional[int] = None
    """
    The end address of the compressed section of this code, if the code is compressed.
    """
    sdk_version: Optional[int] = None
    """
    The NITRO/TWL SDK version this code was made with.
    This is somewhat inconsistent. A 32-bit value.
    The top 8 bits should always be major version.
    """
    dsi_autoload_sections: Optional[Tuple[int, int]] = None
    """
    The address range containing the ARM i autoload section info,
    if it exists.
    """
    dsi_autoload_start: Optional[int] = None
    """
    The starting address to copy into the DSi autoload section info,
    if it exists.
    """
    dsi_compressed_end: Optional[int] = None
    """
    The end address of the compressed section of the DSi, if it exists.
    """

    @staticmethod
    def from_code(code: bytes, loadaddress: int, entrypoint: Optional[int] = None) -> Optional["CodeStartParams"]:
        """
        Try to find the code start parameters.
        This is only useful for official titles, not Homebrew ones.

        In some older titles, a certain signature is not present to help locate the start parameters structure.
        For these, a best-guess approach is used, scanning the area containing
        the C runtime for this structure. In this case, the sdk_version
        field will be None. For more details on this,
        see the try_find_start_info_no_signature function.

        :param code: The code from which to parse the starting parameters. This should be the ARM9 or ARM7 code.
        :param loadaddress: The address at which this code is loaded.
        :param entrypoint: The entrypoint of the code. This is only used for DS code which has the no compression version of the structure.
        :return: The code start parameters, if they could be found.
        """
        code_start_info_idx = code.find(START_INFO_SIGNATURE_DS)
        if code_start_info_idx == -1:
            # assuming now that this isn't compressed code, and is in an old (pre-DSi) game.
            # try to find start info by other means...
            if entrypoint is not None:
                code_start_info_idx = try_find_start_info_no_signature(code, loadaddress, entrypoint, True)
                if code_start_info_idx is None:
                    return None
                compressed_end = 0
                sdk_version = None
            else:
                return None
        else:
            compressed_end, sdk_version = unpack_from("<2I", code, code_start_info_idx - 8)
            code_start_info_idx -= 28

        codei_start_info_idx = code.find(START_INFO_SIGNATURE_DSI)
        if codei_start_info_idx == -1:
            codei_autoload_sections = codei_autoload_start = codei_compressed_end = None
        else:
            au_secs_start, au_secs_end, codei_autoload_start, codei_compressed_end = \
                unpack_from("<4I", code, codei_start_info_idx - 16)
            codei_autoload_sections = (au_secs_start, au_secs_end)
            if codei_compressed_end == 0:
                codei_compressed_end = None

        au_secs_start, au_secs_end, au_start, bss_start, bss_end = \
            unpack_from("<5I", code, code_start_info_idx)
        return CodeStartParams(
            (au_secs_start, au_secs_end),
            au_start,
            (bss_start, bss_end),
            compressed_end if compressed_end != 0 else None,
            sdk_version,
            codei_autoload_sections,
            codei_autoload_start,
            codei_compressed_end,
        )

    def get_sections(self, code: bytes, loadaddress: int, is_dsi: bool = False) -> Tuple[MutableSequence[Tuple[bytes, Optional[AutoloadSectionInfo]]], bytes]:
        """
        Given the start information of some code, the code, and the load
        address of the code, split the code into sections.

        If the code is compressed, this method will also decompress it.

        This function returns the sections, and the data that would
        be overwritten when decompressing, if the code is compressed.

        :param code: The code from which to get the sections.
                     This should correspond to the code these start parameters were obtained from.
                     For ARM9, ARM9 or ARM9i code. Similarly for ARM7.
        :param loadaddress: The address at which the code is loaded.
        :param is_dsi: Whether the code is DSi code (ARM9i or ARM7i).
        :return: The automatically loaded sections. The first member of the tuple is the sequence of sections. The first and last
                 entries of the sequence will not have section info; they correspond to the code before and after the sections.
                 All other entries in the sequence will have section info.

                 The second member of the tuple is the data which was in the code but after the compressed data,
                 so that it is overwritten when decompressed. If the code is not compressed, this will be empty.

                 If the autoload section info or autoload start fields are None for this code, then 
                 ``([(decompressed, None)], rem)`` will be returned, where ``rem`` is the remainder after
                 decompression, and ``decompressed`` is the decompressed code.
        """

        # decompress the code
        
        dp = "dsi_" if is_dsi else ""
        compressed_end = getattr(self, dp + "compressed_end")
        if compressed_end:
            code, rem = decompress_code(code, compressed_end - loadaddress)
        else:
            rem = bytes()

        # find out if we have the extra field in the autoload info
        # (why did nintendo do this to me)
        if self.dsi_autoload_sections is not None:
            # we are working with DSi-compatible code...
            # we have the extra field.
            autoload_fun = AutoloadSectionInfo.from_bytes_dsi
            autoload_size = 16
        else:
            autoload_fun = AutoloadSectionInfo.from_bytes_ds
            autoload_size = 12

        au_secs_offs: Optional[Tuple[int, int]] = getattr(self, dp + "autoload_sections")
        au_start: Optional[int] = getattr(self, dp + "autoload_start") - loadaddress
        if au_secs_offs is not None and au_start is not None:
            au_secs: Sequence[AutoloadSectionInfo] = [autoload_fun(code, off - loadaddress) for off in range(au_secs_offs[0], au_secs_offs[1], autoload_size)]
            cur_off = 0
            def get_amount(amount: int) -> bytes:
                nonlocal cur_off
                ret = code[cur_off:cur_off + amount]
                cur_off += amount
                return ret
            ret_seq: Sequence[Tuple[bytes, Optional[AutoloadSectionInfo]]] = []
            ret_seq.append((get_amount(au_start), None))
            ret_seq.extend(
                (get_amount(au.size), au)
                for au in au_secs
            )
            ret_seq.append((code[cur_off:], None))
            return (ret_seq, rem)
        else:
            return ([(code, None)], rem)

    def pack_code_from_sections(
        self,
        data: Tuple[Sequence[Tuple[bytes, Optional[AutoloadSectionInfo]]], bytes],
        loadaddress: int,
        which: Literal["9"] | Literal["7"],
        is_dsi: bool = False,
        try_compress: Optional[bool] = None,
        autoload_info_write_mode: Literal["overwrite"] | Literal["overwrite_and_expand"] | Literal["append"] = "overwrite",
    ) -> bytes:
        """
        Given sections in the format returned by get_sections, pack the code back together.

        This method modifies the autoload fields of this structure according to the supplied parameters.
        After the code is re-packed, the ``CodeStartParams.write_start_info`` method should be called on the non-DSi code
        to write the new autoload fields.

        :param data: The data to be packed. This should be in the same format as returned by ``CodeStartParams.get_sections``.
        :param loadaddress: The address at which the code is loaded.
        :param which: Whether this code is ARM9 or ARM7 code.
        :param is_dsi: Whether this code is DS or DSi code.
        :param try_compress: Whether to try or compress the code or not. If this parameter is not supplied, then compression will be tried
                             only if the code was originally compressed. If setting this parameter to ``True``, ensure that the ``compressed_data_end``
                             field is present in the start parameters structure in the code.
        :param autoload_info_write_mode: How the autoload section info is inserted in the code.

                                         If the value is "overwrite", then this method
                                         will only overwrite the sections if there is enough room where the section
                                         info was previously. If there is not enough room, a ValueError will be raised.

                                         If the value is "overwrite_and_expand", then the method
                                         will push back the data after the autoload section info, if necessary.

                                         If the value is "append", then the autoload section info will be appended to the end of
                                         the code.
        :return: The packed code.
        :raises ValueError: If the code is to be compressed, but after combining all the sections, it is not padded to a 4-byte boundary.
        :raises ValueError: If ``autoload_info_write_mode`` is ``overwrite`` and there is not enough room in the original structure to overwrite it.
        """
        dp = "dsi_" if is_dsi else ""

        seq, rem = data

        if try_compress is None:
            try_compress = getattr(self, dp + "compressed_end") is not None

        if self.dsi_autoload_sections is not None:
            # we are working with DSi-compatible code...
            # we have the extra field.
            autoload_fun = AutoloadSectionInfo.to_bytes_dsi
            autoload_size = 16
        else:
            autoload_fun = AutoloadSectionInfo.to_bytes_ds
            autoload_size = 12

        autoload_sec_info = b''.join(autoload_fun(au, len(bts)) for bts, au in seq[1:-1]) # type: ignore
        old_au_start, old_au_end = getattr(self, dp + "autoload_sections")
        if autoload_info_write_mode == "overwrite":
            if len(autoload_sec_info) > old_au_end - old_au_start:
                raise ValueError("autoload info write mode is overwrite, but there are now more autoload sections to write")
            after_secs_data = autoload_sec_info + seq[-1][0][len(autoload_sec_info):]
            au_secs_start = 0
        elif autoload_info_write_mode == "overwrite_and_expand":
            if len(autoload_sec_info) > old_au_end - old_au_start:
                # expand
                after_secs_data = autoload_sec_info + seq[-1][0][old_au_end - old_au_start:]
            else:
                # overwrite
                after_secs_data = autoload_sec_info + seq[-1][0][len(autoload_sec_info):]
            au_secs_start = 0
        elif autoload_info_write_mode == "append":
            au_secs_start = len(seq[-1][0])
            after_secs_data = seq[-1][0] + autoload_sec_info
        uncompressed_code = b''.join(bts for bts, _ in seq[:-1])
        au_secs_start += len(uncompressed_code) + loadaddress
        uncompressed_code += after_secs_data
        au_secs_end = au_secs_start + (len(seq) - 2) * autoload_size
        au_start = len(seq[0][0]) + loadaddress
        hdr_len = 0 if is_dsi else CODE_HEADER_LEN_MAP[which]

        ret = None
        compressed_end = None
        if try_compress:
            if len(uncompressed_code) & 3 != 0:
                raise ValueError("code to compress is not word-aligned")
            maybe_compressed_code_post_header = compress_code(uncompressed_code[hdr_len:])
            if maybe_compressed_code_post_header is not None:
                ret = bytearray(uncompressed_code[:hdr_len] + maybe_compressed_code_post_header)
                compressed_end = len(ret) + loadaddress
        if ret is None:
            ret = bytearray(uncompressed_code)

        setattr(self, dp + "autoload_sections", (au_secs_start, au_secs_end))
        setattr(self, dp + "autoload_start", au_start)
        setattr(self, dp + "compressed_end", compressed_end)

        return bytes(ret) + rem

    def write_start_info(self, code: bytes, loadaddress: int, entrypoint: Optional[int] = None) -> bytes:
        """
        Write the start info into the given code.

        :param code: The code within which to write the start parameters.
        :param loadaddress: The address at which the code is loaded.
        :param entrypoint: The entrypoint at which the code is loaded. This is only used for DS code which has the no compression version of the structure.
        :return: The modified code.
        :raises ValueError: If the start parameters structure can not be found within the code,
                            or if the code was compressed but the ``compressed_data_end`` field
                            is not in the structure.
        """
        code_start_info_idx = code.find(START_INFO_SIGNATURE_DS)
        code_rw = bytearray(code)
        if code_start_info_idx == -1:
            # assuming now that this isn't compressed code, and is in an old (pre-DSi) game.
            # try to find start info by other means...
            if self.compressed_end is not None:
                raise ValueError("code is compressed, but the code does not support compression")
            if entrypoint is not None:
                code_start_info_idx = try_find_start_info_no_signature(code, loadaddress, entrypoint, False)
                if code_start_info_idx is None:
                    raise ValueError("failed to find code start info")
                compressed_end = None
            else:
                raise ValueError("failed to find code start info")
        else:
            compressed_end = self.compressed_end or 0
            code_start_info_idx -= 28

        if compressed_end is None:
            pack_into("<5I", code_rw, code_start_info_idx, *self.autoload_sections, self.autoload_start, *self.bss_bounds)
        else:
            pack_into("<6I", code_rw, code_start_info_idx, *self.autoload_sections, self.autoload_start, *self.bss_bounds, compressed_end)

        codei_start_info_idx = code.find(START_INFO_SIGNATURE_DSI)
        if codei_start_info_idx == -1:
            if self.dsi_autoload_start is not None or self.dsi_compressed_end is not None or self.dsi_autoload_sections is not None:
                raise ValueError("DSi code has been packed, but there is no DSi start info structure")
        else:
            if self.dsi_autoload_sections is None or self.dsi_autoload_start is None:
                raise ValueError("DSi structure is present in code but DSi autoload info addresses are None")
            pack_into("<4I", code_rw, codei_start_info_idx - 16, *self.dsi_autoload_sections, self.dsi_autoload_start, self.dsi_compressed_end or 0)

        return bytes(code_rw)

def try_find_start_info_no_signature(code: bytes, loadaddress: int, entrypoint: int, check_autoload: bool = False) -> Optional[int]:
    """
    This function looks through the C runtime trying to find the start
    parameters structure, which contains autoload and bss information.
    It does so by locating addresses which are read to,
    and then read at offsets 0, 4, 8, 12, 16, 20.
    After finding these candidates, it narrows down to those which
    satisfy the expected properties of the structure. If a single
    best candidate can be found, it is returned.

    This function should only be called on (old) Nintendo DS ROMs. On Nintendo DSi ROMs
    and newer (relatively speaking) Nintendo DS ROMs, a signature is present to help locate
    the start info structure(s). Furthermore, the autoload code was updated at some point
    in the DSi's lifespan. This function will not work properly on this newer Autoload
    structure.
    """
    # look for candidates that are obviously read at some of the offets 0, 4, 8, 12, 16, 20
    # check that it satisfies obvious expectations about the start info structure

    # we are expecting ldr into a register and then immediately load into other registers
    # from offsets. e.g.
    # ldr r0, addr
    # ldr r1, [r0, #0]
    # ldr r2, [r0, #4]
    # expect ARM (not thumb)

    # returns: (X, Y, off) if ins is
    # ldr rX, [rY, #off]
    # otherwise returns None.
    # PC is Y=15, in which case it is offset from instruction after address
    def get_read_offset(ins: bytes) -> Optional[Tuple[int, int, int]]:
        # unconditional memory operation with immediate offset/pre-index
        if ins[3] != 0b11100101:
            return None
        # word access, load, offset.
        if ins[2] & 0b01110000 != 0b00010000:
            return None
        sgn = 1 if ins[2] & 0b10000000 != 0 else -1
        off = sgn * (ins[0] | ((ins[1] & 0b1111) << 8))
        rn = ins[2] & 0b1111
        if rn == 15:
            off += 4
        rd = ins[1] >> 4
        return (rd, rn, off)

    lc_aligned = (len(code) + 3) & ~3

    candidates = defaultdict(set)

    cur = start = entrypoint - loadaddress
    # crt will be at most 0x4000 bytes (guess).
    while cur - start < 0x4000 and cur + 4 <= lc_aligned:
        ins = code[cur:cur + 4]
        cur += 4
        ro = get_read_offset(ins)
        if ro is None:
            continue
        rd, rn, off = ro
        if rd >= 8 or rn != 15:
            continue
        addr, = unpack_from("<I", code, cur + off)
        if (addr & 3) != 0 or addr - loadaddress > 0x4000 or addr - loadaddress < 0:
            continue
        read_offs = set()
        while cur + 4 <= lc_aligned:
            ins = code[cur:cur + 4]
            ro = get_read_offset(ins)
            if ro is None:
                cur += 4
                break
            if ro[0] != rd and ro[1] == rd:
                cur += 4
                if ro[2] in {0, 4, 8, 12, 16, 20}:
                    read_offs.add(ro[2])
                elif ro[2] > 32 or ro[2] < 0:
                    # invalidate candidate for offset out of range
                    read_offs = set()
                    if addr in candidates:
                        del candidates[addr]
                    break
            else:
                break
        if len(read_offs) > 0:
            candidates[addr] |= read_offs

    valid_candidates = []
    for candidate in candidates:
        if candidate - loadaddress + 20 > lc_aligned:
            continue
        au_secs_start, au_secs_end, au_start = \
            unpack_from("<3I", code, candidate - loadaddress)
        if au_start < loadaddress or au_start & 3 != 0:
            continue
        if au_secs_end & 3 != 0 or (au_secs_end - au_secs_start) % 12 != 0:
            continue
        if check_autoload:
            for i in range(au_secs_start, au_secs_end, 12):
                if i - loadaddress + 12 > lc_aligned:
                    break
                destination, size, bss_size = unpack_from("<3I", code, i - loadaddress)
                if destination & 3 != 0 or size & 3 != 0 or bss_size & 3 != 0:
                    break
                au_start += size
            else:
                if au_start - loadaddress <= lc_aligned:
                    valid_candidates.append(candidate)
        else:
            valid_candidates.append(candidate)
    srt_valid = sorted(valid_candidates, key=lambda c : len(candidates[c]))
    if len(srt_valid) == 0 or len(srt_valid) >= 2 and len(candidates[srt_valid[0]]) == len(candidates[srt_valid[1]]):
        return None
    return srt_valid[0] - loadaddress

def get_start_info_offset(code: bytes, loadaddress: int, entrypoint: Optional[int] = None) -> Optional[int]:
    code_start_info_idx = code.find(START_INFO_SIGNATURE_DS)
    if code_start_info_idx != -1:
        return code_start_info_idx - 28
    # assuming now that this isn't compressed code, and is in an old (pre-DSi) game.
    # try to find start info by other means...
    if entrypoint is not None:
        return try_find_start_info_no_signature(code, loadaddress, entrypoint, True)

__all__: list[str] = ['AutoloadSectionInfo', 'CodeStartParams']
