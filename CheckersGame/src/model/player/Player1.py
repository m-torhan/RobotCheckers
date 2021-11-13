from src.common.enums.FieldStatus import FieldStatus
from src.common.constants.consts import BOARD_SIZE
from src.model.player.BasePlayer import BasePlayer


class Player1(BasePlayer):
    def __init__(self):
        self._starting_position = []
        self.init()

    def init(self, positions=None):
        if positions is None:
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE // 2 - 1):
                    if (x + y) % 2 == 1:
                        self._starting_position.append((x, y))
        else:
            self._starting_position = positions

    def get_starting_positions(self):
        return self._starting_position

    def get_regular_pawn(self):
        return FieldStatus.PLAYER_1_REGULAR_PAWN

    def get_king_pawn(self):
        return FieldStatus.PLAYER_1_KING
