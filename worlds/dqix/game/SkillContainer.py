import json
from typing import List

from ..game.SkillEntry import SkillEntry


class SkillContainer:
    divider_bytes = bytes.fromhex("66000955 5501FFFF")

    def __init__(self):
        self.start_bytes: bytes
        self.skills: dict[int, SkillEntry] = {}
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
            container.skills[entry.ability_id] = entry

        print("All Skills done, yeah!")
        print("Remainder is:")
        print(container.end_bytes)

        return container

    def to_bytes(self):
        out = bytearray()
        out += self.start_bytes
        out += self.divider_bytes.join([skill.to_bytes() for skill in self.skills.values()])
        out += self.end_bytes

        return bytes(out)

    def apply_new_skills(self, data: str):
        new_skill_data: list[dict[str, int]] = json.loads(data)

        for skill_data in new_skill_data:
            self.skills[skill_data["ability_id"]].skill_tree = skill_data["skill_tree"]
