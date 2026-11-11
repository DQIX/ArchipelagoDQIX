import struct

from ...game.skill.SkillLabelDefinition import SkillLabelDefinition


class SkillNamingTable:
    divider_bytes = bytes.fromhex("66000651 05FFFFFF")

    def __init__(self):
        self.record_count: int
        self.string_pool_offset: int
        self.string_pool_size: int
        self.string_count: int
        self.magic_starting_bytes: bytes

        self.skill_labels: list[SkillLabelDefinition] = []

        self.remainder_magic: bytes

    @staticmethod
    def create_from_bytes(data: bytearray):
        container = SkillNamingTable()

        container.record_count, container.string_pool_offset, container.string_pool_size, container.string_count = struct.unpack("<IIII", data[0x0:0x10])
        container.magic_starting_bytes = data[0x10:0x20]

        for i in range(287):
            starting_offset = 0x20 + i * 0x20
            end_offset = starting_offset + 0x20
            label = SkillLabelDefinition(data[starting_offset:end_offset])

            container.skill_labels.append(label)

        container.remainder_magic = data[container.string_pool_offset:]

        return container

    def to_bytes(self):
        out: bytearray = bytearray()

        out += struct.pack("<IIII", self.record_count, self.string_pool_offset, self.string_pool_size, self.string_count)

        out += self.magic_starting_bytes

        for label in self.skill_labels:
            out += label.to_bytes()

        out += self.remainder_magic

        return out

    def get_text_by_offset(self, text_offset: int):
        if text_offset == int('0xFFFFFFFF', 16):
            text = ''
        else:
            text_end = self.remainder_magic[text_offset:].find(b'\x00')
            if text_end == -1:
                raise "Could not find text end for skill - this should not happen!"
            else:
                text = str(self.remainder_magic[text_offset:text_offset + text_end])

        return text
