from enum import auto
import sys

sys.path.append('../../../../../')

from src.robot.game_logic.common.enums.extended_enum import ExtendedEnum

class PlayerEnum(ExtendedEnum):
    PLAYER_1 = 1
    PLAYER_2 = auto()
