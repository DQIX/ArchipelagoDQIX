import zipfile
from typing import TYPE_CHECKING

from ..apnds.rom import Rom
from ..game.SkillContainer import SkillContainer

if TYPE_CHECKING:
    from .. import DQIXPatch


def write_patch(patch_instance: "DQIXPatch", opened_zipfile: zipfile.ZipFile) -> None:
    pass


def patch(rom: Rom, patch_instance: "DQIXPatch") -> None:
    skill_data = bytearray(rom.files["/data/prm/skilltable.bin"])

    skill_container = SkillContainer.create_from_bytes(skill_data)

    rom.files["/data/prm/skilltable.bin"] = skill_container.to_bytes()
