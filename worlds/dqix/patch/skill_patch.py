import json
import zipfile
from random import Random
from typing import TYPE_CHECKING, Dict

from ..apnds.rom import Rom
from ..game.skill.SkillContainer import SkillContainer
from ..game.skill.SkillData import SkillData
from ..game.skill.SkillNameTable import SkillNamingTable
from ..gpc2 import GPC2
from ..options import RandomizeSkills

if TYPE_CHECKING:
    from .. import DQIXPatch


def write_patch(patch_instance: "DQIXPatch", opened_zipfile: zipfile.ZipFile) -> None:
    opened_zipfile.writestr("skilltrees.json", json.dumps(randomize_skill_trees(patch_instance)))


def patch(rom: Rom, patch_instance: "DQIXPatch") -> None:
    if not patch_instance.has_file("skilltrees.json"):
        raise "Tried to apply skill patch, but no skilltree file was present in the patch!"

    new_skill_data: list[dict[str, int]] = json.loads(patch_instance.get_file("skilltrees.json"))

    skill_data = bytearray(rom.files["/data/prm/skilltable.bin"])
    skill_container = SkillContainer.create_from_bytes(skill_data)
    skill_container.apply_new_skills(new_skill_data.copy())

    rom.files["/data/prm/skilltable.bin"] = skill_container.to_bytes()

    # Update skill names, so they properly show in the skill tree menu
    name_data = rom.files["/data/prm/sklname.gp2"]
    archive = GPC2(name_data)
    tables: Dict[str, SkillNamingTable] = {}

    for filename, file in archive.files.items():
        tables[filename] = SkillNamingTable.create_from_bytes(file)

    for filename, skill_table in tables.items():
        new_skill_table = skill_container.update_skill_labels(skill_table)
        archive.replace(filename, new_skill_table.to_bytes())

    rom.files["/data/prm/sklname.gp2"] = archive.to_bytes()


def randomize_skill_trees(patch_instance: "DQIXPatch") -> list[dict[str, int]]:
    world_random: Random = patch_instance.world.random
    randomized_skills = []

    if patch_instance.world.options.randomize_skills.value == RandomizeSkills.option_fully_random:
        skills = SkillData.get_all_randomizable_skills()
        world_random.shuffle(skills)
        randomized_skills = skills

    return [skill.to_dict() for skill in randomized_skills]
