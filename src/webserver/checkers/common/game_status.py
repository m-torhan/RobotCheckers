from enum import auto

from checkers.common.extended_enum import ExtendedEnum


class GameStatus(ExtendedEnum):
    BOARD_PREPARATION_STARTED = auto()
    BOARD_PREPARATION_ENDED = auto()
    READY_TO_PLAY = auto()
    ROBOTS_MOVE_STARTED = auto()
    ROBOTS_MOVE_ENDED = auto()
    PLAYERS_MOVE_STARTED = auto()
    PLAYERS_MOVE_ENDED = auto()
    GAME_FINISHED = auto()
    INVALID_MOVE = auto()
    REMOVE_HAND = auto()
