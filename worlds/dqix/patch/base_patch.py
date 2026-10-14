from typing import TYPE_CHECKING

from game.Shop import ShopContainer
from ..apnds.rom import Rom

if TYPE_CHECKING:
    from .. import DQIXPatch


def patch(rom: Rom, world_package: str, patch_instance: "DQIXPatch", files_dump: dict[str, bytes | bytearray]) -> None:
    shop_data = bytearray(rom.files["/data/bin/menu/shopdata1.bin"])

    shop_container = ShopContainer.create_from_bytes(shop_data)

    rom.files["/data/bin/menu/shopdata1.bin"] = shop_container.to_bytes()
