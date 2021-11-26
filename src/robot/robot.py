import threading
import numpy as np

from ai.ai_player import *
from computer_vision.camera import CameraHandler
from game_logic.checkers import Checkers, Move
from movement.driver import MovementHandler

class RobotCheckers(object):
    def __init__(self):
        self.__movement_handler = MovementHandler()
        self.__camera_handler = CameraHandler()
        self.__robot_thread = threading.Thread(target=self.__robot_handler)

        self.__checkers = None
        self.__ai_player = None
        self.__play = False

        self.__calibrated = False
        self.__robot_arm_moving = False
        self.__run = True
    
    @property
    def calibrated(self):
        return self.__calibrated
    
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
    
    def start(self):
        self.__movement_handler.start()
        self.__camera_handler.start()
    
        self.__robot_thread.start()
    
    def stop(self):
        self.__camera_handler.stop()
        self.__movement_handler.stop()

        self.__run = False

        self.__robot_handler.join()

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
    
    def start_game(self):
        self.__play = True

    def __robot_handler(self):
        # calibration

        self.__movement_handler.calibrate()

        while not (self.__camera_handler.initialized and self.__movement_handler.calibrated):
            # awaiting submodules calibration
            pass
        
        # main robot loop
        while self.__run:
            if self.__play == False:
                # no game to play
                continue
            
            while not self.__checkers.end:
                if self.__checkers.player_turn == self.__ai_player.num:
                    robot_move, _, promoted = self.__ai_player.make_move(self.__checkers)
                    self.__make_move(robot_move, promoted)

                else:
                    player_move = self.__get_player_move()
                    
                    if self.__checkers.is_move_valid(player_move):
                        self.__checkers.make_move(player_move)

                    else:
                        # invalid move
                        pass
    
    def __get_player_move(self):
        board_code, _, _, _ = self.__camera_handler.read_board()

        return self.__checkers.calc_move_between_boards(board_code)

    def __make_move(self, move, promoted):
        _, board_pos, free_pawns, _ = self.__camera_handler.read_board()

        self.__robot_arm_moving = True
        def interrupt_thread_fun():
            interrupted = False
            while self.__robot_arm_moving:
                _, _, _, hand_above_board = self.__camera_handler.read_board()
                if hand_above_board and not interrupted:
                    #self.__movement_handler.interrupt()
                    interrupted = True
                
                if not hand_above_board and interrupted:
                    #self.__movement_handler.continue()
                    interrupted = False
        
        interrupt_thread = threading.Thread(target=interrupt_thread_fun)
        interrupt_thread.start()

        # move selected figure
        self.__movement_handler.move_pawn_from_pos_to_pos(board_pos[move.src], board_pos[move.dest])

        # remove taken figures
        for figrure_pos in move.taken_figure:
            new_pos = (30, 30) # self.__camera_handler.find_free_pos_outside_board()
            self.__movement_handler.move_pawn_from_pos_to_pos(board_pos[figrure_pos], new_pos)
        
        # promote pawn
        if promoted:
            new_pos = (30, 30) # self.__camera_handler.find_free_pos_outside_board()
            self.__movement_handler.move_pawn_from_pos_to_pos(board_pos[move.dest], new_pos)

            if self.__ai_player.num == 0:
                queen_pos = free_pawns['blue'][0]
            else:
                queen_pos = free_pawns['red'][0]

            self.__movement_handler.move_pawn_from_pos_to_pos(queen_pos, board_pos[move.dest])
        
        while not self.__movement_handler.all_done:
            # wait for moves to be done
            pass

        self.__robot_arm_moving = False
        interrupt_thread.join()
