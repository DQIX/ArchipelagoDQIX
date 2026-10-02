from typing import TYPE_CHECKING

from ..apnds.rom import Rom

if TYPE_CHECKING:
    from .. import DQIXPatch


def patch(rom: Rom, world_package: str, patch_instance: "DQIXPatch", files_dump: dict[str, bytes | bytearray]) -> None:
    rom.to_bytes()
    shop_file = rom.files["/data/bin/menu/shopdata1.bin"]
    print(shop_file)
