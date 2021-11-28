from webserver.checkers.common.extended_enum import ExtendedEnum


class StartMode(ExtendedEnum):
    PLAYER = 'player'
    ROBOT = 'robot'
    RANDOM = 'random'
