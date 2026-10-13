from typing import TYPE_CHECKING

from game.Shop import ShopContainer
from ..apnds.rom import Rom

if TYPE_CHECKING:
    from .. import DQIXPatch


def patch(rom: Rom, world_package: str, patch_instance: "DQIXPatch", files_dump: dict[str, bytes | bytearray]) -> None:
    rom.to_bytes()
    shop_data = bytearray(rom.files["/data/bin/menu/shopdata1.bin"])

    shops = ShopContainer.create_from_bytes(shop_data)

    # Chronocrystal replaced with Moonwort Bulb
    shop_data[0xd84:0xd86] = b"\xF7\x55"
    rom.files["/data/bin/menu/shopdata1.bin"] = bytes(shop_data)
    print(shop_data)
