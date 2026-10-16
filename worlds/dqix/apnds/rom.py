# apnds/rom.py
#
# Copyright (C) 2025-2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

"""
:synopsis: Classes relating to Nintendo DS ROMs, their headers, and overlays.

This package contains code to pack and unpack Nintendo DS and DSi ROMs,
including decrypting DSi MODCRYPT (but not DS secure areas). It also contains structures
for manipulating ROM headers.
"""

from collections.abc import Iterable, Mapping, MutableMapping, MutableSequence, Sequence
from dataclasses import dataclass
from enum import IntEnum
from itertools import chain
from queue import SimpleQueue
from struct import pack, pack_into, unpack_from
from typing import Literal, Optional, Tuple

from .aes import aes_ctr
from .code import get_start_info_offset

BANNER_SIZE_MAP: Mapping[int, int] = {
    1: 0x840,
    2: 0x940,
    3: 0x1240,
    0x103: 0x23C0,
}

ST_MROM = 0x51E
ST_PROM = 0xD7E

TRY_CAPSHIFT_BASE = 0x20000
MAX_CAPSHIFT_PROM = 15
MAX_CAPSHIFT_MROM = 10

class HeaderField(IntEnum):
    """
    :synopsis: The offsets of fields within DS and DSi ROM headers.

    These are the fields of the header, and their corresponding offsets.
    The length of each entry is the difference of its successor's offset with it.
    """
    TITLE = 0x000
    """
    The title of the ROM. This should be null-terminated ASCII.
    """
    SERIAL = 0x00C
    """
    Game code.
    """
    MAKER = 0x010
    """
    Maker code.
    """
    UNITCODE = 0x012
    """
    Unit code. 0 for DS, 2 for DS or DSi, 3 for DSi.
    """
    ENCRYPTION_SEED_SELECT = 0x013
    """
    Encryption seed select.
    """
    CHIPCAPACITY = 0x014
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    RESERVED_015 = 0x015
    """
    Reserved.
    """
    DSI_FLAGS = 0x01C
    """
    The second bit is cleared when converting the ROM to bytes.
    """
    NDS_REGION_DSI_PERMIT_JUMP = 0x01D
    """
    Permit jump?
    """
    REVISION = 0x01E
    """
    Game revision.
    """
    ARM9_ROMOFFSET = 0x020
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    ARM9_ENTRYPOINT = 0x024
    """
    Entrypoint of the ARM9 processor.
    """
    ARM9_LOADADDR = 0x028
    """
    Load address of the ARM9 code.
    """
    ARM9_LOADSIZE = 0x02C
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    ARM7_ROMOFFSET = 0x030
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    ARM7_ENTRYPOINT = 0x034
    """
    Entrypoint of the ARM7 processor.
    """
    ARM7_LOADADDR = 0x038
    """
    Load address of the ARM7 code.
    """
    ARM7_LOADSIZE = 0x03C
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    FNTB_ROMOFFSET = 0x040
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    FNTB_BSIZE = 0x044
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    FATB_ROMOFFSET = 0x048
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    FATB_BSIZE = 0x04C
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    OVT9_ROMOFFSET = 0x050
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    OVT9_BSIZE = 0x054
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    OVT7_ROMOFFSET = 0x058
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    OVT7_BSIZE = 0x05C
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    ROMCTRL_DEC = 0x060
    """
    Port 0x40001A4 setting for normal commands.
    """
    ROMCTRL_ENC = 0x064
    """
    Port 0x40001A4 setting for KEY1 commands.
    """
    BANNER_ROMOFFSET = 0x068
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    SECURECRC = 0x06C
    """
    Secure area CRC.
    """
    SECURE_DELAY = 0x06E
    """
    Secure area delay.
    """
    ARM9_AUTOLOADCB = 0x070
    """
    ARM9 autoload callback address.
    """
    ARM7_AUTOLOADCB = 0x074
    """
    ARM7 autoload callback address.
    """
    SECURE_AREA_DISABLE = 0x078
    """
    Secure area disable.
    """
    ROMSIZE = 0x080
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    HEADERSIZE = 0x084
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    NDS_UNK_DSI_ARM9_PARAMS_TABLE_OFFSET = 0x088
    """
    This is computed and set automatically when converting the ROM to bytes,
    when the unit code is nonzero.
    """
    ARM7_PARAMS_TABLE_OFFSET = 0x08C
    """
    This is computed and set automatically when converting the ROM to bytes,
    when the unit code is nonzero.
    """
    NTR_ROM_REGION_END = 0x090
    """
    This is computed and set automatically when converting the ROM to bytes,
    when the unit code is nonzero.
    """
    TWL_ROM_REGION_START = 0x092
    """
    This is computed and set automatically when converting the ROM to bytes,
    when the unit code is nonzero.
    """
    TWL_ROM_REGION_START_END = 0x094
    """
    For the length of ``TWL_ROM_REGION_START`` to be correctly calculated.
    """
    HEADERCRC = 0x15E
    """
    This is computed and set automatically when converting the ROM to bytes.
    """
    DEBUG_ROM_SOURCE = 0x160
    """
    Debug ROM offset.
    """
    DEBUG_ROM_SIZE = 0x164
    """
    Debug ROM size.
    """
    DEBUG_ROM_DESTINATION = 0x168
    """
    Debug ROM destination.
    """
    UNK_16C = 0x16C
    """
    Unknown.
    """
    ZEROS_170 = 0x170
    """
    Zeros.
    """
    MBK_GLOBAL_1 = 0x180
    """
    Global MBK 1.
    """
    MBK_GLOBAL_2 = 0x184
    """
    Global MBK 2.
    """
    MBK_GLOBAL_3 = 0x188
    """
    Global MBK 3.
    """
    MBK_GLOBAL_4 = 0x18C
    """
    Global MBK 4.
    """
    MBK_GLOBAL_5 = 0x190
    """
    Global MBK 5.
    """
    MBK_ARM9_6 = 0x194
    """
    ARM9 MBK 6.
    """
    MBK_ARM9_7 = 0x198
    """
    ARM9 MBK 7.
    """
    MBK_ARM9_8 = 0x19C
    """
    ARM9 MBK 8.
    """
    MBK_ARM7_6 = 0x1A0
    """
    ARM7 MBK 6.
    """
    MBK_ARM7_7 = 0x1A4
    """
    ARM7 MBK 7.
    """
    MBK_ARM7_8 = 0x1A8
    """
    ARM7 MBK 8.
    """
    MBK_WRAMCNT_SETTING = 0x1AC
    """
    Global WRAMCNT Setting.
    """
    REGION_FLAGS = 0x1B0
    """
    Region flags.
    """
    ACCESS_CONTROL = 0x1B4
    """
    Access control.
    """
    SCFG_EXT7_MASK = 0x1B8
    """
    ARM7 SCFG_EXT7 mask.
    """
    UNK_1BC = 0x1BC
    """
    Unknown.
    """
    APPFLAGS = 0x1BF
    """
    Application flags.
    """
    ARM9I_ROMOFFSET = 0x1C0
    """
    This is computed and set automatically when converting the ROM to bytes,
    when the unit code is nonzero.
    """
    RESERVED_1C4 = 0x1C4
    """
    Reserved.
    """
    ARM9I_LOADADDR = 0x1C8
    """
    RAM load address of the ARM9i.
    """
    ARM9I_LOADSIZE = 0x1CC
    """
    This is computed and set automatically when converting the ROM to bytes,
    when the unit code is nonzero.
    """
    ARM7I_ROMOFFSET = 0x1D0
    """
    This is computed and set automatically when converting the ROM to bytes,
    when the unit code is nonzero.
    """
    UNK_1D4 = 0x1D4
    """
    Unknown.
    """
    ARM7I_LOADADDR = 0x1D8
    """
    RAM load address of the ARM7i.
    """
    ARM7I_LOADSIZE = 0x1DC
    """
    This is computed and set automatically when converting the ROM to bytes,
    when the unit code is nonzero.
    """
    DIGEST_NTR_START = 0x1E0
    """
    Digest NTR region offset.
    """
    DIGEST_NTR_SIZE = 0x1E4
    """
    Digest NTR region size.
    """
    DIGEST_TWL_START = 0x1E8
    """
    Digest TWL region offset.
    """
    DIGEST_TWL_SIZE = 0x1EC
    """
    Digest TWL region size.
    """
    SECTOR_HASHTABLE_START = 0x1F0
    """
    Digest sector hashtable offest.
    """
    SECTOR_HASHTABLE_SIZE = 0x1F4
    """
    Digest sector hashtable size.
    """
    BLOCK_HASHTABLE_START = 0x1F8
    """
    Digest block hashtable offset.
    """
    BLOCK_HASHTABLE_SIZE = 0x1FC
    """
    Digest block hashtable size.
    """
    DIGEST_SECTOR_SIZE = 0x200
    """
    Digest sector size.
    """
    DIGEST_BLOCK_SECTORCOUNT = 0x204
    """
    Digest block sector count.
    """
    BANNER_BSIZE = 0x208
    """
    This is computed and set automatically when converting the ROM to bytes,
    when the unit code is nonzero.
    """
    UNK_20C = 0x20C
    """
    Unknown
    """
    TOTAL_ROMSIZE = 0x210
    """
    This is computed and set automatically when converting the ROM to bytes,
    when the unit code is nonzero.
    """
    UNK_214 = 0x214
    """
    Unknown
    """
    UNK_218 = 0x218
    """
    Unknown
    """
    UNK_21C = 0x21C
    """
    Unknown
    """
    MODCRYPT1_START = 0x220
    """
    This is cleared when converting the ROM to bytes.
    """
    MODCRYPT1_SIZE = 0x224
    """
    This is cleared when converting the ROM to bytes.
    """
    MODCRYPT2_START = 0x228
    """
    This is cleared when converting the ROM to bytes.
    """
    MODCRYPT2_SIZE = 0x22C
    """
    This is cleared when converting the ROM to bytes.
    """
    TITLEID = 0x230
    """
    Title ID.
    """
    PUBLIC_SAV_SIZE = 0x238
    """
    public.sav size.
    """
    PRIVATE_SAV_SIZE = 0x23C
    """
    private.sav size.
    """
    RESERVED_240 = 0x240
    """
    Reserved.
    """
    AGE_RATINGS = 0x2F0
    """
    Age ratings.
    """
    HMAC_ARM9 = 0x300
    """
    ARM9 HMAC.
    """
    HMAC_ARM7 = 0x314
    """
    ARM7 HMAC.
    """
    HMAC_DIGEST_MASTER = 0x328
    """
    Digest Master HMAC.
    """
    HMAC_ICON_TITLE = 0x33C
    """
    Icon/Title HMAC.
    """
    HMAC_ARM9I = 0x350
    """
    ARM9i HMAC.
    """
    HMAC_ARM7I = 0x364
    """
    ARM7i HMAC.
    """
    RESERVED_378 = 0x378
    """
    Reserved.
    """
    RESERVED_38C = 0x38C
    """
    Reserved.
    """
    HMAC_ARM9_WO_SECURE_AREA = 0x3A0
    """
    ARM9 HMAC without secure area.
    """
    RESERVED_3B4 = 0x3B4
    """
    Reserved.
    """
    RESERVED_E00 = 0xE00
    """
    Reserved.
    """
    RSA_SIGNATURE = 0xF80
    """
    RSA signature.
    """
    RESERVED_1000 = 0x1000
    """
    Reserved.
    """
    ENTIRE_HEADER = 0x4000
    """
    This is the size of the entire header.
    """

    def succ(self) -> "HeaderField":
        """
        Given a header field, this returns the subsequent header field.
        For ENTIRE_HEADER, it returns ENTIRE_HEADER.

        :return: The successor of this header field.
        """
        match self:
            case HeaderField.TITLE:
                return HeaderField.SERIAL
            case HeaderField.SERIAL:
                return HeaderField.MAKER
            case HeaderField.MAKER:
                return HeaderField.UNITCODE
            case HeaderField.UNITCODE:
                return HeaderField.ENCRYPTION_SEED_SELECT
            case HeaderField.ENCRYPTION_SEED_SELECT:
                return HeaderField.CHIPCAPACITY
            case HeaderField.CHIPCAPACITY:
                return HeaderField.RESERVED_015
            case HeaderField.RESERVED_015:
                return HeaderField.DSI_FLAGS
            case HeaderField.DSI_FLAGS:
                return HeaderField.NDS_REGION_DSI_PERMIT_JUMP
            case HeaderField.NDS_REGION_DSI_PERMIT_JUMP:
                return HeaderField.REVISION
            case HeaderField.REVISION:
                return HeaderField.ARM9_ROMOFFSET
            case HeaderField.ARM9_ROMOFFSET:
                return HeaderField.ARM9_ENTRYPOINT
            case HeaderField.ARM9_ENTRYPOINT:
                return HeaderField.ARM9_LOADADDR
            case HeaderField.ARM9_LOADADDR:
                return HeaderField.ARM9_LOADSIZE
            case HeaderField.ARM9_LOADSIZE:
                return HeaderField.ARM7_ROMOFFSET
            case HeaderField.ARM7_ROMOFFSET:
                return HeaderField.ARM7_ENTRYPOINT
            case HeaderField.ARM7_ENTRYPOINT:
                return HeaderField.ARM7_LOADADDR
            case HeaderField.ARM7_LOADADDR:
                return HeaderField.ARM7_LOADSIZE
            case HeaderField.ARM7_LOADSIZE:
                return HeaderField.FNTB_ROMOFFSET
            case HeaderField.FNTB_ROMOFFSET:
                return HeaderField.FNTB_BSIZE
            case HeaderField.FNTB_BSIZE:
                return HeaderField.FATB_ROMOFFSET
            case HeaderField.FATB_ROMOFFSET:
                return HeaderField.FATB_BSIZE
            case HeaderField.FATB_BSIZE:
                return HeaderField.OVT9_ROMOFFSET
            case HeaderField.OVT9_ROMOFFSET:
                return HeaderField.OVT9_BSIZE
            case HeaderField.OVT9_BSIZE:
                return HeaderField.OVT7_ROMOFFSET
            case HeaderField.OVT7_ROMOFFSET:
                return HeaderField.OVT7_BSIZE
            case HeaderField.OVT7_BSIZE:
                return HeaderField.ROMCTRL_DEC
            case HeaderField.ROMCTRL_DEC:
                return HeaderField.ROMCTRL_ENC
            case HeaderField.ROMCTRL_ENC:
                return HeaderField.BANNER_ROMOFFSET
            case HeaderField.BANNER_ROMOFFSET:
                return HeaderField.SECURECRC
            case HeaderField.SECURECRC:
                return HeaderField.SECURE_DELAY
            case HeaderField.SECURE_DELAY:
                return HeaderField.ARM9_AUTOLOADCB
            case HeaderField.ARM9_AUTOLOADCB:
                return HeaderField.ARM7_AUTOLOADCB
            case HeaderField.ARM7_AUTOLOADCB:
                return HeaderField.SECURE_AREA_DISABLE
            case HeaderField.SECURE_AREA_DISABLE:
                return HeaderField.ROMSIZE
            case HeaderField.ROMSIZE:
                return HeaderField.HEADERSIZE
            case HeaderField.HEADERSIZE:
                return HeaderField.NDS_UNK_DSI_ARM9_PARAMS_TABLE_OFFSET
            case HeaderField.NDS_UNK_DSI_ARM9_PARAMS_TABLE_OFFSET:
                return HeaderField.ARM7_PARAMS_TABLE_OFFSET
            case HeaderField.ARM7_PARAMS_TABLE_OFFSET:
                return HeaderField.NTR_ROM_REGION_END
            case HeaderField.NTR_ROM_REGION_END:
                return HeaderField.TWL_ROM_REGION_START
            case HeaderField.TWL_ROM_REGION_START:
                return HeaderField.TWL_ROM_REGION_START_END
            case HeaderField.TWL_ROM_REGION_START_END:
                return HeaderField.HEADERCRC
            case HeaderField.HEADERCRC:
                return HeaderField.DEBUG_ROM_SOURCE
            case HeaderField.DEBUG_ROM_SOURCE:
                return HeaderField.DEBUG_ROM_SIZE
            case HeaderField.DEBUG_ROM_SIZE:
                return HeaderField.DEBUG_ROM_DESTINATION
            case HeaderField.DEBUG_ROM_DESTINATION:
                return HeaderField.UNK_16C
            case HeaderField.UNK_16C:
                return HeaderField.ZEROS_170
            case HeaderField.ZEROS_170:
                return HeaderField.MBK_GLOBAL_1
            case HeaderField.MBK_GLOBAL_1:
                return HeaderField.MBK_GLOBAL_2
            case HeaderField.MBK_GLOBAL_2:
                return HeaderField.MBK_GLOBAL_3
            case HeaderField.MBK_GLOBAL_3:
                return HeaderField.MBK_GLOBAL_4
            case HeaderField.MBK_GLOBAL_4:
                return HeaderField.MBK_GLOBAL_5
            case HeaderField.MBK_GLOBAL_5:
                return HeaderField.MBK_ARM9_6
            case HeaderField.MBK_ARM9_6:
                return HeaderField.MBK_ARM9_7
            case HeaderField.MBK_ARM9_7:
                return HeaderField.MBK_ARM9_8
            case HeaderField.MBK_ARM9_8:
                return HeaderField.MBK_ARM7_6
            case HeaderField.MBK_ARM7_6:
                return HeaderField.MBK_ARM7_7
            case HeaderField.MBK_ARM7_7:
                return HeaderField.MBK_ARM7_8
            case HeaderField.MBK_ARM7_8:
                return HeaderField.MBK_WRAMCNT_SETTING
            case HeaderField.MBK_WRAMCNT_SETTING:
                return HeaderField.REGION_FLAGS
            case HeaderField.REGION_FLAGS:
                return HeaderField.ACCESS_CONTROL
            case HeaderField.ACCESS_CONTROL:
                return HeaderField.SCFG_EXT7_MASK
            case HeaderField.SCFG_EXT7_MASK:
                return HeaderField.UNK_1BC
            case HeaderField.UNK_1BC:
                return HeaderField.APPFLAGS
            case HeaderField.APPFLAGS:
                return HeaderField.ARM9I_ROMOFFSET
            case HeaderField.ARM9I_ROMOFFSET:
                return HeaderField.RESERVED_1C4
            case HeaderField.RESERVED_1C4:
                return HeaderField.ARM9I_LOADADDR
            case HeaderField.ARM9I_LOADADDR:
                return HeaderField.ARM9I_LOADSIZE
            case HeaderField.ARM9I_LOADSIZE:
                return HeaderField.ARM7I_ROMOFFSET
            case HeaderField.ARM7I_ROMOFFSET:
                return HeaderField.UNK_1D4
            case HeaderField.UNK_1D4:
                return HeaderField.ARM7I_LOADADDR
            case HeaderField.ARM7I_LOADADDR:
                return HeaderField.ARM7I_LOADSIZE
            case HeaderField.ARM7I_LOADSIZE:
                return HeaderField.DIGEST_NTR_START
            case HeaderField.DIGEST_NTR_START:
                return HeaderField.DIGEST_NTR_SIZE
            case HeaderField.DIGEST_NTR_SIZE:
                return HeaderField.DIGEST_TWL_START
            case HeaderField.DIGEST_TWL_START:
                return HeaderField.DIGEST_TWL_SIZE
            case HeaderField.DIGEST_TWL_SIZE:
                return HeaderField.SECTOR_HASHTABLE_START
            case HeaderField.SECTOR_HASHTABLE_START:
                return HeaderField.SECTOR_HASHTABLE_SIZE
            case HeaderField.SECTOR_HASHTABLE_SIZE:
                return HeaderField.BLOCK_HASHTABLE_START
            case HeaderField.BLOCK_HASHTABLE_START:
                return HeaderField.BLOCK_HASHTABLE_SIZE
            case HeaderField.BLOCK_HASHTABLE_SIZE:
                return HeaderField.DIGEST_SECTOR_SIZE
            case HeaderField.DIGEST_SECTOR_SIZE:
                return HeaderField.DIGEST_BLOCK_SECTORCOUNT
            case HeaderField.DIGEST_BLOCK_SECTORCOUNT:
                return HeaderField.BANNER_BSIZE
            case HeaderField.BANNER_BSIZE:
                return HeaderField.UNK_20C
            case HeaderField.UNK_20C:
                return HeaderField.TOTAL_ROMSIZE
            case HeaderField.TOTAL_ROMSIZE:
                return HeaderField.UNK_214
            case HeaderField.UNK_214:
                return HeaderField.UNK_218
            case HeaderField.UNK_218:
                return HeaderField.UNK_21C
            case HeaderField.UNK_21C:
                return HeaderField.MODCRYPT1_START
            case HeaderField.MODCRYPT1_START:
                return HeaderField.MODCRYPT1_SIZE
            case HeaderField.MODCRYPT1_SIZE:
                return HeaderField.MODCRYPT2_START
            case HeaderField.MODCRYPT2_START:
                return HeaderField.MODCRYPT2_SIZE
            case HeaderField.MODCRYPT2_SIZE:
                return HeaderField.TITLEID
            case HeaderField.TITLEID:
                return HeaderField.PUBLIC_SAV_SIZE
            case HeaderField.PUBLIC_SAV_SIZE:
                return HeaderField.PRIVATE_SAV_SIZE
            case HeaderField.PRIVATE_SAV_SIZE:
                return HeaderField.RESERVED_240
            case HeaderField.RESERVED_240:
                return HeaderField.AGE_RATINGS
            case HeaderField.AGE_RATINGS:
                return HeaderField.HMAC_ARM9
            case HeaderField.HMAC_ARM9:
                return HeaderField.HMAC_ARM7
            case HeaderField.HMAC_ARM7:
                return HeaderField.HMAC_DIGEST_MASTER
            case HeaderField.HMAC_DIGEST_MASTER:
                return HeaderField.HMAC_ICON_TITLE
            case HeaderField.HMAC_ICON_TITLE:
                return HeaderField.HMAC_ARM9I
            case HeaderField.HMAC_ARM9I:
                return HeaderField.HMAC_ARM7I
            case HeaderField.HMAC_ARM7I:
                return HeaderField.RESERVED_378
            case HeaderField.RESERVED_378:
                return HeaderField.RESERVED_38C
            case HeaderField.RESERVED_38C:
                return HeaderField.HMAC_ARM9_WO_SECURE_AREA
            case HeaderField.HMAC_ARM9_WO_SECURE_AREA:
                return HeaderField.RESERVED_3B4
            case HeaderField.RESERVED_3B4:
                return HeaderField.RESERVED_E00
            case HeaderField.RESERVED_E00:
                return HeaderField.RSA_SIGNATURE
            case HeaderField.RSA_SIGNATURE:
                return HeaderField.RESERVED_1000
            case HeaderField.RESERVED_1000:
                return HeaderField.ENTIRE_HEADER
            case HeaderField.ENTIRE_HEADER:
                return HeaderField.ENTIRE_HEADER

    def len(self) -> int:
        """
        This is the length of this header field, computed by `self.succ() - self`.

        :return: The length of this header field.
        """
        if self == HeaderField.ENTIRE_HEADER:
            return self
        else:
            return self.succ() - self

