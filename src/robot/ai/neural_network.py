import sys
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '../../../'))

import numpy as np

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
    
class NeuralNetwork(object):
    def __init__(self, network_folder):
        i = 0
        self.__model_input_shape = (8, 8, 4)
        self.__kernels = []
        self.__biases = []

        while True:
            try:
                kernel = np.load(os.path.join(network_folder, f'kernel_{i}'))
                self.__kernels.append(kernel)
                i += 1
            except:
                break

        while True:
            try:
                bias = np.load(os.path.join(network_folder, f'bias_{i}'))
                self.__biases.append(bias)
                i += 1
            except:
                break
    
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

def get_network(network_folder):
    return NeuralNetwork(network_folder)