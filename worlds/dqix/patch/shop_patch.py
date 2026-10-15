from random import shuffle
from typing import TYPE_CHECKING, List, Dict

from ..game.ShopData import ShopData
from ..game.ShopContainer import ShopContainer
from ..apnds.rom import Rom

if TYPE_CHECKING:
    from .. import DQIXPatch


def patch(rom: Rom, world_package: str, patch_instance: "DQIXPatch", files_dump: dict[str, bytes | bytearray]) -> None:
    shop_data = bytearray(rom.files["/data/bin/menu/shopdata1.bin"])

    shop_container = ShopContainer.create_from_bytes(shop_data)

    shop_container = randomize_shops(shop_container)

    rom.files["/data/bin/menu/shopdata1.bin"] = shop_container.to_bytes()


def randomize_shops(container: ShopContainer) -> ShopContainer:
    modified_container = ShopContainer()
    modified_container.start_bytes = container.start_bytes
    modified_container.end_bytes = container.end_bytes

    items_by_shop_type: Dict[int, List[int]] = {
        ShopData.TYPE_WEAPONS: [],
        ShopData.TYPE_ARMOR: [],
        ShopData.TYPE_COMMON_ITEMS: [],
        ShopData.TYPE_ITEMS_AND_EQUIPMENT: [],
        ShopData.TYPE_ALL_EQUIPMENT: [],
        ShopData.TYPE_MIXED: []
    }
    for shop in container.shops:
        for item in shop.items:
            if item > 0:
                items_by_shop_type[shop.shop_type].append(item)

    for i in range(len(items_by_shop_type)):
        shuffle(items_by_shop_type[i])

    for shop in container.shops:
        shop.items = items_by_shop_type[shop.shop_type][:ShopData.ITEM_COUNT_BY_SHOP[shop.identifier]]
        del items_by_shop_type[shop.shop_type][:ShopData.ITEM_COUNT_BY_SHOP[shop.identifier]]
        modified_container.shops.append(shop)

    return modified_container
