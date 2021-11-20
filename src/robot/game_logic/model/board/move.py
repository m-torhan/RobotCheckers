from typing import Tuple, List

class Move(object):
    def __init__(self, src, dest, pawns_for_taking: List[Tuple[int, int]] = None):
        self._src = src
        self._dest = dest
        self._next_move = []
        if pawns_for_taking is None:
            self._pawns_for_taking = []
        else:
            self._pawns_for_taking = pawns_for_taking

    @property
    def src(self):
        return self._src

    @property
    def dest(self):
        return self._dest

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
        return self._position == other._dest \
               and self.pawns_for_taking == other.pawns_for_taking \
               and self.next_move == other.next_move

