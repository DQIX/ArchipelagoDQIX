from typing import TYPE_CHECKING

from ..apnds.rom import Rom, HeaderField

if TYPE_CHECKING:
    from .. import DQIXPatch


def patch(rom: Rom, world_package: str, patch_instance: "DQIXPatch", files_dump: dict[str, bytes | bytearray]) -> None:
    version_string = "APDQIX{}.{}.{}\0".format(patch_instance.PATCH_VERSION.major, patch_instance.PATCH_VERSION.minor, patch_instance.PATCH_VERSION.build)

    rom.header[HeaderField.TITLE] = version_string.encode("ascii")
