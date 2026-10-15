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
