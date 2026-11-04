from ...game.skill.SkillLabelDefinition import SkillLabelDefinition


class SkillLabelTable:
    divider_bytes = bytes.fromhex("66000651 05FFFFFF")

    def __init__(self):
        self.record_count: int
        self.string_pool_offset: int
        self.string_pool_size: int
        self.string_count: int
        self.magic_starting_bytes: bytes

        self.skill_label_definitions: list[SkillLabelDefinition] = []
        self.skill_texts: list = []
        self.timestamp: bytes

    @staticmethod
    def create_from_bytes(data: bytearray):
        container = SkillLabelTable()

        container.record_count = int.from_bytes(data[0x0:0x4], "little")
        container.string_pool_offset = int.from_bytes(data[0x4:0x8], "little")
        container.string_pool_size = int.from_bytes(data[0x8:0xB], "little")
        container.string_count = int.from_bytes(data[0xB:0x10], "little")
        container.magic_starting_bytes = data[0x10:0x20]

        for i in range(286):
            starting_offset = 0x20 + i * 0x20
            end_offset = starting_offset + 0x20
            label = SkillLabelDefinition(data[starting_offset:end_offset])
            container.skill_label_definitions.append(label)

            text_start = container.string_pool_offset + label.name_offset
            text_end = data[text_start:].find(b'\x00')
            if text_end == -1:
                print("Could not find text end for skill: ")
                print(label.index)
                print(label.name_offset)
                print(label.append_icon)
                print(label.grants_ability_flag)
                print(label.cost)
                print(label.tree)
            else:
                container.skill_texts.append(str(data[text_start:text_start + text_end]))

        return container
