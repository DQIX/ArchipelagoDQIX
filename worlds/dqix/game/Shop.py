class Shop:
    def __init__(self, byte_data: bytes):
        """
        +0x0 4 bytes Shop identifier, 0 to 30 and 32 to 37
        +0x4 4 bytes of unknown purpose, ranging from 1 to 5
        +0x8 18x 4 bytes item id
        +0x50 4 bytes: Price multiplier in percent, usually 100
        +0x54 4 bytes: Shop Type, eg 3 for a "general" shop
        :param byte_data:
        """
        self.identifier = int.from_bytes(byte_data[0x0:0x4], "little")
        self.magic_number = int.from_bytes(byte_data[0x4:0x8], "little")

        item_bytes = byte_data[0x8: 0x50]
        self.items = [int.from_bytes(item_bytes[i:i + 4], "little") for i in range(0, len(item_bytes), 4)]
        self.price_multiplier = int.from_bytes(byte_data[0x50: 0x54], "little")
        self.shop_type = int.from_bytes(byte_data[0x54:0x58], "little")

        self.price_multiplier = self.price_multiplier * 5

    def to_bytes(self):
        """
        Transforms the shop back into it's corresponding bytes
        :return:
        """
        out = bytearray()
        out += bytearray(int.to_bytes(self.identifier, 4, "little"))
        out += bytearray(int.to_bytes(self.magic_number, 4, "little"))
        for i in range(18):
            # If the shop was not filled with enough items, mark the remaining ones as empty / 0
            item = self.items[i] if 0 <= i < len(self.items) else 0
            out += bytearray(int.to_bytes(item, 4, "little"))

        out += bytearray(int.to_bytes(self.price_multiplier, 4, "little"))
        out += bytearray(int.to_bytes(self.shop_type, 4, "little"))

        return out
