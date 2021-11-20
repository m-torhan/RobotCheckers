from enum import auto

from src.robot.game_logic.common.enums.extended_enum import ExtendedEnum

class MoveType(ExtendedEnum):
    REGULAR = auto()
    TAKING  = auto()
