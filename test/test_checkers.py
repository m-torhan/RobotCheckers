import sys

sys.path.append('..')
sys.path.append('../src/robot/ai')
sys.path.append('../src/robot/game_logic')

import random
import unittest

from src.robot.game_logic.checkers import Checkers
from src.robot.ai.ai_player import AIPlayerRandom

class BoardTest(unittest.TestCase):
    def test_calc_move_between_boards(self):
        for _ in range(100):
            checkers = Checkers()

            player_1 = AIPlayerRandom(0)
            player_2 = AIPlayerRandom(1)

            for _ in range(random.randint(0, 16)):
                if checkers.player_turn == player_1.num:
                    _ = player_1.make_move(checkers)

                elif checkers.player_turn == player_2.num:
                    _ = player_2.make_move(checkers)
                
            new_checkers = checkers.copy()

            if new_checkers.player_turn == player_1.num:
                move, _, _ = player_1.make_move(new_checkers)

            elif new_checkers.player_turn == player_2.num:
                move, _, _ = player_2.make_move(new_checkers)
            
            new_board = new_checkers.board

            calc_move = checkers.calc_move_between_boards(new_board)

            self.assertEqual(move, calc_move)

if __name__ == '__main__':
    unittest.main()
