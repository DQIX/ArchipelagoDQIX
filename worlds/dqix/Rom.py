import hashlib
import os
from typing import TYPE_CHECKING

import Utils
from Files import APProcedurePatch, APTokenMixin, APTokenTypes

if TYPE_CHECKING:
    from dqix import DragonQuestIX

DQIXHASH: str = "3a63438fff7db282fa3133e8fd020e85"


class DQIXProcedurePatch(APProcedurePatch, APTokenMixin):
    game = "Dragon Quest IX"
    hash = DQIXHASH
    patch_file_ending = ".apdqix"
    result_file_ending = ".nds"

    procedure = [
        ("apply_tokens", ["token_patch.bin"])
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()


def get_base_rom_bytes(file_name: str = "") -> bytes:
    base_rom_bytes = getattr(get_base_rom_bytes, "base_rom_bytes", None)
    if not base_rom_bytes:
        file_name = get_base_rom_path(file_name)
        base_rom_bytes = bytes(open(file_name, "rb").read())

        basemd5 = hashlib.md5()
        basemd5.update(base_rom_bytes)
        if DQIXHASH != basemd5.hexdigest():
            raise Exception('Supplied Base Rom does not match known MD5 for European release.')
        get_base_rom_bytes.base_rom_bytes = base_rom_bytes
    return base_rom_bytes


def get_base_rom_path(file_name: str = "") -> str:
    if not file_name:
        file_name = DragonQuestIX.settings.rom_file
    if not os.path.exists(file_name):
        file_name = Utils.user_path(file_name)
    return file_name


def patch_rom(world: "DragonQuestIX", patch: DQIXProcedurePatch) -> None:
    patch.write_token(APTokenTypes.WRITE, 0x0, b"APDQIX\x00\x00\x00\x00\x00\x00")

    patch.write_file("token_patch.bin", patch.get_token_binary())
