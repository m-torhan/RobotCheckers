from webserver.checkers.common.extended_enum import ExtendedEnum


class Winner(ExtendedEnum):
    DRAW = -1
    PLAYER1 = 0
    PLAYER2 = 1
