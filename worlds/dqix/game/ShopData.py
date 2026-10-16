from typing import Dict, List, NamedTuple


class ShopConfig(NamedTuple):
    items: List[int]
    shop_type: int
    item_count: int


class ShopData:
    TYPE_WEAPONS = 0
    TYPE_ARMOR = 1
    TYPE_COMMON_ITEMS = 2
    TYPE_ITEMS_AND_EQUIPMENT = 3
    TYPE_ALL_EQUIPMENT = 4
    TYPE_MIXED = 5

    SHOPS_WITH_DATA: Dict[int, ShopConfig] = {
        32: ShopConfig([], 0, 18),
        0: ShopConfig([], 0, 18),
        1: ShopConfig([], 0, 18),
        36: ShopConfig([], 0, 18),
        2: ShopConfig([], 0, 6),
        3: ShopConfig([], 0, 18),
        4: ShopConfig([], 0, 18),
        5: ShopConfig([], 0, 18),
        6: ShopConfig([], 0, 6),
        7: ShopConfig([], 0, 18),
        8: ShopConfig([], 0, 18),
        9: ShopConfig([], 0, 12),
        10: ShopConfig([], 0, 18),
        11: ShopConfig([], 0, 18),
        12: ShopConfig([], 0, 12),
        33: ShopConfig([], 0, 18),
        13: ShopConfig([], 0, 18),
        14: ShopConfig([], 0, 18),
        15: ShopConfig([], 0, 12),
        16: ShopConfig([], 0, 12),
        17: ShopConfig([], 0, 18),
        18: ShopConfig([], 0, 18),
        19: ShopConfig([], 0, 12),
        20: ShopConfig([], 0, 18),
        21: ShopConfig([], 0, 18),
        22: ShopConfig([], 0, 12),
        23: ShopConfig([], 0, 18),
        24: ShopConfig([], 0, 18),
        25: ShopConfig([], 0, 18),
        26: ShopConfig([], 0, 12),
        27: ShopConfig([], 0, 18),
        28: ShopConfig([], 0, 18),
        29: ShopConfig([], 0, 12),
        34: ShopConfig([], 0, 6),
        30: ShopConfig([], 0, 1),
        35: ShopConfig([], 0, 18),
        37: ShopConfig([], 0, 12)
    }

    _items_by_shop_type_initialized = False

    ITEMS_BY_SHOP_TYPE: Dict[int, List[int]] = {
        TYPE_WEAPONS: [],
        TYPE_ARMOR: [],
        TYPE_COMMON_ITEMS: [],
        TYPE_ITEMS_AND_EQUIPMENT: [],
        TYPE_ALL_EQUIPMENT: [],
        TYPE_MIXED: []
    }

    @staticmethod
    def get_items_by_shop_type() -> dict[int, list[int]]:
        if not ShopData._items_by_shop_type_initialized:
            [ShopData.ITEMS_BY_SHOP_TYPE[shop.shop_type].extend(shop.items) for shop in ShopData.SHOPS_WITH_DATA.values()]
            ShopData._items_by_shop_type_initialized = True
        return ShopData.ITEMS_BY_SHOP_TYPE
