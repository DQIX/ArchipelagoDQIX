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

        container.record_count = int.from_bytes(data[0x0:0x4], "little")
        container.string_pool_offset = int.from_bytes(data[0x4:0x8], "little")
        container.string_pool_size = int.from_bytes(data[0x8:0xB], "little")
        container.string_count = int.from_bytes(data[0xB:0x10], "little")
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

        out += int.to_bytes(self.record_count, 4, "little")
        out += int.to_bytes(self.string_pool_offset, 4, "little")
        out += int.to_bytes(self.string_pool_size, 4, "little")
        out += int.to_bytes(self.string_count, 4, "little")
        out += self.magic_starting_bytes

        for label in self.skill_labels:
            out += label.to_bytes()

        out += self.remainder_magic

        return out
