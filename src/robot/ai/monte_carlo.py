import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '../../../'))

import src.robot.ai.ai_player as ai_player

def get_best_move(checkers, simulations):
    player_num = checkers.player_turn

    available_moves = checkers.calc_available_moves_for_player(checkers.player_turn)
    move_score = []

    for move in available_moves:

        player_1 = ai_player.AIPlayerRandom(1 - player_num)
        player_2 = ai_player.AIPlayerRandom(player_num)

        s = 0
        for _ in range(simulations):
            new_checkers = checkers.copy()
            new_checkers.make_move(move, False)
            while not new_checkers.end:
                if new_checkers.player_turn == player_1.num:
                    move, _, _ = player_1.make_move(new_checkers)

                elif new_checkers.player_turn == player_2.num:
                    move, _, _ = player_2.make_move(new_checkers)
                
            if new_checkers.winner == player_num:
                s += 5
            elif new_checkers.winner == -1:
                s += 1
        
        move_score.append(s)
    
    return available_moves[move_score.index(max(move_score))]