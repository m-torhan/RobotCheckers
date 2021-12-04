import sys
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '../../../'))

import pygame
from pygame.locals import *
from time import perf_counter, sleep
import threading
import numpy as np
import random

from src.robot.game_logic.checkers import Checkers
from src.robot.ai.ai_player import AIPlayerAlphaBeta, AIPlayerMinimax, AIPlayerRandom

window_width = 768
window_height = 512

generation_size = 100
top_rate = .2
mutation_rate = .05
duels_per_generation = 4
eval_duels = 50

def sigmoid(x):
    return np.power(1 + np.exp(-x), -1)

def sigmoid_backward(d, x):
    s = sigmoid(x)
    return d*s*(1 - s)

def relu(x):
    return np.maximum(x, 0)

def leakyrelu(x):
    return np.where(x > 0, x, x*.01)

def conv2d(input, kernel):
    kernel_size = kernel.shape[0]
    pad = np.copy(input)
    pad = np.pad(pad, ((kernel_size//2,),(kernel_size//2,),(0,)))
    output = np.zeros((input.shape[0], input.shape[1], kernel.shape[3]))

    for x in range(output.shape[0]):
        for y in range(output.shape[1]):
            for f in range(output.shape[2]):
                output[x,y,f] = (pad[x:x + kernel_size,
                                     y:y + kernel_size]*kernel[:,:,:,f]).sum()

    return output

class AIPlayerNeuralNetworkGenetic(object):
    def __init__(self):
        self.num = 0
        self.__model_input_shape = (8, 8, 4)
        model_arch = [(0, 4)] + [(3, 8)]*8
        self.__kernels = [np.random.normal(size=(model_arch[i][0],
                                                 model_arch[i][0],
                                                 model_arch[i - 1][1],
                                                 model_arch[i][1])) for i in range(1, len(model_arch))] +\
                         [np.random.normal(size=(1, 1, model_arch[-1][1], 1))]
        self.__biases = [np.random.normal(size=(model_arch[i][1])) for i in range(1, len(model_arch))] +\
                        [np.random.normal(size=(1))]
        
        self.layers = []

    def make_move(self, checkers):
        move = self.get_best_move(checkers)

        ret, promoted = checkers.make_move(move)
        
        return move, ret, promoted

    def get_best_move(self, checkers):
        board = checkers.board.copy()

        if checkers.player_turn == 1:
            board = np.rot90(board, 2)
            board[board == 1] = 5
            board[board == 2] = 6
            board[board == 3] = 1
            board[board == 4] = 2
            board[board == 5] = 3
            board[board == 6] = 4

        layer_output = np.zeros(self.__model_input_shape)
        for i in range(4):
            layer_output[:,:,i] = board == (i + 1)

        self.layers = []
        self.layers.append(layer_output.copy())
        for i in range(len(self.__kernels)):
            layer_input = conv2d(layer_output, self.__kernels[i]) + self.__biases[i]
            if i < len(self.__kernels) - 1:
                layer_output = relu(layer_input)
                layer_output -= layer_output.mean()
                layer_output /= layer_output.std()
            else:
                layer_output = sigmoid(layer_input)
            self.layers.append(layer_output.copy())

        available_moves = checkers.calc_available_moves_for_player(checkers.player_turn)

        if checkers.player_turn == 1:
            layer_output = np.rot90(layer_output, 2)

        best_move = None
        best_score = 0
        for i, move in enumerate(available_moves):
            score = layer_output[move.src[0],move.src[1],0] + layer_output[move.dest[0],move.dest[1],0]
            if score > best_score or best_move is None:
                best_score = score
                best_move = move
        
        return best_move

    def breed(self, other):
        child = AIPlayerNeuralNetworkGenetic()

        for i in range(0, len(child.__kernels)):
            r = (np.random.randint(1, size=self.__kernels[i].shape) == 0).astype(np.int)
            child.__kernels[i] = self.__kernels[i]*r + other.__kernels[i]*(1 - r)
        for i in range(0, len(child.__biases)):
            r = (np.random.randint(1, size=self.__biases[i].shape) == 0).astype(np.int)
            child.__biases[i] = self.__biases[i]*r + other.__biases[i]*(1 - r)

        return child

    def mutate(self):
        for i in range(len(self.__kernels)):
            self.__kernels[i] += np.random.normal(size=self.__kernels[i].shape)/self.__kernels[i].shape[0]*\
                                 (np.random.randint(4, size=self.__kernels[i].shape) == 0)/16
        for i in range(len(self.__biases)):
            self.__biases[i] += np.random.normal(size=self.__biases[i].shape)/self.__biases[i].shape[0]*\
                                (np.random.randint(4, size=self.__biases[i].shape) == 0)/16
    
    def save_network(self, folder_name):
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)
        
        for i, kernel in enumerate(self.__kernels):
            np.save(os.path.join(folder_name, f'kernel_{i}'), kernel)

        for i, bias in enumerate(self.__biases):
            np.save(os.path.join(folder_name, f'bias_{i}'), bias)
    
    @classmethod
    def load_network(self, folder_name):
        i = 0

        ai_player = AIPlayerNeuralNetworkGenetic()

        while True:
            try:
                kernel = np.load(os.path.join(folder_name, f'kernel_{i}'))
                ai_player.__kernels.append(kernel)
                i += 1
            except:
                break

        while True:
            try:
                bias = np.load(os.path.join(folder_name, f'bias_{i}'))
                ai_player.__biases.append(bias)
                i += 1
            except:
                break
        
        return ai_player

available_moves = None
checkers = None
run = True
move_time = [[], []]
generation_num = 0
player_1_layers = None
player_2_layers = None

def train_fun():
    global run
    global checkers
    global available_moves
    global move_time
    global generation_num
    global generation_size
    global mutation_rate
    global top_rate
    global eval_duels
    global player_1_layers
    global player_2_layers

    generation = []
    for _ in range(generation_size):
        generation.append([0, AIPlayerNeuralNetworkGenetic()])
    while run:
        for d in range(duels_per_generation):
            shuffled = list(range(generation_size))
            random.shuffle(shuffled)
            pairs = [(shuffled[2*i], shuffled[2*i + 1]) for i in range(generation_size//2)]
        
            for i, (player_1_idx, player_2_idx) in enumerate(pairs):
                print(f'\r{generation_num} {d + 1}/{duels_per_generation}  {i + 1}/{len(pairs)}  ', end='')

                checkers = Checkers()

                player_1 = generation[player_1_idx][1]
                player_2 = generation[player_2_idx][1]
                player_1.num = 0
                player_2.num = 1

                while not checkers.end and run:
                    #sleep(1)
                    available_moves = checkers.calc_available_moves_for_player(checkers.player_turn)

                    time_0 = perf_counter()
                    if checkers.player_turn == player_1.num:
                        _ = player_1.make_move(checkers)
                        player_1_layers = player_1.layers

                    elif checkers.player_turn == player_2.num:
                        _ = player_2.make_move(checkers)
                        player_2_layers = player_2.layers
                    
                    #sleep(1)
                    move_time[checkers.player_turn == player_1.num].append(perf_counter() - time_0)
                
                if checkers.winner == player_1.num:
                    generation[player_1_idx][0] += 1
                    generation[player_2_idx][0] -= 1

                elif checkers.winner == player_2.num:
                    generation[player_1_idx][0] -= 1
                    generation[player_2_idx][0] += 1

        # new generation
        generation.sort(key=lambda x: x[0], reverse=True)
        
        print(f' {generation[0][0]} ', end='')

        # evaluate best
        player_2_layers = []
        score_rand = 0
        for _ in range(eval_duels):
            checkers = Checkers()

            r = random.getrandbits(1)
            player_1 = generation[0][1]
            player_1.num = int(r == 0)
            player_2 = AIPlayerRandom(int(r != 0))

            while not checkers.end and run:
                available_moves = checkers.calc_available_moves_for_player(checkers.player_turn)

                time_0 = perf_counter()
                if checkers.player_turn == player_1.num:
                    _ = player_1.make_move(checkers)
                    player_1_layers = player_1.layers

                elif checkers.player_turn == player_2.num:
                    _ = player_2.make_move(checkers)
                
                move_time[checkers.player_turn == player_1.num].append(perf_counter() - time_0)
            
            if checkers.winner == player_1.num:
                score_rand += 1

        print(f' score (vs rand): {score_rand/eval_duels:.4f}', end='')

        player_2_layers = []
        score_ab = 0
        for _ in range(eval_duels):
            checkers = Checkers()

            r = random.getrandbits(1)
            player_1 = generation[0][1]
            player_1.num = int(r == 0)
            player_2 = AIPlayerAlphaBeta(int(r != 0), 4)

            while not checkers.end and run:
                available_moves = checkers.calc_available_moves_for_player(checkers.player_turn)

                time_0 = perf_counter()
                if checkers.player_turn == player_1.num:
                    _ = player_1.make_move(checkers)
                    player_1_layers = player_1.layers

                elif checkers.player_turn == player_2.num:
                    _ = player_2.make_move(checkers)
                
                move_time[checkers.player_turn == player_1.num].append(perf_counter() - time_0)
            
            if checkers.winner == player_1.num:
                score_ab += 1

        print(f' score (vs ab): {score_ab/eval_duels:.4f}')

        generation[0][1].save_network(f'./neural_networks/gen_{generation_num}_{score_rand/eval_duels:.3f}_{score_ab/eval_duels:.3f}/'.replace('.', '_'))

        # remove worst
        generation = generation[:int(len(generation)*top_rate)]

        # breed
        while len(generation) < generation_size:
            parent_a, parent_b = random.sample(generation, 2)
            generation.append([0, parent_a[1].breed(parent_b[1])])
        
        # mutate
        for i in range(generation_size):
            generation[i][0] = 0
            if random.random() < mutation_rate:
                generation[i][1].mutate()

        generation_num += 1

train_thread = threading.Thread(target=train_fun)
thread_started = False

pygame.init()
window = pygame.display.set_mode((window_width, window_height), 0, 32)

pygame.display.set_caption('Pygame template')

def draw_text(text, size, color, surface, position, anchor=''):
    font = pygame.font.SysFont('consolas', size*3//4)
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if anchor == 'bottomleft':
        textrect.bottomleft = position
    elif anchor == 'topleft':
        textrect.topleft = position
    elif anchor == 'bottomright':
        textrect.bottomright = position
    elif anchor == 'topright':
        textrect.topright = position
    else:
        textrect.center = position

    surface.blit(textobj, textrect)

def terminate():
    pygame.quit()
    sys.exit()

time_0 = perf_counter()

clock = pygame.time.Clock()

run = True
while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        
        if event.type == KEYDOWN:
            if event.key == K_s and not thread_started:
                train_thread.start()
                thread_started = True

            if event.key == K_e:
                run = False
            
    delta_time, time_0 = perf_counter() - time_0, perf_counter()
    
    window.fill((0, 0, 0))
    
    if checkers is not None:
        for i in range(checkers.board.shape[0]):
            for j in range(checkers.board.shape[1]):
                pygame.draw.rect(window, ((192,)*3, (0, 192, 0))[(i + j) % 2], (32*i, 32*j, 32, 32), 0)
                square = checkers.board[i,j]
                col = None
                if square == 1:
                    col = (255,)*3
                elif square == 3:
                    col = (0,)*3
                elif square == 2:
                    col = (0, 0, 255)
                elif square == 4:
                    col = (255, 0, 0)
                if col is not None:
                    pygame.draw.circle(window, col, (32*i + 16, 32*j + 16), 10, 0)

    if available_moves is not None:
        for j, move in enumerate(available_moves):
            random.seed(j)
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            for i in range(len(move.chain) - 1):
                pygame.draw.line(window, (r, g, b), np.array(move.chain[i])*32 + 16, np.array(move.chain[i + 1])*32 + 16, 8)

    x_offset = 256
    y_offset = 0
    pix = 4
    if player_1_layers is not None:
        for layer in player_1_layers:
            for k in range(layer.shape[2]):
                for i in range(layer.shape[1]):
                    for j in range(layer.shape[0]):
                        pygame.draw.rect(window, (max(0, min(int(128 + 128*layer[j, i, k]), 255)),)*3, (x_offset + pix*i, y_offset + pix*j + layer.shape[0]*pix*k, pix, pix), 0)
            x_offset += (layer.shape[1] + 1)*pix

    x_offset = 256
    y_offset = 256
    if player_2_layers is not None:
        for layer in player_2_layers:
            for k in range(layer.shape[2]):
                for i in range(layer.shape[1]):
                    for j in range(layer.shape[0]):
                        pygame.draw.rect(window, (max(0, min(int(128 + 128*layer[j, i, k]), 255)),)*3, (x_offset + pix*i, y_offset + pix*j + layer.shape[0]*pix*k, pix, pix), 0)
            x_offset += (layer.shape[1] + 1)*pix

    # if len(move_time[0]) > 0 and len(move_time[1]) > 0:
    #     draw_text(f'{sum(move_time[0])/len(move_time[0]):.05f} {sum(move_time[1])/len(move_time[1]):.05f}', 16, (255,)*3, window, (384, 32))

    pygame.display.update()
    
    clock.tick(30)