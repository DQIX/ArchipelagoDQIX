import json
from typing import List

from ..game.Shop import Shop


class ShopContainer:
    def __init__(self):
        self.shops: List[Shop] = []
        self.start_bytes: bytes
        self.end_bytes: bytes
        self.divider_bytes = bytes.fromhex('67001655 55555555 05FFFFFF')

    @staticmethod
    def create_from_bytes(data: bytearray):
        container = ShopContainer()
        container.start_bytes = data[0x0:0x34]
        container.end_bytes = data[0xE9C:]

        for i in range(37):
            # Start of the Shop data section + length of one shop entry + 12 Bytes of offset / divider between shops
            shop_offset = 0x34 + (0x58 * i) + (12 * i)
            shop = Shop(data[shop_offset:shop_offset + 0x58])
            container.shops.append(shop)

        return container

    def to_bytes(self):
        out = bytearray()
        out += self.start_bytes
        out += self.divider_bytes.join([shop.to_bytes() for shop in self.shops])
        out += self.end_bytes

        return bytes(out)

    def apply_new_shop_data(self, data: str):
        new_shop_data = json.loads(data)

        for index, shop in enumerate(self.shops):
            relevant_data = new_shop_data[str(shop.identifier)]
            shop.items = relevant_data["items"]
            shop.shop_type = relevant_data["shop_type"]
            self.shops[index] = shop

    def apply_shop_price_modifiers(self, data: str):
        price_modifiers = json.loads(data)

        for index, shop in enumerate(self.shops):
            if str(shop.identifier) in price_modifiers:
                shop.price_multiplier = price_modifiers[str(shop.identifier)]
                self.shops[index] = shop
            else:
                raise Exception("No price modifiers for shop with ID {} were found - this should not happen.".format(index))
