from web.apps.checkers.common.extended_enum import ExtendedEnum


class UserAction(ExtendedEnum):
    END_GAME = 'end_game'
    STOP_ROBOT = 'stop_robot'
    RESUME_ROBOT = 'resume_robot'
