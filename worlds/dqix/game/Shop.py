class Shop:
    def __init__(self, byte_data: bytes):
        self.identifier = int.from_bytes(byte_data[0x0:0x4], "little")
        self.magic_number = int.from_bytes(byte_data[0x4:0x8], "little")

        item_bytes = byte_data[0x8: 0x50]
        self.items = [int.from_bytes(item_bytes[i:i + 4], "little") for i in range(0, len(item_bytes), 4)]
        self.price_multiplier = int.from_bytes(byte_data[0x50: 0x54], "little")
        self.shop_type = int.from_bytes(byte_data[0x54:0x58], "little")

        self.price_multiplier = self.price_multiplier * 5

    def to_bytes(self):
        out = bytearray()
        out += bytearray(int.to_bytes(self.identifier, 4, "little"))
        out += bytearray(int.to_bytes(self.magic_number, 4, "little"))
        for item in self.items:
            out += bytearray(int.to_bytes(item, 4, "little"))

        out += bytearray(int.to_bytes(self.price_multiplier, 4, "little"))
        out += bytearray(int.to_bytes(self.shop_type, 4, "little"))

        return out


class ShopContainer:
    def __init__(self):
        self.shops = []
        self.start_bytes: bytes
        self.end_bytes: bytes
        self.divider_bytes = bytes.fromhex('670016555555555505FFFFFF')

    @staticmethod
    def create_from_bytes(data: bytearray):
        # 1x 4 bytes Shop identifier, 0 to 37 (almost)
        # 1x 4 bytes of unknown purpose, ranging from 1 to 5
        # 18x 4 bytes per item sold
        # 1x 4 bytes: Price multiplier in percent, normally 100
        # 1x 4 bytes: Shop Type, eg 3 for a "general" shop

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
