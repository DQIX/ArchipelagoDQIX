import json
import logging
import zipfile
from collections import Counter
from random import Random
from typing import TYPE_CHECKING, Dict, List

from Options import OptionError
from ..Options import RandomizeShops
from ..game.ShopData import ShopData, ShopConfig
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


def get_random_valid_item(item_pool: Dict[int, int], existing_items: List[int], world_random: Random) -> int:
    allowed_items = {k: v for k, v in item_pool.items() if k not in existing_items}
    if len(allowed_items) == 0:
        raise Exception("No allowed items remain")
    return world_random.sample(list(allowed_items.keys()), k=1)[0]


def randomize_shops(patch_instance: "DQIXPatch", randomization_type: int) -> Dict[int, Dict]:
    # logging.warning("ITEMS_BY_SHOP_TYPE")
    # for shop_type, items in ShopData.ITEMS_BY_SHOP_TYPE.items():
        # logging.warning(str(shop_type) + ": {" + ", ".join(["{}: {}".format(a, b) for a, b in {k: v for k, v in sorted(ShopData.ITEMS_BY_SHOP_TYPE[shop_type].items(), key=lambda item: item[1], reverse=True)}.items()]) + "}")

    # logging.warning("ITEMS_BY_REGION")
    # for region, items in ShopData.ITEMS_BY_REGION.items():
        # logging.warning(str(region) + ": {" + ", ".join(["{}: {}".format(a, b) for a, b in {k: v for k, v in sorted(ShopData.ITEMS_BY_REGION[region].items(), key=lambda item: item[1], reverse=True)}.items()]) + "}")

    # logging.warning("ITEMS_BY_REGION_AND_SHOP_TYPE")
    # for region, data in ShopData.ITEMS_BY_REGION_AND_SHOP_TYPE.items():
    #     logging.warning("REGION: "+ str(region))
    #     for shop_type, items in data.items():
    #         logging.warning(str(shop_type) + ": {" + ", ".join(["{}: {}".format(a, b) for a, b in {k: v for k, v in sorted(ShopData.ITEMS_BY_REGION_AND_SHOP_TYPE[region][shop_type].items(), key=lambda item: item[1], reverse=True)}.items()]) + "}")

    # logging.warning("ALL_ITEMS")
    # logging.warning([a for a in {k: v for k, v in sorted(ShopData.ALL_ITEMS.items(), key=lambda item: item[1], reverse=True)}.items()])

    if randomization_type == RandomizeShops.option_none:
        raise OptionError("This should not be possible - Trying to randomize shops when randomization_type is \"None\"")
    shops: Dict[int, Dict[str, List[int] | int]] = {}
    world_random = patch_instance.world.random

    if randomization_type == RandomizeShops.option_same_category:
        items_by_shop_type: Dict[int, Dict[int, int]] = ShopData.ITEMS_BY_SHOP_TYPE
        shops_by_type: Dict[int, Dict[int, ShopConfig]] = {
            ShopData.SHOP_TYPE_WEAPONS: {},
            ShopData.SHOP_TYPE_ARMOR: {},
            ShopData.SHOP_TYPE_COMMON_ITEMS: {},
            ShopData.SHOP_TYPE_ITEMS_AND_EQUIPMENT: {},
            ShopData.SHOP_TYPE_ALL_EQUIPMENT: {},
            ShopData.SHOP_TYPE_MIXED: {}
        }
        for shop_id, shop in ShopData.SHOPS_WITH_DATA.items():
            shop.items = []
            shops_by_type[shop.shop_type][shop_id] = shop

        for shop_type, shops_with_type in shops_by_type.items():
            all_items: Dict[int, int] = items_by_shop_type[shop_type]
            unfilled_shops: List[int] = [u[0] for u in sorted(shops_with_type.items(), key=lambda s: s[1].item_count, reverse=True)]
            shuffled_shops: Dict[int, ShopConfig] = {}
            for shop_id, shop in shops_with_type.items():
                shop.items = []
                shuffled_shops[shop_id] = shop
            # world_random.shuffle(unfilled_shops)

            while all_items and unfilled_shops:
                force_filled_shop = False

                out_of_stock: List[int] = []
                for item, amount in sorted(all_items.items(), key=lambda single_item: single_item[1], reverse=True):
                    if amount >= len(unfilled_shops):
                        if amount > len(unfilled_shops):
                            # logging.warning("{} shops left to place {} copies of item {}".format(len(unfilled_shops), amount, item))
                            raise Exception("{} shops left to place {} copies of item {}".format(len(unfilled_shops), amount, item))
                        # Item needs to be force-filled into all remaining shops
                        force_filled_shop = True
                        for shop_id in unfilled_shops:
                            shuffled_shops[shop_id].items.append(item)
                            if len(shuffled_shops[shop_id].items) == shuffled_shops[shop_id].item_count:
                                unfilled_shops.remove(shop_id)
                        out_of_stock.append(item)
                for item in out_of_stock:
                    all_items.pop(item)
                if force_filled_shop:
                    continue

                # Force fills are done, now fill randomly
                shop_to_fill = unfilled_shops.pop()
                item_fill_count = shops_with_type[shop_to_fill].item_count - len(shuffled_shops[shop_to_fill].items)

                for i in range(item_fill_count):
                    new_item = get_random_valid_item(all_items, shuffled_shops[shop_to_fill].items, world_random)
                    if new_item in shuffled_shops[shop_to_fill].items:
                        logging.warning("Trying to add duplicate item to Shop {}: {}".format(shop_to_fill, new_item))
                    all_items[new_item] -= 1
                    if all_items[new_item] == 0:
                        all_items.pop(new_item)
                    shuffled_shops[shop_to_fill].items.append(new_item)
            if all_items:
                logging.warning("Still items left after filled all shops - something went wrong!")
                logging.warning("Remaining items in pool: " + str(all_items))
            for shop_id, shop in shuffled_shops.items():
                shops[shop_id] = {"items": shop.items, "shop_type": shop.shop_type}

        # for shop_id, shop in ShopData.SHOPS_WITH_DATA.items():
        #     logging.warning("---------- Handling data for Shop {} - Type: {} - Item Count: {} ----------".format(shop_id, shop.shop_type, shop.item_count))
        #     remaining_items_per_shop_type = copy.deepcopy(items_by_shop_type[shop.shop_type])
        #     items = get_required_items_for_count(remaining_items_per_shop_type, shops_by_type[shop.shop_type])
        #     for item in items:
        #         remaining_items_per_shop_type.remove(item)
        #     item_count = len(items)
        #     if item_count > 0:
        #         logging.warning("Item Pool with {} items already selected / added: {}".format(item_count, str(Counter(remaining_items_per_shop_type))))
        #     while item_count < shop.item_count:
        #         # If sorting out required items, this should never return an empty sequence
        #         possible_items = [item for item in remaining_items_per_shop_type if item not in items]
        #         item = world_random.choice(possible_items)
        #         items.append(item)
        #         item_count += 1
        #         logging.warning("Added item to shop: " + str(item))
        #         remaining_items_per_shop_type.remove(item)
        #
        #     items_by_shop_type[shop.shop_type] = remaining_items_per_shop_type
        #     shops_by_type[shop.shop_type] -= 1
        #     shops[shop_id] = {"items": items, "shop_type": shop.shop_type}
        #     logging.warning("---------- Done for Shop {} ----------".format(shop_id))

    # elif randomization_type == RandomizeShops.option_same_region:
    #     items_by_region = ShopData.get_items_grouped_by_region()
    #
    #     for shop_id, shop in ShopData.SHOPS_WITH_DATA.items():
    #         remaining_items_per_shop_type = items_by_region[shop.region]
    #         items = world_random.sample(sorted(remaining_items_per_shop_type), shop.item_count)
    #         for item in items:
    #             remaining_items_per_shop_type[item] -= 1
    #             if remaining_items_per_shop_type[item] == 0:
    #                 remaining_items_per_shop_type.pop(item)
    #         items_by_region[shop.region] = remaining_items_per_shop_type
    #         shops[shop_id] = {"items": items, "shop_type": shop.shop_type}
    # elif randomization_type == RandomizeShops.option_same_category_and_region:
    #     items_by_region_and_shop_type = ShopData.get_items_grouped_by_region_and_shop_type()
    #
    #     for shop_id, shop in ShopData.SHOPS_WITH_DATA.items():
    #         remaining_items_per_shop_type = items_by_region_and_shop_type[shop.region][shop.shop_type]
    #         items = world_random.sample(sorted(remaining_items_per_shop_type), shop.item_count)
    #         for item in items:
    #             remaining_items_per_shop_type[item] -= 1
    #             if remaining_items_per_shop_type[item] == 0:
    #                 remaining_items_per_shop_type.pop(item)
    #         items_by_region_and_shop_type[shop.region][shop.shop_type] = remaining_items_per_shop_type
    #         shops[shop_id] = {"items": items, "shop_type": shop.shop_type}
    # elif randomization_type == RandomizeShops.option_true_random:
    #     all_items = ShopData.get_ungrouped_items()
    #
    #     for shop_id, shop in ShopData.SHOPS_WITH_DATA.items():
    #         remaining_items_per_shop_type = all_items[shop.shop_type]
    #         items = world_random.sample(sorted(remaining_items_per_shop_type), shop.item_count)
    #         for item in items:
    #             remaining_items_per_shop_type[item] -= 1
    #             if remaining_items_per_shop_type[item] == 0:
    #                 remaining_items_per_shop_type.pop(item)
    #         all_items[shop.shop_type] = remaining_items_per_shop_type
    #         shops[shop_id] = {"items": items, "shop_type": shop.shop_type}

    return shops
