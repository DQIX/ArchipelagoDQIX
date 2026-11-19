import struct


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
        self.identifier, self.magic_number = struct.unpack("<II", byte_data[0x0:0x8])
        item_bytes = byte_data[0x8: 0x50]
        self.items = list(struct.unpack("<18I", item_bytes))
        self.price_multiplier, self.shop_type = struct.unpack("<II", byte_data[0x50:0x58])

    def to_bytes(self):
        """
        Transforms the shop back into it's corresponding bytes
        :return:
        """
        out = bytearray()

        out += struct.pack("<II", self.identifier, self.magic_number)
        for i in range(18):
            # If the shop was not filled with enough items, mark the remaining ones as empty / 0
            item = self.items[i] if 0 <= i < len(self.items) else 0
            out += struct.pack("<I", item)

        out += struct.pack("<II", self.price_multiplier, self.shop_type)

        return out
