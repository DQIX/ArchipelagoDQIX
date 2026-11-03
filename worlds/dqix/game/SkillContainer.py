import json

from ..game.SkillEntry import SkillEntry


class SkillContainer:
    divider_bytes = bytes.fromhex("66000955 5501FFFF")

    def __init__(self):
        self.start_bytes: bytes
        self.skills: list[SkillEntry] = []
        self.end_bytes: bytes

    @staticmethod
    def create_from_bytes(data: bytearray):
        container = SkillContainer()
        container.start_bytes = data[0x0:0x28]
        container.end_bytes = data[0x3148:]

        print("Start bytes:")
        print(container.start_bytes)

        rest_data = data[0x28:0x3148].split(SkillContainer.divider_bytes)
        for skill_data in rest_data:
            entry = SkillEntry(skill_data)
            container.skills.append(entry)

        print("All Skills done, yeah!")
        print("Remainder is:")
        print(container.end_bytes)

        return container

    def to_bytes(self):
        out = bytearray()
        out += self.start_bytes
        out += self.divider_bytes.join([skill.to_bytes() for skill in self.skills])
        out += self.end_bytes

        return bytes(out)

    def apply_new_skills(self, data: str):
        new_skill_data: list[dict[str, int]] = json.loads(data)

        new_skills = []
        for skill in self.skills:
            new_data = new_skill_data.pop()
            skill.ability_id = new_data["skill_id"]
            skill.action_id = new_data["action_id"]
            skill.nature = new_data["nature"]
            skill.bonus_value = new_data["bonus"]
            skill.secondary_action = new_data["secondary_action"]
            skill.display_category = new_data["display_category"]
            new_skills.append(skill)

        self.skills = new_skills
