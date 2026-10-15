from typing import Dict


class ShopData:
    TYPE_WEAPONS = 0
    TYPE_ARMOR = 1
    TYPE_COMMON_ITEMS = 2
    TYPE_ITEMS_AND_EQUIPMENT = 3
    TYPE_ALL_EQUIPMENT = 4
    TYPE_MIXED = 5

    ITEM_COUNT_BY_SHOP: Dict[int, int] = {
        32: 18,
        0: 18,
        1: 18,
        36: 18,
        2: 6,
        3: 18,
        4: 18,
        5: 18,
        6: 6,
        7: 18,
        8: 18,
        9: 12,
        10: 18,
        11: 18,
        12: 12,
        33: 18,
        13: 18,
        14: 18,
        15: 12,
        16: 12,
        17: 18,
        18: 18,
        19: 12,
        20: 18,
        21: 18,
        22: 12,
        23: 18,
        24: 18,
        25: 18,
        26: 12,
        27: 18,
        28: 18,
        29: 12,
        34: 6,
        30: 1,
        35: 18,
        37: 12
    }
