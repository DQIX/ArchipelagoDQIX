import json
import zipfile
from typing import TYPE_CHECKING, Dict

from ..game.ShopData import ShopData, ShopConfig
from ..game.ShopContainer import ShopContainer
from ..apnds.rom import Rom

if TYPE_CHECKING:
    from .. import DQIXPatch


def write_patch(patch_instance: "DQIXPatch", opened_zipfile: zipfile.ZipFile) -> None:
    opened_zipfile.writestr("shop_data.json", json.dumps(randomize_shops(patch_instance)))


def patch(rom: Rom, world_package: str, patch_instance: "DQIXPatch", files_dump: dict[str, bytes | bytearray]) -> None:
    shop_data = bytearray(rom.files["/data/bin/menu/shopdata1.bin"])

    shop_container = ShopContainer.create_from_bytes(shop_data)

    shop_container.apply_new_shop_data(patch_instance.get_file("shop_data.json"))

    rom.files["/data/bin/menu/shopdata1.bin"] = shop_container.to_bytes()


def randomize_shops(patch_instance: "DQIXPatch") -> Dict[int, Dict]:
    shops = {}
    items_by_shop_type = ShopData.get_items_by_shop_type()
    for shop_type in items_by_shop_type.keys():
        patch_instance.world.random.shuffle(items_by_shop_type[shop_type])

    for shop_id, shop in ShopData.SHOPS_WITH_DATA.items():
        items = items_by_shop_type[shop.shop_type][:shop.item_count]
        del items_by_shop_type[shop.shop_type][:shop.item_count]
        shops[shop_id] = ShopConfig(items, shop.shop_type, shop.item_count)._asdict()

    return shops
