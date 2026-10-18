from typing import Dict, List, NamedTuple


class ShopConfig(NamedTuple):
    items: List[int]
    shop_type: int
    item_count: int
    region: str


class ShopData:
    TYPE_WEAPONS = 0
    TYPE_ARMOR = 1
    TYPE_COMMON_ITEMS = 2
    TYPE_ITEMS_AND_EQUIPMENT = 3
    TYPE_ALL_EQUIPMENT = 4
    TYPE_MIXED = 5

    REGION_NEWID_ISLE = "newid_isle"
    REGION_CENTRAL_ISLAND = "central_island"
    REGION_BLOOMINGDALE_AREA = "bloomingdale_area"
    REGION_NORTH_EAST = "north_east"
    REGION_POST_FALL = "post_fall"
    REGION_REST_OF_WORLD = "rest_of_world"

    SHOPS_WITH_DATA: Dict[int, ShopConfig] = {
        32: ShopConfig([22000, 22004, 22019, 20004, 20005, 20300, 20100, 21296, 21291, 12410, 13005, 13095, 13101, 15003, 16094, 16213, 17406, 17404], TYPE_ITEMS_AND_EQUIPMENT, 18, REGION_NEWID_ISLE),
        0: ShopConfig([20004, 20005, 20003, 20500, 20503, 19050, 19051, 19052, 20403, 20494, 20300, 20301, 20600, 20601, 20800, 20801, 20100, 20101], TYPE_WEAPONS, 18, REGION_NEWID_ISLE),
        1: ShopConfig([21291, 21192, 12410, 12205, 12498, 13095, 13101, 13102, 13103, 13519, 13006, 13305, 15200, 15003, 16213, 16214, 17404, 17408], TYPE_ARMOR, 18, REGION_NEWID_ISLE),
        36: ShopConfig([21291, 21192, 12410, 12205, 12498, 13095, 13101, 13102, 13103, 13519, 13006, 13305, 15200, 15003, 16213, 16214, 17404, 17408], TYPE_ARMOR, 18, REGION_NEWID_ISLE),
        2: ShopConfig([22000, 22004, 22019, 22257, 22018, 18007], TYPE_COMMON_ITEMS, 6, REGION_NEWID_ISLE),
        3: ShopConfig([22000, 22007, 22019, 22018, 21192, 21091, 12498, 12411, 13519, 13203, 13305, 15200, 15004, 16095, 16312, 17118, 17405, 18009], TYPE_ITEMS_AND_EQUIPMENT, 18, REGION_NEWID_ISLE),
        4: ShopConfig([20003, 20006, 20503, 20506, 19051, 19052, 19053, 20403, 20494, 20404, 20301, 20302, 20601, 20602, 20801, 20805, 20101, 20104], TYPE_WEAPONS, 18, REGION_NEWID_ISLE),
        5: ShopConfig([21091, 21001, 12411, 12495, 13103, 13197, 13790, 13011, 13039, 15200, 15291, 15005, 16095, 16307, 16218, 17118, 17391, 17405], TYPE_ARMOR, 18, REGION_NEWID_ISLE),
        6: ShopConfig([22000, 22004, 22007, 22019, 22257, 22018], TYPE_COMMON_ITEMS, 6, REGION_NEWID_ISLE),
        7: ShopConfig([22000, 22004, 22019, 20006, 20506, 19053, 20404, 20302, 20602, 20805, 20104, 21092, 12191, 13192, 13039, 13306, 16218, 16316], TYPE_ITEMS_AND_EQUIPMENT, 18, REGION_CENTRAL_ISLAND),
        8: ShopConfig([20293, 19152, 20700, 20901, 21092, 12191, 12416, 12208, 13192, 13791, 13012, 13605, 15291, 15009, 16216, 16104, 17391, 17119], TYPE_ALL_EQUIPMENT, 18, REGION_CENTRAL_ISLAND),
        9: ShopConfig([22000, 22004, 22007, 22019, 22257, 22018, 22010, 22015, 18009, 18005, 18004, 18007], TYPE_COMMON_ITEMS, 12, REGION_CENTRAL_ISLAND),
        10: ShopConfig([22000, 22004, 22007, 22019, 22257, 22018, 22015, 12796, 12496, 13791, 13306, 15033, 15009, 16216, 16302, 17119, 17411, 18011], TYPE_ITEMS_AND_EQUIPMENT, 18, REGION_BLOOMINGDALE_AREA),
        11: ShopConfig([20010, 20507, 19057, 20406, 20303, 20603, 20804, 20105, 21004, 12191, 12700, 13183, 13520, 15010, 15048, 16263, 16311, 17102], TYPE_ALL_EQUIPMENT, 18, REGION_BLOOMINGDALE_AREA),
        12: ShopConfig([22000, 22004, 22007, 22019, 22018, 22010, 22015, 18005, 18004, 18007, 18010, 18011], TYPE_ITEMS_AND_EQUIPMENT, 12, REGION_BLOOMINGDALE_AREA),
        33: ShopConfig([20208, 19159, 20905, 21292, 21392, 12800, 12801, 12809, 13522, 13606, 13608, 13620, 15032, 16302, 16104, 16303, 16229, 17408], TYPE_ITEMS_AND_EQUIPMENT, 18, REGION_BLOOMINGDALE_AREA),
        13: ShopConfig([20010, 20012, 20507, 20508, 19057, 19061, 19064, 20406, 20408, 20303, 20306, 20603, 20606, 20804, 20806, 20105, 20107, 20702], TYPE_WEAPONS, 18, REGION_BLOOMINGDALE_AREA),
        14: ShopConfig([21004, 21005, 12790, 12400, 12200, 12201, 12801, 13183, 13180, 13001, 13015, 13504, 13032, 15000, 16317, 16205, 16200, 16203], TYPE_ARMOR, 18, REGION_BLOOMINGDALE_AREA),
        15: ShopConfig([17100, 17108, 17101, 17105, 17106, 17109, 17110, 17302, 17402, 17400, 17403, 17104], TYPE_ARMOR, 12, REGION_BLOOMINGDALE_AREA),
        16: ShopConfig([22023, 22024, 22000, 22003, 22004, 22007, 22008, 22019, 22257, 22018, 22010, 22015], TYPE_COMMON_ITEMS, 12, REGION_BLOOMINGDALE_AREA),
        17: ShopConfig([20012, 20001, 20508, 20511, 19058, 19064, 20408, 20495, 20306, 20307, 20606, 20609, 20806, 20809, 20111, 20200, 19153, 20704], TYPE_WEAPONS, 18, REGION_NORTH_EAST),
        18: ShopConfig([21290, 12792, 12429, 12600, 12701, 12403, 13184, 13521, 13205, 13325, 15298, 15100, 15001, 16204, 16202, 16207, 16208, 17103], TYPE_ARMOR, 18, REGION_NORTH_EAST),
        19: ShopConfig([22000, 22001, 22004, 22005, 22007, 22019, 22257, 22018, 22010, 22015, 18010, 18011], TYPE_COMMON_ITEMS, 12, REGION_NORTH_EAST),
        20: ShopConfig([20001, 20002, 20511, 20502, 19058, 20495, 20307, 20609, 20607, 20809, 20113, 20200, 19153, 20702, 20704, 20705, 20903, 20900], TYPE_WEAPONS, 18, REGION_NORTH_EAST),
        21: ShopConfig([21390, 21395, 12702, 12401, 12407, 12408, 12202, 13601, 13500, 13003, 15102, 15106, 16308, 16100, 16103, 16210, 16209, 17114], TYPE_ARMOR, 18, REGION_NORTH_EAST),
        22: ShopConfig([22000, 22001, 22004, 22007, 22019, 22257, 22018, 22010, 22015, 22021, 22022, 22103], TYPE_COMMON_ITEMS, 12, REGION_NORTH_EAST),
        23: ShopConfig([22000, 22004, 22007, 22019, 22018, 22015, 20502, 20496, 20109, 12295, 12814, 13009, 16258, 16306, 16313, 16318, 16212, 17404], TYPE_MIXED, 18, REGION_NORTH_EAST),
        24: ShopConfig([20002, 20013, 20511, 20512, 19059, 20410, 20310, 20611, 20809, 20811, 20200, 20205, 19153, 19155, 20705, 20708, 20900, 20907], TYPE_WEAPONS, 18, REGION_POST_FALL),
        25: ShopConfig([21000, 21391, 12180, 12295, 12404, 12402, 13187, 13041, 13017, 13329, 15101, 15103, 15002, 16223, 16309, 16300, 17300, 17111], TYPE_ARMOR, 18, REGION_POST_FALL),
        26: ShopConfig([22000, 22001, 22004, 22005, 22007, 22019, 22257, 22018, 22010, 22015, 22021, 22022], TYPE_COMMON_ITEMS, 12, REGION_POST_FALL),
        27: ShopConfig([20019, 20513, 19062, 20493, 20310, 20611, 20614, 20811, 20812, 20115, 20205, 20291, 19155, 19156, 20708, 20710, 20907, 20910], TYPE_WEAPONS, 18, REGION_POST_FALL),
        28: ShopConfig([21391, 21006, 21292, 12795, 12207, 12417, 13187, 13172, 13207, 13329, 15105, 15043, 15013, 15019, 16206, 16319, 17115, 17401], TYPE_ARMOR, 18, REGION_POST_FALL),
        29: ShopConfig([22000, 22001, 22004, 22005, 22007, 22019, 22257, 22018, 22010, 22015, 22021, 22022], TYPE_COMMON_ITEMS, 12, REGION_POST_FALL),
        34: ShopConfig([22000, 22004, 22019, 22018, 22010, 22015], TYPE_COMMON_ITEMS, 6, REGION_REST_OF_WORLD),
        30: ShopConfig([22258], TYPE_COMMON_ITEMS, 1, REGION_REST_OF_WORLD),
        35: ShopConfig([21294, 12405, 12406, 12409, 12204, 13174, 13604, 13503, 13018, 13627, 13390, 13391, 15047, 16224, 17112, 17117, 17113, 17116], TYPE_ARMOR, 18, REGION_NEWID_ISLE),
        37: ShopConfig([20015, 20515, 19065, 20401, 20314, 20615, 20814, 20118, 20210, 19161, 20712, 20911], TYPE_WEAPONS, 12, REGION_NEWID_ISLE),
    }

    _items_by_shop_type_initialized = False
    _items_by_region_initialized = False
    _items_by_region_and_shop_type_initialized = False
    _ungrouped_items_initialized = False

    ITEMS_BY_SHOP_TYPE: Dict[int, List[int]] = {
        TYPE_WEAPONS: [],
        TYPE_ARMOR: [],
        TYPE_COMMON_ITEMS: [],
        TYPE_ITEMS_AND_EQUIPMENT: [],
        TYPE_ALL_EQUIPMENT: [],
        TYPE_MIXED: []
    }

    ITEMS_BY_REGION: Dict[str, Dict[int, int]] = {
        REGION_NEWID_ISLE: {},
        REGION_CENTRAL_ISLAND: {},
        REGION_BLOOMINGDALE_AREA: {},
        REGION_NORTH_EAST: {},
        REGION_POST_FALL: {},
        REGION_REST_OF_WORLD: {}
    }

    ITEMS_BY_REGION_AND_SHOP_TYPE: Dict[str, Dict[int, Dict[int, int]]] = {
        REGION_NEWID_ISLE: {
            TYPE_WEAPONS: {},
            TYPE_ARMOR: {},
            TYPE_COMMON_ITEMS: {},
            TYPE_ITEMS_AND_EQUIPMENT: {},
            TYPE_ALL_EQUIPMENT: {},
            TYPE_MIXED: {}
        },
        REGION_CENTRAL_ISLAND: {
            TYPE_WEAPONS: {},
            TYPE_ARMOR: {},
            TYPE_COMMON_ITEMS: {},
            TYPE_ITEMS_AND_EQUIPMENT: {},
            TYPE_ALL_EQUIPMENT: {},
            TYPE_MIXED: {}
        },
        REGION_BLOOMINGDALE_AREA: {
            TYPE_WEAPONS: {},
            TYPE_ARMOR: {},
            TYPE_COMMON_ITEMS: {},
            TYPE_ITEMS_AND_EQUIPMENT: {},
            TYPE_ALL_EQUIPMENT: {},
            TYPE_MIXED: {}
        },
        REGION_NORTH_EAST: {
            TYPE_WEAPONS: {},
            TYPE_ARMOR: {},
            TYPE_COMMON_ITEMS: {},
            TYPE_ITEMS_AND_EQUIPMENT: {},
            TYPE_ALL_EQUIPMENT: {},
            TYPE_MIXED: {}
        },
        REGION_POST_FALL: {
            TYPE_WEAPONS: {},
            TYPE_ARMOR: {},
            TYPE_COMMON_ITEMS: {},
            TYPE_ITEMS_AND_EQUIPMENT: {},
            TYPE_ALL_EQUIPMENT: {},
            TYPE_MIXED: {}
        },
        REGION_REST_OF_WORLD: {
            TYPE_WEAPONS: {},
            TYPE_ARMOR: {},
            TYPE_COMMON_ITEMS: {},
            TYPE_ITEMS_AND_EQUIPMENT: {},
            TYPE_ALL_EQUIPMENT: {},
            TYPE_MIXED: {}
        }
    }

    ALL_ITEMS: Dict[int, int] = {}

    def init(self) -> None:
        self.init_grouped_by_shop_type()
        self.init_grouped_by_region()
        self.init_grouped_by_region_and_shop_type()
        self.init_ungrouped()

    def init_grouped_by_shop_type(self):
        if not self._items_by_shop_type_initialized:
            for shop in self.SHOPS_WITH_DATA.values():
                for item in shop.items:
                    self.ITEMS_BY_SHOP_TYPE[shop.shop_type].append(item)
            self._items_by_shop_type_initialized = True

    def init_grouped_by_region(self):
        if not self._items_by_region_initialized:
            for shop in self.SHOPS_WITH_DATA.values():
                for item in shop.items:
                    if item not in self.ITEMS_BY_REGION[shop.region]:
                        self.ITEMS_BY_REGION[shop.region][item] = 1
                    else:
                        self.ITEMS_BY_REGION[shop.region][item] += 1
            self._items_by_region_initialized = True

    def init_grouped_by_region_and_shop_type(self):
        if not self._items_by_region_and_shop_type_initialized:
            for shop in self.SHOPS_WITH_DATA.values():
                for item in shop.items:
                    if item not in self.ITEMS_BY_REGION_AND_SHOP_TYPE[shop.region][shop.shop_type]:
                        self.ITEMS_BY_REGION_AND_SHOP_TYPE[shop.region][shop.shop_type][item] = 1
                    else:
                        self.ITEMS_BY_REGION_AND_SHOP_TYPE[shop.region][shop.shop_type][item] += 1
            self._items_by_region_and_shop_type_initialized = True

    def init_ungrouped(self):
        if not self._ungrouped_items_initialized:
            for shop in self.SHOPS_WITH_DATA.values():
                for item in shop.items:
                    if item not in self.ALL_ITEMS:
                        self.ALL_ITEMS[item] = 1
                    else:
                        self.ALL_ITEMS[item] += 1
            self._ungrouped_items_initialized = True

    def get_items_grouped_by_shop_type(self) -> dict[int, list[int]]:
        self.init_grouped_by_shop_type()
        return self.ITEMS_BY_SHOP_TYPE

    def get_items_grouped_by_region(self) -> dict[str, dict[int, int]]:
        self.init_grouped_by_region()
        return self.ITEMS_BY_REGION

    def get_items_grouped_by_region_and_shop_type(self) -> dict[str, dict[int, dict[int, int]]]:
        self.init_grouped_by_region_and_shop_type()
        return self.ITEMS_BY_REGION_AND_SHOP_TYPE

    def get_ungrouped_items(self):
        self.init_ungrouped()
        return self.ALL_ITEMS
