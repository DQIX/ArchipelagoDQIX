from typing import List

from ..game.SkillEntry import SkillEntry


class SkillContainer:
    divider_bytes = bytes.fromhex("66000955 5501FFFF")

    def __init__(self):
        self.start_bytes: bytes
        self.skills: List[SkillEntry] = []
        self.end_bytes: bytes

    @staticmethod
    def create_from_bytes(data: bytearray):
        container = SkillContainer()
        container.start_bytes = data[0x0:0x28]
        container.end_bytes = data[0x311C:]

        print("Start bytes:")
        print(container.start_bytes)

        rest_data = data[0x28:0x3148].split(SkillContainer.divider_bytes)
        for skill_data in rest_data:
            entry = SkillEntry(skill_data)
            if entry.skill_point_cost > 0:
                entry.skill_point_cost = 10
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