class Header:
    """
    :synopsis: The header of a DS or DSi ROM.

    This is the header of a DS or DSi ROM. Its fields can be accessed using indexing notation:
    ``header[HeaderField.TITLE]`` will return the title, in bytes.
    """
    data: bytearray
    """
    The underlying data of the header.
    """

    def __init__(self, data: bytes):
        """
        Initialize a header with some underlying data.

        :param data: The header data.
        :raises ValueError: If the length of the data is not ``0x4000``.
        """
        if len(data) != HeaderField.ENTIRE_HEADER:
            raise ValueError("header data is of incorrect length (expected 0x4000 bytes)")
        self.data = bytearray(data)

    def __getitem__(self, key: HeaderField) -> bytes:
        """
        Get a field from the header as bytes.

        :param key: The header field to get.
        :return: The header field.
        """
        if key == HeaderField.ENTIRE_HEADER:
            return bytes(self.data)
        else:
            return bytes(self.data[key:key.succ()])
    
    def __setitem__(self, key: HeaderField, value: bytes | int) -> None:
        """
        Set a field from the header from bytes or an integer. If an integer
        is passed, it is interpreted as little endian.

        :param key: The header field to set.
        :param value: The value to set it to.
        """
        if isinstance(value, int):
            value = value.to_bytes(key.len(), 'little')
        if key == HeaderField.ENTIRE_HEADER:
            self.data[:] = value
        else:
            self.data[key:key.succ()] = value

    def get_le(self, key: HeaderField) -> int:
        """
        Get a field from the header as an integer. It is interpreted as little endian.

        :param key: The header field to get.
        :return: The value of the header field, interpreted as a little-endian integer.
        """
        if key == HeaderField.ENTIRE_HEADER:
            return int.from_bytes(self.data, 'little')
        else:
            return int.from_bytes(self[key], 'little')

    def get_rom_region(self, rom: bytes, offset: HeaderField, length: HeaderField) -> bytes:
        """
        Given the entire ROM, the field corresponding to the offset in the ROM, and the
        field corresponding to the binary size in the ROM, return the region in the ROM.

        :param rom: The ROM.
        :param offset: The field containing the ROM offset of the region.
        :param length: The field containing the length of the region.
        :return: The region.
        """
        off = self.get_le(offset)
        return rom[off:off + self.get_le(length)]

