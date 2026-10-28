import json
import zipfile
from random import Random
from typing import TYPE_CHECKING, Dict

from ..apnds.rom import Rom
from ..game.SkillContainer import SkillContainer
from ..game.SkillData import SkillData

if TYPE_CHECKING:
    from .. import DQIXPatch


def write_patch(patch_instance: "DQIXPatch", opened_zipfile: zipfile.ZipFile) -> None:
    opened_zipfile.writestr("skilltrees.json", json.dumps(randomize_skill_trees(patch_instance.world.random)))


def patch(rom: Rom, patch_instance: "DQIXPatch") -> None:
    skill_data = bytearray(rom.files["/data/prm/skilltable.bin"])

    skill_container = SkillContainer.create_from_bytes(skill_data)

    skill_container.apply_new_skills(patch_instance.get_file("skilltrees.json"))

    rom.files["/data/prm/skilltable.bin"] = skill_container.to_bytes()


def randomize_skill_trees(world_random: Random) -> list[dict[str, int]]:
    new_skills: list[Dict[str, int]] = []
    skills_by_skill_tree: Dict[int, int] = {}
    unfilled_skill_trees = [i for i in range(0, 26)]

    for skill in SkillData.get_all_skills():
        target_tree = world_random.choice(unfilled_skill_trees)
        skill["skill_tree"] = target_tree
        if target_tree not in skills_by_skill_tree:
            skills_by_skill_tree[target_tree] = 0
        skills_by_skill_tree[target_tree] += 1
        new_skills.append(skill)

        if skills_by_skill_tree[target_tree] == 11:
            unfilled_skill_trees.remove(target_tree)

    return new_skills
