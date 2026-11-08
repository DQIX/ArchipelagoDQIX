from .SkillData import SkillData
from .SkillLabelDefinition import SkillLabelDefinition
from .SkillNameTable import SkillNamingTable
from ..skill.SkillEntry import SkillEntry


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

        rest_data = data[0x28:0x3148].split(SkillContainer.divider_bytes)
        for skill_data in rest_data:
            entry = SkillEntry(skill_data)
            container.skills.append(entry)

        return container

    def to_bytes(self):
        out = bytearray()
        out += self.start_bytes
        out += self.divider_bytes.join([skill.to_bytes() for skill in self.skills])
        out += self.end_bytes

        return bytes(out)

    def apply_new_skills(self, new_skill_data: list[dict[str, int]]):
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

    def update_skill_labels(self, skill_table: SkillNamingTable) -> SkillNamingTable:
        new_list: list[SkillLabelDefinition] = []
        original_naming_data_by_tree_and_cost: dict[int, dict[int, dict[str, int | bool]]] = {}
        new_skills_by_tree_and_cost = self.get_skills_by_tree_and_cost()

        # Mapping of the naming data for a given skill / position in the original skill tree
        for label in skill_table.skill_labels:
            if label.tree not in original_naming_data_by_tree_and_cost:
                original_naming_data_by_tree_and_cost[label.tree] = {}
            original_naming_data_by_tree_and_cost[label.tree][label.cost] = {
                "text_offset": label.text_offset,
                "append_icon": label.append_icon
            }

        """
        Wir suchen den korrekten Eintrag für den Skill in Tree X und Cost Y, nachdem der Randomizer am Werk war
        Wir haben die vanilla Daten mit der Zuordnung: Tree X und Cost Y => passende Bezeichnung und Icon Ja/Nein
        
        Basierend auf unseren randomized skills, die ihre eigenen position und cost haben jetzt, müssen wir die bestehenden Labels updaten,
        mit korrekten Text-Offset und Icon anzeigen Ja/Nein
        
        Für jedes bestehende Label: Was sind die neuen Werte für dieses Label an Tree X und Cost Y?
        => Den Skill holen, der jetzt neu an Tree X und Cost Y liegt. self.skills nach tree und cost
          => Für diese Ability-ID: Text-Offset herholen aus Original-Liste
          => Daten für Ability-ID Z für das aktuelle Label anwenden   
        """

        for i, label in enumerate(skill_table.skill_labels):
            if label.tree == 0:
                continue
            new_ability_id: int = new_skills_by_tree_and_cost[label.tree][label.cost]
            original_tree, original_cost = SkillData.get_original_tree_and_cost_by_ability_id(new_ability_id)

            # noinspection bad-assignment
            label.append_icon = original_naming_data_by_tree_and_cost[original_tree][original_cost]["append_icon"]
            label.text_offset = original_naming_data_by_tree_and_cost[original_tree][original_cost]["text_offset"]
            new_list.append(label)

        skill_table.skill_labels = new_list

        return skill_table

    def get_skills_by_tree_and_cost(self) -> dict[int, dict[int, int]]:
        out = {}
        for skill in self.skills:
            if skill.skill_tree not in out:
                out[skill.skill_tree] = {}
            out[skill.skill_tree][skill.skill_point_cost] = skill.ability_id

        return out
