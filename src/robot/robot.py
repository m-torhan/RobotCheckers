import sys
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '../'))
sys.path.append(os.path.join(dir_path, './ai'))
sys.path.append(os.path.join(dir_path, './computer_vision'))
sys.path.append(os.path.join(dir_path, './game_logic'))
sys.path.append(os.path.join(dir_path, './movement'))

import threading
import numpy as np
import time

from ai.ai_player import *
from computer_vision.camera import CameraHandler, camera_config
from game_logic.checkers import Checkers, Move
from movement.driver import MovementHandler, driver_config

class RobotCheckers(object):
    def __init__(self):
        self.__movement_handler = MovementHandler()
        self.__camera_handler = CameraHandler(True)
        self.__robot_thread = threading.Thread(target=self.__robot_handler)

        self.__checkers = None
        self.__ai_player = None
        self.__play = False

        self.__player_move_valid = True
        self.__robot_arm_moving = False
        self.__run = True
    
    @property
    def calibrated(self):
        return self.__camera_handler.initialized and self.__movement_handler.calibrated
        
    @property
    def driver_calibrated(self):
        return self.__movement_handler.calibrated
        
    @property
    def camera_calibrated(self):
        return self.__camera_handler.initialized
    
    @property
    def board_from_chekcers(self):
        if self.__checkers is None or self.__ai_player is None:
            return None

        # not sure when board should be roated 180 - TODO check it
        if self.__ai_player.num == 0:
            return self.__checkers.board
        else:
            return np.rot90(self.__checkers.board, 2)
    
    @property
    def board_from_camera(self):
        return self.__camera_handler.read_board()[0]
    
    @property
    def board_from_checkers(self):
        if self.__checkers is not None:
            return self.__checkers.board
        return None
    
    @property
    def all_moves(self):
        if self.__checkers is not None:
            return self.__checkers.all_moves
        return None
    
    @property
    def turn_counter(self):
        if self.__checkers is not None:
            return self.__checkers.turn_counter
        return None
    
    @property
    def winner(self):
        if self.__checkers is not None:
            return self.__checkers.winner
        return None
    
    @property
    def player_turn(self):
        if self.__checkers is not None:
            return self.__checkers.player_turn != self.__ai_player.num
        return None
    
    @property
    def player_move_valid(self):
        return self.__player_move_valid
    
    @property
    def player_available_moves(self):
        if self.__checkers is not None:
            return self.__checkers.calc_available_moves_for_player(
                self.__checkers.oponent(self.__ai_player.num))
        return None
    
    def start(self):
        self.__movement_handler.start()
        self.__camera_handler.start()
    
        self.__robot_thread.start()
    
    def stop(self):
        self.__run = False

        self.__robot_thread.join()

        self.__camera_handler.stop()
        self.__movement_handler.stop()

    def initialize_game(self, robot_color, difficulty):
        self.__checkers = Checkers()

        if difficulty == 1:
            # random
            self.__ai_player = AIPlayerRandom(robot_color)
        elif difficulty <= 4:
            # MonteCarlo with 10, 20, 30 simulations per move
            self.__ai_player = AIPlayerMonteCarlo(robot_color, (difficulty - 1)*10)
        elif difficulty <= 7:
            # Minimax with depth of 2, 3, 4
            self.__ai_player = AIPlayerMinimax(robot_color, difficulty - 3)
        else:
            # Alpha-beta with depth of 5, 6, 7
            self.__ai_player = AIPlayerMinimax(robot_color, difficulty - 3)

        # board preparation
        self.__prepare_board()
    
    def start_game(self):
        if self.__checkers is not None:
            self.__play = True

    def __robot_handler(self):
        # calibration

        self.__movement_handler.calibrate()

        while not (self.__camera_handler.initialized and self.__movement_handler.calibrated) and self.__run:
            # awaiting submodules calibration
            time.sleep(1)
        
        # main robot loop
        while self.__run:
            time.sleep(.1)
            if self.__play == False:
                # no game to play
                continue
            
            while not self.__checkers.end:
                if self.__checkers.player_turn == self.__ai_player.num:
                    robot_move, _, promoted = self.__ai_player.make_move(self.__checkers)
                    self.__make_move(robot_move, promoted)
                else:
                    player_move = self.__get_player_move()

                    if player_move is not None and self.__checkers.is_move_valid(player_move):
                        self.__player_move_valid = True
                        self.__checkers.make_move(player_move)

                    else:
                        self.__player_move_valid = False
            
            self.__play = False

    def __get_player_move(self):
        timer = None
        board_code = None

        while self.__run:
            board_code, _, _, hand_above_board = self.__camera_handler.read_board()

            if not hand_above_board:
                if timer is None:
                    timer = time.perf_counter()
                elif time.perf_counter() - timer > 1:
                    break

            else:
                timer = None
                
            time.sleep(.1)
        
        if board_code is None:
            return None

        return self.__checkers.calc_move_between_boards(board_code)

    def __make_move(self, move, promoted):
        board_pos = None
        free_figures = None

        while self.__run:
            _, board_pos, free_figures, _ = self.__camera_handler.read_board()

            if np.abs(board_pos[move.src]).sum() > 1.e-5:
                break
                
            time.sleep(.1)

        self.__robot_arm_moving = True
        def interrupt_thread_fun():
            interrupted = False
            while self.__robot_arm_moving and self.__run:
                _, _, _, hand_above_board = self.__camera_handler.read_board()
                if hand_above_board and not interrupted:
                    self.__movement_handler.pause()
                    interrupted = True
                
                if not hand_above_board and interrupted:
                    self.__movement_handler.unpause()
                    interrupted = False

                time.sleep(.1)
        
        interrupt_thread = threading.Thread(target=interrupt_thread_fun)
        interrupt_thread.start()
        
        # move selected figure
        self.__movement_handler.move_pawn_from_pos_to_square(*self.__cam_pos_to_drv_pos(board_pos[move.src]),
                                                             *move.dest)
        # remove taken figures
        for figrure_pos in move.taken_figures:
            free_pos = (30, 30) # self.__camera_handler.find_free_pos_outside_board()
            self.__movement_handler.move_pawn_from_pos_to_pos(*self.__cam_pos_to_drv_pos(board_pos[figrure_pos]),
                                                              *self.__cam_pos_to_drv_pos(free_pos))
        
        # promote pawn
        if promoted:
            free_pos = (30, 30) # self.__camera_handler.find_free_pos_outside_board()
            self.__movement_handler.move_pawn_from_square_to_pos(*move.dest,
                                                                 *self.__cam_pos_to_drv_pos(free_pos))

            if self.__checkers.player_turn == 0:
                queen_pos = free_figures['blue'][0]
            else:
                queen_pos = free_figures['red'][0]

            self.__movement_handler.move_pawn_from_pos_to_square(*self.__cam_pos_to_drv_pos(queen_pos),
                                                                 *move.dest)
        
        # move to corner
        self.__movement_handler.move_to_pos(self.__movement_handler.X_range[1], self.__movement_handler.Y_range[0])

        time.sleep(1)

        while not self.__movement_handler.all_done and self.__run:
            # wait for moves to be done
            time.sleep(.1)

        self.__robot_arm_moving = False
        interrupt_thread.join()
    
    def __prepare_board(self):
        board_code = None
        free_figures = None
        timer = None

        self.__robot_arm_moving = True

        def interrupt_thread_fun():
            interrupted = False
            while self.__robot_arm_moving and self.__run:
                _, _, _, hand_above_board = self.__camera_handler.read_board()
                if hand_above_board and not interrupted:
                    self.__movement_handler.pause()
                    interrupted = True
                
                if not hand_above_board and interrupted:
                    self.__movement_handler.unpause()
                    interrupted = False
                
                time.sleep(.1)
        
        interrupt_thread = threading.Thread(target=interrupt_thread_fun)
        interrupt_thread.start()
        
        # move to corner
        self.__movement_handler.move_to_pos(self.__movement_handler.X_range[1], self.__movement_handler.Y_range[0])

        time.sleep(1)

        while not self.__movement_handler.all_done and self.__run:
            time.sleep(.1)

        while self.__run:
            board_code, _, free_figures, hand_above_board = self.__camera_handler.read_board()
            
            if not hand_above_board:
                if timer is None:
                    timer = time.perf_counter()
                elif time.perf_counter() - timer > 5:
                    break

            else:
                timer = None
            
            time.sleep(.1)
        

        if not self.__run:
            return

        to_move = [[], [], [], []]
        free_figures_indices = [0, 0, 0, 0]

        for x in range(8):
            for y in range(8):
                c = self.__checkers.board[x, y]
                if c != 0 and c != board_code[x, y]:
                    print('__', c)
                    print(camera_config.pawns_code_colors[c])
                    print(free_figures_indices[c - 1])
                    free_figure_pos = free_figures[camera_config.pawns_code_colors[c]][free_figures_indices[c - 1]]
                    to_move[c - 1].append((*self.__cam_pos_to_drv_pos(free_figure_pos), x, y))

                    free_figures_indices[c - 1] += 1

        for l in to_move:
            print(l)
        print()

        for c in range(len(to_move)):
            for f_x, f_y, x, y in to_move[c]:
                self.__movement_handler.move_pawn_from_pos_to_square(f_x, f_y, x, y)
        
        time.sleep(1)

        # move to corner
        self.__movement_handler.move_to_pos(self.__movement_handler.X_range[1], self.__movement_handler.Y_range[0])

        time.sleep(1)
        
        while not self.__movement_handler.all_done and self.__run:
            # wait for moves to be done
            time.sleep(.1)

        self.__robot_arm_moving = False
        interrupt_thread.join()
    
    @staticmethod
    def __cam_pos_to_drv_pos(pos, offset=True):
        return (driver_config.square_size*pos[0], driver_config.square_size*pos[1])
