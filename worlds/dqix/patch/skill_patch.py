import json
import zipfile
from random import Random
from typing import TYPE_CHECKING

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
    shuffled_skills = SkillData.get_all_skills()
    world_random.shuffle(shuffled_skills)

    return [skill.to_dict() for skill in shuffled_skills]
