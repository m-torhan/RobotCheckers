from typing import Tuple, List


class Move:
    def __init__(self, position, pawns_for_taking: List[Tuple[int, int]] = None):
        self._position = position
        self._next_move = []
        if pawns_for_taking is None:
            self._pawns_for_taking = []
        else:
            self._pawns_for_taking = pawns_for_taking

    def get_position(self):
        return self._position

    @property
    def next_move(self):
        return self._next_move

    def add_next_move(self, move):
        self._next_move.append(move)

    @property
    def pawns_for_taking(self):
        return self._pawns_for_taking

    def add_pawn_for_taking(self, pawn: Tuple[int, int]):
        self._pawns_for_taking.append(pawn)

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self._position == other.get_position() \
               and self.pawns_for_taking == other.pawns_for_taking \
               and self.next_move == other.next_move

