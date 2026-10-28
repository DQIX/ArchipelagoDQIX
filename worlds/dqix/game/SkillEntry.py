class SkillEntry:
    def __init__(self, byte_data: bytes):
        """
        +0x0 4 bytes Ability ID, e.g 12 for "Mercurial Thrust"
        +0x4 4 bytes skill tree (1 - 26)
        +0x8 4 bytes skill point cost to learn (total for tree)
        +0xA 4 bytes actionId learned when gaining the ability
        +0xA 4 bytes "Nature" of the ability, e.g. 1 = ability, 2 = attack, 3 Crit modifier...
        +0xA 4 bytes Actual bonus value, e.g. 30 (for health)
        +0xA 4 bytes Secondary action
        +0xA 4 bytes row number
        +0xA 4 bytes display category
        :param byte_data:
        """
        self.ability_id = int.from_bytes(byte_data[0x0:0x4], "little")
        self.skill_tree = int.from_bytes(byte_data[0x4:0x8], "little")
        self.skill_point_cost = int.from_bytes(byte_data[0x8:0xC], "little")
        self.action_id = int.from_bytes(byte_data[0xC:0x10], "little")
        self.nature = int.from_bytes(byte_data[0x10:0x14], "little")
        self.bonus_value = int.from_bytes(byte_data[0x14:0x18], "little")
        self.secondary_action = int.from_bytes(byte_data[0x18:0x1C], "little")
        self.row_number = int.from_bytes(byte_data[0x1C:0x20], "little")
        self.display_category = int.from_bytes(byte_data[0x20:0x24], "little")

    def to_bytes(self):
        """
        Transforms the SkillEntry back into it's corresponding bytes
        :return:
        """
        out = bytearray()

        out += bytearray(int.to_bytes(self.ability_id, 4, "little"))
        out += bytearray(int.to_bytes(self.skill_tree, 4, "little"))
        out += bytearray(int.to_bytes(self.skill_point_cost, 4, "little"))
        out += bytearray(int.to_bytes(self.action_id, 4, "little"))
        out += bytearray(int.to_bytes(self.nature, 4, "little"))
        out += bytearray(int.to_bytes(self.bonus_value, 4, "little"))
        out += bytearray(int.to_bytes(self.secondary_action, 4, "little"))
        out += bytearray(int.to_bytes(self.row_number, 4, "little"))
        out += bytearray(int.to_bytes(self.display_category, 4, "little"))

        return out

    def to_dict(self):
        return {
            "ability_id": self.ability_id,
            "skill_tree": self.skill_tree,
            "skill_point_cost": self.skill_point_cost,
            "action_id": self.action_id,
            "nature": self.nature,
            "bonus_value": self.bonus_value,
            "secondary_action": self.secondary_action,
            "row_number": self.row_number,
            "display_category": self.display_category,
        }

