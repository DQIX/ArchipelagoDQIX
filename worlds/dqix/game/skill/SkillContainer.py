from .SkillData import SkillData
from .SkillLabelDefinition import SkillLabelDefinition
from .SkillNameTable import SkillLabelTable
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

    def update_skill_labels(self, skill_table: SkillLabelTable) -> SkillLabelTable:
        new_list: list[SkillLabelDefinition] = []

        original_skill_labels_by_tree_and_cost: dict[int, dict[int, SkillLabelDefinition]] = {}
        modified_skill_labels_by_tree_and_cost: dict[int, dict[int, SkillLabelDefinition]] = {}

        for label in skill_table.skill_labels:
            if label.tree not in original_skill_labels_by_tree_and_cost:
                original_skill_labels_by_tree_and_cost[label.tree] = {}
            original_skill_labels_by_tree_and_cost[label.tree][label.cost] = label

        for skill in self.skills:
            orig_skill = SkillData.get_original_skill_by_ability_id(skill.ability_id)

            skill_definition = original_skill_labels_by_tree_and_cost[orig_skill.tree][orig_skill.cost]
            skill_definition.tree = skill.skill_tree
            skill_definition.cost = skill.skill_point_cost

            if skill_definition.tree not in modified_skill_labels_by_tree_and_cost:
                modified_skill_labels_by_tree_and_cost[skill_definition.tree] = {}
            modified_skill_labels_by_tree_and_cost[skill_definition.tree][skill_definition.cost] = skill_definition

        for tree, skills in sorted(modified_skill_labels_by_tree_and_cost.items(), key=lambda x: x[0]):
            for skill_def in sorted(skills.values(), key=lambda x: x.cost if x.cost > 0 else 1000):
                new_list.append(skill_def)

        skill_table.skill_labels = new_list

        return skill_table
