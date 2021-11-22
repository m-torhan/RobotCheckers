import random

import minimax
import monte_carlo

class AIPlayer(object):
    def __init__(self, num):
        self.__num = num

    @property
    def num(self):
        return self.__num

    def make_move(self, checkers):
        pass

class AIPlayerRandom(AIPlayer):
    def make_move(self, checkers):
        available_moves = checkers.calc_available_moves_for_player(self.num)
        move = random.choice(available_moves)
        ret = checkers.make_move(move)
        
        return move, ret

class AIPlayerMinimax(object):
    def __init__(self, num, max_depth):
        super(AIPlayerMinimax, self).__init__(num)
        self.__max_depth = max_depth

    def make_move(self, checkers):
        move = minimax.get_best_move(checkers, self.__max_depth)
        ret = checkers.make_move(move)
        
        return move, ret
        
class AIPlayerMonteCarlo(AIPlayer):
    def __init__(self, num, simulations):
        super(AIPlayerMonteCarlo, self).__init__(num)
        self.__simulations = simulations

    def make_move(self, checkers):
        move = monte_carlo.get_best_move(checkers, self.__simulations)
        ret = checkers.make_move(move)
        
        return move, ret