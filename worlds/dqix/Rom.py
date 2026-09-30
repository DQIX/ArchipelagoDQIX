from typing import TYPE_CHECKING

from Files import APProcedurePatch, APTokenMixin, APTokenTypes
from settings import get_settings

if TYPE_CHECKING:
    from dqix import DragonQuestIX

DQIX_HASH: str = "3a63438fff7db282fa3133e8fd020e85"


class DQIXProcedurePatch(APProcedurePatch, APTokenMixin):
    game = "Dragon Quest IX"
    hash = DQIX_HASH
    patch_file_ending = ".apdqix"
    result_file_ending = ".nds"

    procedure = [
        ("apply_tokens", ["token_data.bin"])
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()


def get_base_rom_bytes() -> bytes:
    with open(get_settings().dqix_settings.rom_file, "rb") as infile:
        base_rom_bytes = bytes(infile.read())

    return base_rom_bytes


def patch_rom(world: "DragonQuestIX", patch: DQIXProcedurePatch) -> None:
    patch.write_token(APTokenTypes.WRITE, 0x0, b"APDQIX\x00\x00\x00\x00\x00\x00")

    patch.write_file("token_data.bin", patch.get_token_binary())
