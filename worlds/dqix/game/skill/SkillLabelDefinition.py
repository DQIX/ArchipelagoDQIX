class SkillLabelDefinition:
    def __init__(self, data: bytes):
        self.magic_bytes: bytes = data[0x0:0x8]
        self.index: int = int.from_bytes(data[0x8:0xC], "little")
        self.name_offset: int = int.from_bytes(data[0xC:0x10], "little")
        self.grants_ability_flag: bool = True if int.from_bytes(data[0x10:0x14], "little") == 1 else False
        self.tree: int = int.from_bytes(data[0x14:0x18], "little")
        self.cost: int = int.from_bytes(data[0x18:0x1C], "little")
        self.append_icon: bool = True if int.from_bytes(data[0x1C:0x20], "little") == 1 else False
