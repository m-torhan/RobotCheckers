from enum import auto
import sys

sys.path.append('../../../../../')

from src.robot.game_logic.common.enums.extended_enum import ExtendedEnum

class FieldStatus(ExtendedEnum):
    EMPTY_FIELD           = 0
    PLAYER_1_REGULAR_PAWN = auto()
    PLAYER_1_KING         = auto()
    PLAYER_2_REGULAR_PAWN = auto()
    PLAYER_2_KING         = auto()
