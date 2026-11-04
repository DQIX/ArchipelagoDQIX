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
    if not patch_instance.has_file("skilltrees.json"):
        raise "Tried to apply skill patch, but no skilltree file was present in the patch!"

    new_skill_data: list[dict[str, int]] = json.loads(patch_instance.get_file("skilltrees.json"))

    skill_data = bytearray(rom.files["/data/prm/skilltable.bin"])
    skill_container = SkillContainer.create_from_bytes(skill_data)
    skill_container.apply_new_skills(new_skill_data)

    rom.files["/data/prm/skilltable.bin"] = skill_container.to_bytes()

    skill_container.update_skill_labels(new_skill_data)


def randomize_skill_trees(world_random: Random) -> list[dict[str, int]]:
    shuffled_skills = SkillData.get_all_skills()
    world_random.shuffle(shuffled_skills)

    return [skill.to_dict() for skill in shuffled_skills]
