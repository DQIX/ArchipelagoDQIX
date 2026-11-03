class SkillDetails:
    def __init__(self, skill_id: int, action_id: int, bonus: int, display_category: int, nature: int, secondary_action: int):
        self.skill_id = skill_id
        self.action_id = action_id
        self.bonus = bonus
        self.display_category = display_category
        self.nature = nature
        self.secondary_action = secondary_action

    def to_dict(self) -> dict[str, int]:
        return {
            "skill_id": self.skill_id,
            "action_id": self.action_id,
            "bonus": self.bonus,
            "display_category": self.display_category,
            "nature": self.nature,
            "secondary_action": self.secondary_action
        }
