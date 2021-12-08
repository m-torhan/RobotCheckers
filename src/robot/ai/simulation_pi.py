import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '../../../'))

from time import perf_counter
import numpy as np
import random

from src.robot.ai.ai_player import AIPlayerRandom, AIPlayerMonteCarlo, AIPlayerMinimax, AIPlayerAlphaBeta, AIPlayerNeuralNetwork
from src.robot.game_logic.checkers import Checkers

games_per_pair = 10000
pairs = (
    ((AIPlayerRandom, None),   (AIPlayerMonteCarlo, 10)),
    ((AIPlayerRandom, None),   (AIPlayerMonteCarlo, 30)),
    ((AIPlayerRandom, None),   (AIPlayerMinimax, 2)),
    ((AIPlayerRandom, None),   (AIPlayerMinimax, 3)),
    ((AIPlayerRandom, None),   (AIPlayerAlphaBeta, 4)),
    ((AIPlayerRandom, None),   (AIPlayerAlphaBeta, 5)),
    ((AIPlayerMonteCarlo, 30), (AIPlayerMinimax, 2)),
    ((AIPlayerMonteCarlo, 30), (AIPlayerMinimax, 3)),
    ((AIPlayerMonteCarlo, 30), (AIPlayerAlphaBeta, 4)),
    ((AIPlayerMonteCarlo, 30), (AIPlayerAlphaBeta, 5)),
)

scores = [[0, 0, 0] for _ in range(len(pairs))]
moves_time = [[0, 0] for _ in range(len(pairs))]
moves_count = [[0, 0] for _ in range(len(pairs))]
names = []
for i in range(len(pairs)):
    (player_1_ai, player_1_param), (player_2_ai, player_2_param) = pairs[i]
    if player_1_param is None:
        player_1 = player_1_ai(0)
    else:
        player_1 = player_1_ai(0, player_1_param)

    if player_2_param is None:
        player_2 = player_2_ai(1)
    else:
        player_2 = player_2_ai(1, player_2_param)

    names.append([str(player_1), str(player_2)])

for j in range(games_per_pair):
    for i in range(len(pairs)):
        (player_1_ai, player_1_param), (player_2_ai, player_2_param) = pairs[i]

        checkers = Checkers(0)
        r = random.getrandbits(1)
        player_1_num = int(r == 0)
        player_2_num = int(r != 0)

        if player_1_param is None:
            player_1 = player_1_ai(player_1_num)
        else:
            player_1 = player_1_ai(player_1_num, player_1_param)

        if player_2_param is None:
            player_2 = player_2_ai(player_2_num)
        else:
            player_2 = player_2_ai(player_2_num, player_2_param)

        while not checkers.end:
            time_0 = perf_counter()

            if checkers.player_turn == player_1.num:
                _ = player_1.make_move(checkers)

            elif checkers.player_turn == player_2.num:
                _ = player_2.make_move(checkers)
            
            moves_time[i][checkers.player_turn == player_1.num] += perf_counter() - time_0
            moves_count[i][checkers.player_turn == player_1.num] += 1
            
        if checkers.winner == player_1_num:
            scores[i][0] += 1
        elif checkers.winner == player_2_num:
            scores[i][2] += 1
        else:
            scores[i][1] += 1

        l = [0, 0]
        for k in range(len(pairs)):
            l[0] = max(len(str(names[k])), l[0])
            l[1] = max(len(str(scores[k])), l[1])

        os.system('cls')
        for k in range(len(pairs)):
            print(f'pair: {str(names[k]).ljust(l[0])} score: {str(scores[k]).ljust(l[1])}, move time: [{moves_time[k][0]/(moves_count[k][0] + 1e-7):.5f}, {moves_time[k][1]/(moves_count[k][1] + 1e-7):.5f}]')