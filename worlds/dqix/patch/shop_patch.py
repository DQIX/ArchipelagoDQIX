import json
import logging
import zipfile
from random import Random
from typing import TYPE_CHECKING, Dict, List

from Options import OptionError
from ..Options import RandomizeShops
from ..apnds.rom import Rom
from ..game.ShopContainer import ShopContainer
from ..game.ShopData import ShopData, ShopConfig

if TYPE_CHECKING:
    from .. import DQIXPatch


def write_patch(patch_instance: "DQIXPatch", opened_zipfile: zipfile.ZipFile) -> None:
    opened_zipfile.writestr("shop_data.json", json.dumps(randomize_shops(patch_instance, patch_instance.world.options.randomize_shops.value)))


def patch(rom: Rom, patch_instance: "DQIXPatch") -> None:
    shop_data = bytearray(rom.files["/data/bin/menu/shopdata1.bin"])

    shop_container = ShopContainer.create_from_bytes(shop_data)

    shop_container.apply_new_shop_data(patch_instance.get_file("shop_data.json"))

    rom.files["/data/bin/menu/shopdata1.bin"] = shop_container.to_bytes()


def get_backup_item(shop_type: int, current_items: List[int], world_random: Random) -> int:
    replacements = []

    # Weapons
    if shop_type in [ShopData.SHOP_TYPE_WEAPONS, ShopData.SHOP_TYPE_ALL, ShopData.SHOP_TYPE_ALL_EQUIPMENT, ShopData.SHOP_TYPE_MIXED]:
        replacements.extend([20015, 20023, 20003, 20515, 20513, 19065, 19064, 19052, 20400, 20496, 20495, 20311, 20301, 20308, 20613, 20812, 20804, 20806, 20115, 20114, 20104, 20209, 19162, 20712, 20912])

    # Armor
    if shop_type in [ShopData.SHOP_TYPE_ARMOR, ShopData.SHOP_TYPE_ALL, ShopData.SHOP_TYPE_ALL_EQUIPMENT]:
        replacements.extend([21294, 21280, 21299, 12805, 12795, 12801, 12418, 13606, 13305, 13521, 13003, 15045, 16263, 17103, 17405])

    # Accessories
    if shop_type in [ShopData.SHOP_TYPE_COMMON_ITEMS, ShopData.SHOP_TYPE_ALL, ShopData.SHOP_TYPE_MIXED]:
        replacements.extend([18014, 18020, 18034, 18011, 18008, 18001, 18004])

    # Normal Items
    if shop_type in [ShopData.SHOP_TYPE_COMMON_ITEMS, ShopData.SHOP_TYPE_ALL, ShopData.SHOP_TYPE_MIXED]:
        replacements.extend([22258, 22082, 22073, 22020, 22018, 22012, 22002, 22072, 22103])

    replacements = [item for item in replacements if item not in current_items]

    if len(replacements) == 0:
        raise Exception("Could not fill shop with replacements - this should not usually happen.", shop_type, current_items)

    return world_random.choice(replacements)


def get_random_valid_item(item_pool: Dict[int, int], existing_items: List[int], world_random: Random, shop_type: int) -> int:
    allowed_items = {k: v for k, v in item_pool.items() if k not in existing_items}
    if len(allowed_items) == 0:
        logging.warning("No allowed items remain - Shop will be have filler items")
        return get_backup_item(shop_type, existing_items, world_random)
    return world_random.choice(list(allowed_items.keys()))


def randomize_shops(patch_instance: "DQIXPatch", randomization_type: int) -> Dict[int, Dict]:
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
            ShopData.SHOP_TYPE_ALL: {},
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
                            logging.warning("{} shops left to place {} copies of item {} - ignoring the extras".format(len(unfilled_shops), amount, item))
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
                    new_item = get_random_valid_item(all_items, shuffled_shops[shop_to_fill].items, world_random, shuffled_shops[shop_to_fill].shop_type)
                    if new_item in all_items:
                        all_items[new_item] -= 1
                        if all_items[new_item] == 0:
                            all_items.pop(new_item)
                        shuffled_shops[shop_to_fill].items.append(new_item)
            if all_items:
                logging.warning("Still items left after filled all shops - something went wrong!")
                logging.warning("Remaining items in pool: " + str(all_items))
            for shop_id, shop in shuffled_shops.items():
                missing_item_count = shop.item_count - len(shop.items)
                if missing_item_count > 0:
                    for _ in range(missing_item_count):
                        backup_item = get_backup_item(shop.shop_type, shop.items, world_random)
                        shop.items.append(backup_item)
                        logging.warning("Filling shop {} that is missing slots with {}".format(shop_id, backup_item))

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
