from enum import auto

from src.common.enums.ExtendedEnum import ExtendedEnum


class MoveType(ExtendedEnum):
    REGULAR = auto()
    TAKING = auto()
