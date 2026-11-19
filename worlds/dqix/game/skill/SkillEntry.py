import struct


class SkillEntry:
    def __init__(self, byte_data: bytes):
        """
        +0x0 4 bytes Ability ID, e.g. 12 for "Mercurial Thrust"
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
        self.ability_id, self.skill_tree, self.skill_point_cost, self.action_id, self.nature, self.bonus_value, self.secondary_action, self.row_number, self.display_category = struct.unpack("<9I", byte_data)

    def to_bytes(self):
        """
        Transforms the SkillEntry back into it's corresponding bytes
        :return:
        """
        return struct.pack('<9I', self.ability_id, self.skill_tree, self.skill_point_cost, self.action_id, self.nature, self.bonus_value, self.secondary_action, self.row_number, self.display_category)

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
