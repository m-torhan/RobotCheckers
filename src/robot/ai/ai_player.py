import random

import minimax

class AIPlayer(object):
    def __init__(self, algorithm=None):
        if algorithm == 'random':
            self.get_next_move = lambda _, moves: random.choice(moves)
        elif algorithm == 'minimax':
            self.get_next_move = minimax.get_next_move
        else:
            raise ValueError
