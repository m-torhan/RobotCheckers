from enum import auto

from src.common.enums.ExtendedEnum import ExtendedEnum


class FieldStatus(ExtendedEnum):
    EMPTY_FIELD = 0
    PLAYER_1_REGULAR_PAWN = auto()
    PLAYER_1_KING = auto()
    PLAYER_2_REGULAR_PAWN = auto()
    PLAYER_2_KING = auto()
