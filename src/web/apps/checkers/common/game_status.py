from enum import auto

from web.apps.checkers.common.extended_enum import ExtendedEnum


class GameStatus(ExtendedEnum):
    BOARD_PREPARATION_STARTED = auto()
    BOARD_COULD_NOT_BE_CALIBRATED_BY_CV = auto()
    CALIBRATION_FINISHED = auto()
    BOARD_PREPARATION_FINISHED = auto()
    READY_TO_PLAY = auto()
    ROBOTS_MOVE_STARTED = auto()
    ROBOTS_MOVE_ENDED = auto()
    PLAYERS_MOVE_STARTED = auto()
    PLAYERS_MOVE_ENDED = auto()
    GAME_FINISHED = auto()
    INVALID_MOVE = auto()
    REMOVE_HAND = auto()
