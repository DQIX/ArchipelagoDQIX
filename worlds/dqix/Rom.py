import logging
from typing import TYPE_CHECKING, Dict, Any, Callable
from zipfile import ZipFile

from .options import RandomizeShops
from Utils import Version
from .patch import shop_patch
from worlds.Files import APAutoPatchInterface
from settings import get_settings

if TYPE_CHECKING:
    from worlds.dqix import DragonQuestIX


class DQIXPatch(APAutoPatchInterface):
    game = "Dragon Quest IX"
    patch_file_ending = ".apdqix"
    result_file_ending = ".nds"
    DQIX_HASH: str = "3a63438fff7db282fa3133e8fd020e85"
    PATCH_VERSION = Version(1, 0, 0)

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

    def has_file(self, file: str) -> bool:
        return PatchMethods.has_file(self, file)


class PatchMethods:
    @staticmethod
    def write_contents(patch: DQIXPatch, opened_zipfile: ZipFile) -> None:
        procedures: list[str] = ["base_patch"]

        if patch.world.options.randomize_shops.value != RandomizeShops.option_none:
            procedures.append("shop_patch")
            shop_patch.write_patch(patch, opened_zipfile)

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
                    DQIXPatch,
                ],
                None,
            ],
        ] = {
            "base_patch": base_patch.patch,
            "shop_patch": shop_patch.patch
        }

        base_data = get_base_rom_bytes()
        rom = apnds_rom.Rom.from_bytes(base_data)
        procedures: list[str] = str(
            patch.get_file("procedures.txt"), "utf-8"
        ).splitlines()
        for prod in procedures:
            patch_procedures[prod](rom, patch)

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

    @staticmethod
    def has_file(patch: DQIXPatch, file: str) -> bool:
        if file not in patch.files:
            patch.read()
        return file in patch.files


def get_base_rom_bytes() -> bytes:
    with open(get_settings().dqix_options.rom_file, "rb") as infile:
        base_rom_bytes = bytes(infile.read())

    return base_rom_bytes
