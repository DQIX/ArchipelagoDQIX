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
