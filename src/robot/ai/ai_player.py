import random

import minimax

class AIPlayerRandom(object):
    def __init__(self, num):
        self.__num = num
    
    @property
    def num(self):
        return self.__num

    def make_move(self, checkers):
        available_moves = checkers.calc_available_moves_for_player(self.__num)
        move = random.choice(available_moves)
        ret = checkers.make_move(move)
        
        return move, ret

class AIPlayerMinimax(object):
    def __init__(self, num, max_depth):
        self.__num = num
        self.__max_depth = max_depth

    @property
    def num(self):
        return self.__num

    def make_move(self, checkers):
        move = minimax.get_best_move(checkers, self.__max_depth)
        ret = checkers.make_move(move)
        
        return move, ret