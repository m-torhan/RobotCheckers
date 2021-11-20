import sys

sys.path.append('../../../../../')

from src.robot.game_logic.common.enums.field_status import FieldStatus
from src.robot.game_logic.common.constants.consts import BOARD_SIZE

class BasePlayer:
    def __init__(self):
        pass

    def get_starting_positions(self):
        raise NotImplementedError

    def get_regular_pawn(self):
        raise NotImplementedError

    def get_king_pawn(self):
        raise NotImplementedError

class Player1(BasePlayer):
    def __init__(self):
        self._starting_position = []
        self.init()

    def init(self, positions=None):
        if positions is None:
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE//2 - 1):
                    if (x + y)%2 == 1:
                        self._starting_position.append((x, y))
        else:
            self._starting_position = positions

    def get_starting_positions(self):
        return self._starting_position

    def get_regular_pawn(self):
        return FieldStatus.PLAYER_1_REGULAR_PAWN

    def get_king_pawn(self):
        return FieldStatus.PLAYER_1_KING

class Player2(BasePlayer):
    def __init__(self):
        self._starting_position = []
        self.init()

    def init(self, positions=None):
        if positions is None:
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE//2 + 1, BOARD_SIZE):
                    if (x + y)%2 == 1:
                        self._starting_position.append((x, y))
        else:
            self._starting_position = positions

    def get_starting_positions(self):
        return self._starting_position

    def get_regular_pawn(self):
        return FieldStatus.PLAYER_2_REGULAR_PAWN

    def get_king_pawn(self):
        return FieldStatus.PLAYER_2_KING
