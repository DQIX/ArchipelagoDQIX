from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range


class EndBoss(Choice):
    """Determines which Boss needs to be defeated to finish the game"""
    display_name = "Game Goal"
    auto_display_name = True

    option_master_of_nuun = 0
    option_greygnarl = 1
    option_corvus = 2

    default = option_corvus


class FillerAmount(Range):
    """Percentage of the item pool that should contain filler items (Gold and XP)"""
    display_name = "Filler Amount"

    range_start = 0
    range_end = 90
    default = 10


class RandomizeShops(Choice):
    """
    Choose if and how the shops should be randomized.
    - "None" => Do not randomize Shops
    - "Same Shop Type" => Shops of the same type are randomized
    - "Same Region" => Shops in the same region are randomized
    - "Same Shop Type And Region" => Shops of the same type and in the same region are randomized
    - "True Random" => All Shops get randomized together
    """
    display_name = "Randomize Shops"
    auto_display_name = True

    option_none = 0
    option_same_shop_type = 1
    option_same_region = 2
    option_same_shop_type_and_region = 3
    option_true_random = 4

    default = option_none


@dataclass
class DQIXOptions(PerGameCommonOptions):
    end_boss: EndBoss
    filler_amount: FillerAmount
    randomize_shops: RandomizeShops
