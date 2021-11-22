import sys

sys.path.append('../../../')

from src.robot.game_logic.checkers import Checkers
import ai_player

def get_best_move(checkers, simulations):
    player_num = checkers.player_turn

    available_moves = checkers.calc_available_moves_for_player(checkers.player_turn)
    win_probability = []

    for move in available_moves:
        new_checkers = checkers.copy()
        new_checkers.make_move(move, False)

        player_1 = ai_player.AIPlayerRandom(1 - player_num)
        player_2 = ai_player.AIPlayerRandom(player_num)

        s = 0
        for _ in range(simulations):
            while not new_checkers.end:
                if new_checkers.player_turn == player_1.num:
                    move, _ = player_1.make_move(new_checkers)

                elif new_checkers.player_turn == player_2.num:
                    move, _ = player_2.make_move(new_checkers)
                
            if new_checkers.winner == player_num:
                s += 1
        
        win_probability.append(s/simulations)
    
    return available_moves[win_probability.index(max(win_probability))]