import struct


class SkillLabelDefinition:
    def __init__(self, data: bytes):
        self.magic_bytes: bytes = data[0x0:0x8]
        self.index, self.text_offset, grants_ability_flag, self.tree, self.cost, append_icon = struct.unpack("<IIIIII", data[0x8:])
        self.grants_ability_flag: bool = bool(grants_ability_flag)
        self.append_icon: bool = bool(append_icon)
        # self.text_offset: int = 27

    def to_bytes(self):
        out = bytearray()

        out += self.magic_bytes
        out += struct.pack("<IIIIII", self.index, self.text_offset, 1 if self.grants_ability_flag else 0, self.tree, self.cost, 1 if self.append_icon else 0)

        return out