def get_files(header: Header, rom: bytes) -> Tuple[MutableSequence[bytes], Sequence[int]]:
    """
    Given a header and ROM, return the sequence of files in the FAT, as bytes,
    along with the order of these files within ROM.
    """
    fatb = header.get_rom_region(rom, HeaderField.FATB_ROMOFFSET, HeaderField.FATB_BSIZE)
    fatb_ints = [int.from_bytes(fatb[i:i + 4], 'little') for i in range(0, len(fatb), 4)]
    files = [rom[fatb_ints[i]:fatb_ints[i + 1]] for i in range(0, len(fatb_ints), 2)]
    order = sorted(range(len(fatb) // 8), key=lambda i : fatb_ints[2 * i])
    return (files, order)

def get_filename_id_map(fntb: bytes) -> MutableMapping[str, int]:
    """
    Given a header and ROM, return a mapping from file paths to file IDs (in the FAT).
    """

    ret = {}
    dir_queue: SimpleQueue[Tuple[int, str]] = SimpleQueue()
    # queue is (dir id, dir path)
    dir_queue.put((0, ''))

    while not dir_queue.empty():
        dir_id, dir_path = dir_queue.get()
        contents_off, file_id = unpack_from("<IH", fntb, 8 * dir_id)

        while fntb[contents_off] != 0:
            is_dir = fntb[contents_off] & 0x80 != 0
            name_len = fntb[contents_off] & 0x7F
            contents_off += 1
            path = f"{dir_path}/{fntb[contents_off:contents_off + name_len].decode('ascii')}"
            contents_off += name_len
            if is_dir:
                dir_id = 0xFFF & int.from_bytes(fntb[contents_off:contents_off + 2], 'little')
                dir_queue.put((dir_id, path))
                contents_off += 2
            else:
                ret[path] = file_id
                file_id += 1

    return ret

@dataclass
class Overlay:
    """
    :synopsis: This is a single overlay.

    .. code-block:: c
       
       struct Overlay {
           u32 id;
           u32 ram_address;
           u32 ram_size;
           u32 bss_size;
           u32 sinit_init;
           u32 sinit_init_end;
           u32 file_id;
           u32 compressed_size:24;
           // first bit is whether it is compressed
           u32 flags:8;
       };
    """
    id: int
    """
    This is the overlay's ID.
    """
    ram_address: int
    """
    This is the RAM address at which the overlay is to be loaded.
    """
    ram_size: int
    """
    This is the RAM size of the overlay when loaded.
    """
    bss_size: int
    """
    BSS size.
    """
    sinit_init: int
    """
    Static init.
    """
    sinit_init_end: int
    """
    Static init end..
    """
    data: bytes
    """
    This is the data of the overlay.
    """
    flags: int
    """
    The overlay's flags.
    """
    compressed_size: int
    """
    The overlay's size when compressed, if it is compressed.
    """

    def table_entry_data(self) -> MutableSequence[int]:
        return [
            self.id,
            self.ram_address,
            self.ram_size,
            self.bss_size,
            self.sinit_init,
            self.sinit_init_end,
            -1,
            (self.flags << 24) | self.compressed_size,
        ]

    def is_compressed(self) -> bool:
        """
        Check if the overlay is compressed.

        :return: If the overlay is compressed.
        """
        return self.flags & 1 != 0

def get_overlays(header: Header, rom: bytes, files: Sequence[bytes], which: Literal["9"] | Literal["7"]) -> MutableSequence[Overlay]:
    """
    Given a header, ROM, and the files in the ROM, return the overlays for either the ARM9 or ARM7 processor.
    """
    table = header.get_rom_region(rom, getattr(HeaderField, f"OVT{which}_ROMOFFSET"), getattr(HeaderField, f"OVT{which}_BSIZE"))

    ret = []

    for off in range(0, len(table), 32):
        id, ram_address, ram_size, bss_size, sinit_init, sinit_init_end, file_id, flags_and_uc_size = unpack_from("<8I", table, off)
        ret.append(Overlay(id, ram_address, ram_size, bss_size, sinit_init, sinit_init_end, files[file_id], flags_and_uc_size >> 24, flags_and_uc_size & 0xFFFFFF))

    return ret

def construct_overlay_table(overlays: Sequence[Overlay], file_id_off: int = 0) -> Tuple[bytes, Sequence[bytes]]:
    """
    Given a sequence of overlays, and a starting file ID, return the overlay table and the sequence of overlays.
    """
    table = bytes()
    data_seq = []
    for ov in overlays:
        file_id = len(data_seq) + file_id_off
        data_seq.append(ov.data)
        table_entry_data = ov.table_entry_data()
        table_entry_data[6] = file_id
        table += pack("<8I", *table_entry_data)
    return (table, data_seq)

def path_key(path: str) -> Tuple:
    """
    The path key is the decomposition of a path `'/a/b/c'` into
    a tuple of its components, `('a', 'b', 'c')`
    """
    return tuple(path.split('/')[1:])

def path_key_to_path(*kwargs: str) -> str:
    """
    This recomposes a path from its path key.
    """
    return "/" + "/".join(kwargs)

def construct_fntb(filenames: Iterable[str], file_id_off: int) -> Tuple[bytes, Mapping[str, int]]:
    """
    Given the filenames in the ROM, and the first file ID for the files, construct the FNT
    and the mapping from filenames to file IDs.
    """
    header = bytes()
    contents = bytes()

    cur_dir = tuple()
    # path key -> dir id, seq of children (name, dir id or None)
    dir_map: MutableMapping[Tuple[str, ...], Tuple[int, MutableSequence[Tuple[str, Optional[int]]]]] = {}
    dir_map[()] = (0xF000, [])

    def path_key_for_sorted(pk: Tuple[str, ...]) -> Tuple[str, ...]:
        return (*pk[:-1], '\0' + pk[-1])

    paths = sorted(map(path_key, filenames), key=path_key_for_sorted)

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
    filename_id_map = {}
    for pk, (_, children) in dir_map.items():
        parent_id = dir_map[pk[:-1]][0] if len(pk) > 0 else len(dir_map)
        header += pack("<I2H", len(contents) + header_len, file_id_off, parent_id)
        for name, id_if_dir in children:
            contents += int.to_bytes(len(name) | (0x00 if id_if_dir is None else 0x80), 1)
            contents += name.encode('ascii')
            if id_if_dir is not None:
                contents += int.to_bytes(id_if_dir, 2, 'little')
            else:
                filename_id_map[path_key_to_path(*pk, name)] = file_id_off
                file_id_off += 1
        contents += b'\0'

    return (header + contents, filename_id_map)

CRC_TABLE: Sequence[int] = [0, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401, 0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400]

def crc16(data: bytes, crc: int) -> int:
    """
    Compute the 16-bit CRC value for some bytes.
    """
    bit = 0

    for i in range(0, len(data), 2):
        x = int.from_bytes(data[i:i + 2], 'little')
        for bit in range(0, 16, 4):
            y = CRC_TABLE[crc & 0xF]
            crc >>= 4
            crc ^= y
            crc ^= CRC_TABLE[(x >> bit) & 0xF]

    return crc

def process_modcrypt(rom: bytes, header: Header) -> bytes:
    dsi_flags = header.get_le(HeaderField.DSI_FLAGS)
    if dsi_flags & 2 == 0:
        return rom

    if dsi_flags & 4 != 0 or header.get_le(HeaderField.APPFLAGS) & 0x80 != 0:
        key = rom[:0x10][::-1]
    else:
        game_code = header[HeaderField.SERIAL]
        key_x = b'Nintendo' + game_code + game_code[::-1]
        key_y = header[HeaderField.HMAC_ARM9I][:0x10]
        key_x_i = int.from_bytes(key_x, 'little')
        key_y_i = int.from_bytes(key_y, 'little')
        pre_rol = ((key_x_i ^ key_y_i) + 0xFFFEFB4E295902582A680F5F1A4F3E79)
        shft = pre_rol << 42
        rol = shft | ((shft >> 128) & ((1 << 42) - 1))
        rol &= (1 << 128) - 1
        key = rol.to_bytes(16)

    iv1 = header[HeaderField.HMAC_ARM9][:0x10][::-1]
    iv2 = header[HeaderField.HMAC_ARM7][:0x10][::-1]

    rom_m = bytearray(rom)

    mc1_start = header.get_le(HeaderField.MODCRYPT1_START)
    if mc1_start != 0:
        mc1_size = header.get_le(HeaderField.MODCRYPT1_SIZE)
        mc1 = rom[mc1_start:mc1_start + mc1_size]
        new_mc1 = aes_ctr(key, iv1, mc1, True)
        rom_m[mc1_start:mc1_start + mc1_size] = new_mc1

    mc2_start = header.get_le(HeaderField.MODCRYPT2_START)
    if mc2_start != 0:
        mc2_size = header.get_le(HeaderField.MODCRYPT2_SIZE)
        mc2 = rom[mc2_start:mc2_start + mc2_size]
        new_mc2 = aes_ctr(key, iv2, mc2)
        rom_m[mc2_start:mc2_start + mc2_size] = new_mc2


    return bytes(rom_m)

@dataclass
class Rom:
    """
    :synopsis: This is the decomposition of a DS ROM into its parts.
    """
    header: Header
    """
    This is the header of the ROM.
    """
    arm9: bytes
    """
    This is the ARM9 code of the ROM.
    """
    arm7: bytes
    """
    This is the ARM7 code of the ROM.
    """
    arm9_overlays: MutableSequence[Overlay]
    """
    These are the ARM9 overlays of the ROM.
    """
    arm7_overlays: MutableSequence[Overlay]
    """
    These are the ARM7 overlays of the ROM.
    """
    arm9i: Optional[bytes]
    """
    This is the ARM9i code of the ROM, if it exists.
    """
    arm7i: Optional[bytes]
    """
    This is the ARM7i code of the ROM, if it exists.
    """
    files: MutableMapping[str, bytes]
    """
    This is the mapping of file paths to files in the ROM.
    """
    file_order: MutableSequence[str]
    """
    This is the physical order the files are located in the ROM, by path.
    """
    banner: bytes
    """
    This is the ROM's banner.
    """
    rom_alignment: int = 0x200
    """
    This is the alignment used starting each block when converting the ROM to bytes.
    It should be a power of two.
    """

    @staticmethod
    def from_bytes(rom: bytes, decrypt_modcrypt: bool = True) -> "Rom":
        """
        Decompose a ROM into its components.

        :param rom: The ROM bytes.
        :param decrypt_modcrypt: If true, then the modcrypt areas are decrypted.
                                 This should really only be set to False if working with a cartridge
                                 that already has the areas decrypted, but whose modcrypt
                                 regions haven't been cleared in the header.
        :return: The unpacked ROM.
        """
        header = Header(rom[:HeaderField.ENTIRE_HEADER])

        if decrypt_modcrypt:
            rom = process_modcrypt(rom, header)

        (file_seq, file_id_order) = get_files(header, rom)
        fntb = header.get_rom_region(rom, HeaderField.FNTB_ROMOFFSET, HeaderField.FNTB_BSIZE)
        filename_id_map = get_filename_id_map(fntb)
        arm9_ovys = get_overlays(header, rom, file_seq, "9")
        arm7_ovys = get_overlays(header, rom, file_seq, "7")
        id_filename_map = {id:name for name, id in filename_id_map.items()}
        file_order = [id_filename_map[id] for id in file_id_order if id in id_filename_map]

        arm9_start = header.get_le(HeaderField.ARM9_ROMOFFSET)
        if arm9_start < 0x8000:
            # we have a secure area
            if rom[0x4000:0x4008] == b'encryObj':
                print("warning: this rom has an indication that it has an encrypted secure area. decryption is not currently implemented by this library")
            elif rom[0x4000:0x4008] != b'\xFF\xDE\xFF\xE7' * 2:
                print("warning: this rom has an indication that it had an encrypted secure area, but the secure area signature does not match that expected of a dump")
        arm9_len = header.get_le(HeaderField.ARM9_LOADSIZE)
        if arm9_start + arm9_len + 12 <= len(rom) and rom[arm9_start + arm9_len:arm9_start + arm9_len + 4] == bytes.fromhex('2106C0DE'):
            arm9_len += 12
        arm9 = rom[arm9_start:arm9_start + arm9_len]

        arm7 = header.get_rom_region(rom, HeaderField.ARM7_ROMOFFSET, HeaderField.ARM7_LOADSIZE)

        banner_off = header.get_le(HeaderField.BANNER_ROMOFFSET)
        banner_version = int.from_bytes(rom[banner_off:banner_off + 2], 'little')
        banner = rom[banner_off:banner_off + BANNER_SIZE_MAP[banner_version]]

        if header.get_le(HeaderField.UNITCODE) != 0:
            if header.get_le(HeaderField.ARM9I_ROMOFFSET) != 0:
                arm9i = header.get_rom_region(rom, HeaderField.ARM9I_ROMOFFSET, HeaderField.ARM9I_LOADSIZE)
            else:
                arm9i = None
            if header.get_le(HeaderField.ARM7I_ROMOFFSET) != 0:
                arm7i = header.get_rom_region(rom, HeaderField.ARM7I_ROMOFFSET, HeaderField.ARM7I_LOADSIZE)
            else:
                arm7i = None
        else:
            arm9i = arm7i = None

        return Rom(
            header,
            arm9,
            arm7,
            arm9_ovys,
            arm7_ovys,
            arm9i,
            arm7i,
            {name:file_seq[id] for name, id in filename_id_map.items()},
            file_order,
            banner
        )

    def to_bytes(self, fill_tail: bool = True, fill_with: bytes = b'\xFF') -> bytes:
        """
        From the components of a ROM, construct the ROM.

        :param fill_tail: Whether to fill the tail of the ROM to the power of 2 size.
        :param fill_with: What to pad the ROM with.
        :return: The packed ROM.
        :raises ValueError: If ``fill_with`` is not of length 1.
        """
        if len(fill_with) != 1:
            raise ValueError(f"fill_with has length greater than 1")

        rom_alignment = self.rom_alignment

        ovt9, ovys9 = construct_overlay_table(self.arm9_overlays)
        ovt7, ovys7 = construct_overlay_table(self.arm7_overlays, len(ovys9))

        fatb = bytearray(b'\0' * (len(ovys9) + len(ovys7) + len(self.files)) * 8)
        fatb_i = 0
        post_header_bytes = bytes()
        header = Header(bytes(self.header.data))

        storage_type: Literal["MROM"] | Literal["PROM"] = "MROM" if header[HeaderField.SECURE_DELAY] == ST_MROM else "PROM"

        def cur_off() -> int:
            return len(post_header_bytes) + HeaderField.ENTIRE_HEADER
        def align_post_header_bytes() -> int:
            nonlocal post_header_bytes
            padding_len = -len(post_header_bytes) & (rom_alignment - 1)
            post_header_bytes += fill_with * padding_len
            return padding_len

        header[HeaderField.ARM9_ROMOFFSET] = cur_off()
        post_header_bytes += self.arm9
        align_post_header_bytes()

        if len(self.arm9) > 12 and self.arm9[-12:-8] == bytes.fromhex('2106C0DE'):
            header[HeaderField.ARM9_LOADSIZE] = len(self.arm9) - 12
        else:
            header[HeaderField.ARM9_LOADSIZE] = len(self.arm9)

        def size_after_padding(size: int) -> int:
            return size + (-size & (rom_alignment - 1))

        def pad_bytes(data: bytes) -> bytes:
            padding = -len(data) & (rom_alignment - 1)
            return data + fill_with * padding

        def write_ovs(which: Literal["9"] | Literal["7"]) -> None:
            nonlocal post_header_bytes
            nonlocal fatb_i

            ovt = ovt9 if which == "9" else ovt7
            header[getattr(HeaderField, f"OVT{which}_ROMOFFSET")] = cur_off() if len(ovt) > 0 else 0
            header[getattr(HeaderField, f"OVT{which}_BSIZE")] = len(ovt)

            post_header_bytes += ovt
            align_post_header_bytes()

            coff = cur_off()
            ovys = ovys9 if which == "9" else ovys7
            for ovy in ovys:
                pack_into("<2I", fatb, fatb_i, coff, coff + len(ovy))
                fatb_i += 8
                coff += size_after_padding(len(ovy))
            post_header_bytes += b''.join(pad_bytes(ovy) for ovy in ovys)

        write_ovs("9")

        header[HeaderField.ARM7_ROMOFFSET] = cur_off()
        post_header_bytes += self.arm7
        align_post_header_bytes()
        header[HeaderField.ARM7_LOADSIZE] = len(self.arm7)
        write_ovs("7")

        files_in_order = frozenset(self.file_order)
        file_order = list(chain(self.file_order, (filename for filename in self.files if filename not in files_in_order)))

        if len(self.files) > 0:
            (fntb, filename_id_map) = construct_fntb(self.files.keys(), len(ovys9) + len(ovys7))

            header[HeaderField.FNTB_ROMOFFSET] = cur_off()
            post_header_bytes += fntb
            align_post_header_bytes()
            header[HeaderField.FNTB_BSIZE] = len(fntb)

            file_off = cur_off() + size_after_padding(len(fatb)) + size_after_padding(len(self.banner))

            for path in file_order:
                file = self.files[path]
                pack_into("<2I", fatb, filename_id_map[path] * 8, file_off, file_off + len(file))
                file_off += size_after_padding(len(file))
        else:
            header[HeaderField.FNTB_ROMOFFSET] = 0
            header[HeaderField.FNTB_BSIZE] = 0

        header[HeaderField.FATB_ROMOFFSET] = cur_off()
        post_header_bytes += fatb
        align_post_header_bytes()
        header[HeaderField.FATB_BSIZE] = len(fatb)

        header[HeaderField.BANNER_ROMOFFSET] = cur_off()
        post_header_bytes += self.banner
        last_padding = align_post_header_bytes()
        header[HeaderField.BANNER_BSIZE] = len(self.banner)

        post_header_bytes += b''.join(pad_bytes(self.files[path]) for path in file_order)

        if len(file_order) > 0:
            last_padding = -len(self.files[file_order[-1]]) & (rom_alignment - 1)

        if last_padding > 0:
            post_header_bytes = post_header_bytes[:-last_padding]
            last_padding = 0

        ntr_rom_size = cur_off()

        has_twl_section = header.get_le(HeaderField.UNITCODE) != 0 \
            and (self.arm9i is not None or self.arm7i is not None)

        if header.get_le(HeaderField.UNITCODE) != 0:
            # twl section should be padded to 0x80000
            post_header_bytes += fill_with * (-len(post_header_bytes) & 0x7FFFF)
            header[HeaderField.NTR_ROM_REGION_END] = header[HeaderField.TWL_ROM_REGION_START] = cur_off() >> 0x13
            sio = get_start_info_offset(self.arm9, header.get_le(HeaderField.ARM9_LOADADDR), header.get_le(HeaderField.ARM9_ENTRYPOINT))
            if sio is not None:
                header[HeaderField.NDS_UNK_DSI_ARM9_PARAMS_TABLE_OFFSET] = sio
            sio = get_start_info_offset(self.arm7, header.get_le(HeaderField.ARM7_LOADADDR), header.get_le(HeaderField.ARM7_ENTRYPOINT))
            if sio is not None:
                header[HeaderField.ARM7_PARAMS_TABLE_OFFSET] = sio

        # we clear the modcrypt areas (assuming that they were decrypted when loading... no need to re-encrypt,
        # and they might have moved... if people complain then I'll implement this again in the future.
        header[HeaderField.DSI_FLAGS] = header.get_le(HeaderField.DSI_FLAGS) & ~2
        for i in [1, 2]:
            for sfx in ["START", "SIZE"]:
                header[getattr(HeaderField, f"MODCRYPT{i}_{sfx}")] = 0

        if has_twl_section:
            align_post_header_bytes()
            if self.arm9i is not None:
                # there is some cryptographic stuff before the arm9i...
                # leave it zero for now
                post_header_bytes += bytes(0x3000)

                header[HeaderField.ARM9I_ROMOFFSET] = cur_off()
                post_header_bytes += self.arm9i
                last_padding = align_post_header_bytes()
                header[HeaderField.ARM9I_LOADSIZE] = len(self.arm9i)
            else:
                header[HeaderField.ARM9I_ROMOFFSET] = header[HeaderField.ARM9I_LOADSIZE] = 0
            if self.arm7i is not None:
                header[HeaderField.ARM7I_ROMOFFSET] = cur_off()
                post_header_bytes += self.arm7i
                last_padding = align_post_header_bytes()
                header[HeaderField.ARM7I_LOADSIZE] = len(self.arm7i)
            else:
                header[HeaderField.ARM7I_ROMOFFSET] = header[HeaderField.ARM7I_LOADSIZE] = 0


        if last_padding > 0:
            post_header_bytes = post_header_bytes[:-last_padding]

        total_rom_size = cur_off()

        trycap = TRY_CAPSHIFT_BASE
        maxshift = MAX_CAPSHIFT_PROM if storage_type == "PROM" else MAX_CAPSHIFT_MROM
        for shift in range(maxshift):
            if total_rom_size < (trycap << shift):
                header[HeaderField.CHIPCAPACITY] = shift
                break
        else:
            shift = maxshift
        if shift == maxshift:
            raise RuntimeError("rom size is too big")

        tailsize = trycap << shift

        header[HeaderField.ROMSIZE] = ntr_rom_size
        if header.get_le(HeaderField.UNITCODE) != 0:
            header[HeaderField.TOTAL_ROMSIZE] = total_rom_size
            header[HeaderField.BANNER_BSIZE] = len(self.banner)
        header[HeaderField.HEADERSIZE] = HeaderField.ENTIRE_HEADER

        header[HeaderField.HEADERCRC] = crc16(bytes(header.data[:HeaderField.HEADERCRC]), 0xFFFF)

        if fill_tail:
            post_header_bytes += fill_with * (tailsize - len(post_header_bytes) - HeaderField.ENTIRE_HEADER)

        return bytes(header.data + post_header_bytes)

__all__: list[str] = ['HeaderField', 'Header', 'Overlay', 'Rom']
