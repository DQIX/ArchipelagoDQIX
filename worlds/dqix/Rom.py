import logging
from typing import TYPE_CHECKING, Dict, Any, Callable
from zipfile import ZipFile

from worlds.Files import APAutoPatchInterface
from settings import get_settings

if TYPE_CHECKING:
    from worlds.dqix import DragonQuestIX



class DQIXPatch(APAutoPatchInterface):
    game = "Dragon Quest IX"
    patch_file_ending = ".apdqix"
    result_file_ending = ".nds"
    DQIX_HASH: str = "3a63438fff7db282fa3133e8fd020e85"

    def __init__(self, path: str, player=None, player_name="", world=None):
        self.world: "DragonQuestIX" = world
        self.files: dict[str, bytes] = {}
        super().__init__(path, player, player_name, "")

    def write_contents(self, opened_zipfile: ZipFile) -> None:
        super().write_contents(opened_zipfile)
        PatchMethods.write_contents(self, opened_zipfile)

    def get_manifest(self) -> Dict[str, Any]:
        return PatchMethods.get_manifest(self, super().get_manifest())

    def patch(self, target: str) -> None:
        PatchMethods.patch(self, target)

    def read_contents(self, opened_zipfile: ZipFile) -> Dict[str, Any]:
        return PatchMethods.read_contents(
            self, opened_zipfile, super().read_contents(opened_zipfile)
        )

    def get_file(self, file: str) -> bytes:
        return PatchMethods.get_file(self, file)


class PatchMethods:
    @staticmethod
    def write_contents(patch: DQIXPatch, opened_zipfile: ZipFile) -> None:
        procedures: list[str] = ["base_patch"]

        opened_zipfile.writestr("procedures.txt", "\n".join(procedures))

    @staticmethod
    def get_manifest(patch: DQIXPatch, manifest: dict[str, Any]) -> Dict[str, Any]:
        manifest["dqix_patch_format"] = 1
        return manifest

    @staticmethod
    def patch(patch: DQIXPatch, target: str) -> None:
        patch.read()

        logging.warning(f"Starting rom patching")

        from .apnds import rom as apnds_rom
        from .patch import base_patch

        patch_procedures: dict[
            str,
            Callable[
                [
                    apnds_rom.Rom,
                    str,
                    DQIXPatch,
                    dict[str, bytes | bytearray],
                ],
                None,
            ],
        ] = {
            "base_patch": base_patch.patch
        }

        files_dump: dict[str, bytes | bytearray] = {}
        base_data = get_base_rom_bytes()
        rom = apnds_rom.Rom.from_bytes(base_data)
        procedures: list[str] = str(
            patch.get_file("procedures.txt"), "utf-8"
        ).splitlines()
        for prod in procedures:
            patch_procedures[prod](rom, __name__, patch, files_dump)

        with open(target, "wb") as f:
            f.write(rom.to_bytes())

    @staticmethod
    def read_contents(patch: DQIXPatch, opened_zipfile: ZipFile, manifest: Dict[str, Any]) -> Dict[str, Any]:
        for file in opened_zipfile.namelist():
            if file not in ["archipelago.json"]:
                patch.files[file] = opened_zipfile.read(file)

        return manifest

    @staticmethod
    def get_file(patch: DQIXPatch, file: str) -> bytes:
        if file not in patch.files:
            patch.read()
        return patch.files[file]


def get_base_rom_bytes() -> bytes:
    with open(get_settings().dqix_options.rom_file, "rb") as infile:
        base_rom_bytes = bytes(infile.read())

    return base_rom_bytes


def patch_rom(world: "DragonQuestIX", patch: DQIXPatch) -> None:
    # patch.write_token(APTokenTypes.WRITE, 0x0FFFFFF0, b"APDQIX")
    # patch.write_file("token_data.bin", patch.get_token_binary())
    pass
