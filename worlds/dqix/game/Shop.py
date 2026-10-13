class Shop:
    def __init__(self, byte_data: bytes):
        self.identifier = int.from_bytes(byte_data[0x0:0x4], "little")
        self.magic_number = int.from_bytes(byte_data[0x4:0x8], "little")

        item_bytes = byte_data[0x8: 0x50]
        self.items = [int.from_bytes(item_bytes[i:i + 4], "little") for i in range(0, len(item_bytes), 4)]
        self.price_multiplier = int.from_bytes(byte_data[0x50: 0x54], "little")
        self.shop_type = int.from_bytes(byte_data[0x54:0x58], "little")
        # TODO actually do something with the bytes


class ShopContainer:
    def __init__(self):
        self.shops = []

    @staticmethod
    def create_from_bytes(data: bytearray):
        # 1x 4 bytes Shop identifier, 0 to 37(?)
        # 1x 4 magic bytes of unkown purpose, ranging from 1 to 5
        # 18x 4 bytes per item sold
        # 1x 4 bytes: Price multiplier in percent, normally 100 or "64000000" in Hex
        # 1x 4 bytes: Shop Type, eg 3 for a "general" shop, or "03000000" in Hex

        # Start of the first shop in Angel Falls: 0x34
        container = ShopContainer()
        for i in range(37):
            shop_offset = 0x34 + (0x58 * i)
            shop = Shop(data[shop_offset:shop_offset + 0x58])

            print("Data for Shop with Index " + str(i))
            print(shop)

            container.shops.append(shop)

        return container
