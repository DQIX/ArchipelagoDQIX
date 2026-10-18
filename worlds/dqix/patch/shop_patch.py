import copy
import json
import logging
import zipfile
from collections import Counter
from typing import TYPE_CHECKING, Dict, List

from Options import OptionError
from ..Options import RandomizeShops
from ..game.ShopData import ShopData
from ..game.ShopContainer import ShopContainer
from ..apnds.rom import Rom

if TYPE_CHECKING:
    from .. import DQIXPatch


def write_patch(patch_instance: "DQIXPatch", opened_zipfile: zipfile.ZipFile) -> None:
    opened_zipfile.writestr("shop_data.json", json.dumps(randomize_shops(patch_instance, patch_instance.world.options.randomize_shops.value)))


def patch(rom: Rom, patch_instance: "DQIXPatch") -> None:
    shop_data = bytearray(rom.files["/data/bin/menu/shopdata1.bin"])

    shop_container = ShopContainer.create_from_bytes(shop_data)

    shop_container.apply_new_shop_data(patch_instance.get_file("shop_data.json"))

    rom.files["/data/bin/menu/shopdata1.bin"] = shop_container.to_bytes()


def get_required_items_for_count(remaining_items: list[int], cnt: int) -> List[int]:
    required_items = []
    counter = Counter(remaining_items)

    for item, amount in counter.items():
        # If as many of one item remain as there are shops, one has to be added to the current shop
        if amount == cnt:
            required_items.append(item)
            logging.warning("Found required item needed to satisfy the generator: {} of item {} present, {} shops remaining".format(amount, item, cnt))
        elif amount > cnt:
            logging.error("Something went really wrong, we have {} items to be placed with {} shops remaining".format(amount, cnt))
    return required_items


def randomize_shops(patch_instance: "DQIXPatch", randomization_type: int) -> Dict[int, Dict]:
    if randomization_type == RandomizeShops.option_none:
        raise OptionError("This should not be possible - Trying to randomize shops when randomization_type is \"None\"")
    shops: Dict[int, Dict[str, List[int] | int]] = {}
    world_random = patch_instance.world.random

    shop_data = ShopData()
    shop_data.init()

    if randomization_type == RandomizeShops.option_same_category:
        items_by_shop_type = shop_data.get_items_grouped_by_shop_type()
        remaining_shops: Dict[int, int] = {
            ShopData.TYPE_WEAPONS: 0,
            ShopData.TYPE_ARMOR: 0,
            ShopData.TYPE_COMMON_ITEMS: 0,
            ShopData.TYPE_ITEMS_AND_EQUIPMENT: 0,
            ShopData.TYPE_ALL_EQUIPMENT: 0,
            ShopData.TYPE_MIXED: 0
        }
        for shop in shop_data.SHOPS_WITH_DATA.values():
            remaining_shops[shop.shop_type] += 1

        for shop_id, shop in shop_data.SHOPS_WITH_DATA.items():
            logging.warning("---------- Handling data for Shop {} - Type: {} - Item Count: {} ----------".format(shop_id, shop.shop_type, shop.item_count))
            remaining_items_per_shop_type = copy.deepcopy(items_by_shop_type[shop.shop_type])
            items = get_required_items_for_count(remaining_items_per_shop_type, remaining_shops[shop.shop_type])
            for item in items:
                remaining_items_per_shop_type.remove(item)
            item_count = len(items)
            if item_count > 0:
                logging.warning("Item Pool with {} items already selected / added: {}".format(item_count, str(Counter(remaining_items_per_shop_type))))
            while item_count < shop.item_count:
                # If sorting out required items, this should never return an empty sequence
                possible_items = [item for item in remaining_items_per_shop_type if item not in items]
                item = world_random.choice(possible_items)
                items.append(item)
                item_count += 1
                logging.warning("Added item to shop: " + str(item))
                remaining_items_per_shop_type.remove(item)

            items_by_shop_type[shop.shop_type] = remaining_items_per_shop_type
            remaining_shops[shop.shop_type] -= 1
            shops[shop_id] = {"items": items, "shop_type": shop.shop_type}
            logging.warning("---------- Done for Shop {} ----------".format(shop_id))

    # elif randomization_type == RandomizeShops.option_same_region:
    #     items_by_region = shop_data.get_items_grouped_by_region()
    #
    #     for shop_id, shop in shop_data.SHOPS_WITH_DATA.items():
    #         remaining_items_per_shop_type = items_by_region[shop.region]
    #         items = world_random.sample(sorted(remaining_items_per_shop_type), shop.item_count)
    #         for item in items:
    #             remaining_items_per_shop_type[item] -= 1
    #             if remaining_items_per_shop_type[item] == 0:
    #                 remaining_items_per_shop_type.pop(item)
    #         items_by_region[shop.region] = remaining_items_per_shop_type
    #         shops[shop_id] = {"items": items, "shop_type": shop.shop_type}
    # elif randomization_type == RandomizeShops.option_same_category_and_region:
    #     items_by_region_and_shop_type = shop_data.get_items_grouped_by_region_and_shop_type()
    #
    #     for shop_id, shop in shop_data.SHOPS_WITH_DATA.items():
    #         remaining_items_per_shop_type = items_by_region_and_shop_type[shop.region][shop.shop_type]
    #         items = world_random.sample(sorted(remaining_items_per_shop_type), shop.item_count)
    #         for item in items:
    #             remaining_items_per_shop_type[item] -= 1
    #             if remaining_items_per_shop_type[item] == 0:
    #                 remaining_items_per_shop_type.pop(item)
    #         items_by_region_and_shop_type[shop.region][shop.shop_type] = remaining_items_per_shop_type
    #         shops[shop_id] = {"items": items, "shop_type": shop.shop_type}
    # elif randomization_type == RandomizeShops.option_true_random:
    #     all_items = shop_data.get_ungrouped_items()
    #
    #     for shop_id, shop in shop_data.SHOPS_WITH_DATA.items():
    #         remaining_items_per_shop_type = all_items[shop.shop_type]
    #         items = world_random.sample(sorted(remaining_items_per_shop_type), shop.item_count)
    #         for item in items:
    #             remaining_items_per_shop_type[item] -= 1
    #             if remaining_items_per_shop_type[item] == 0:
    #                 remaining_items_per_shop_type.pop(item)
    #         all_items[shop.shop_type] = remaining_items_per_shop_type
    #         shops[shop_id] = {"items": items, "shop_type": shop.shop_type}

    return shops
