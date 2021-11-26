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
            
            if self.__checkers.player_turn == self.__ai_player.num:
                robot_move, ret = self.__ai_player.make_move(self.__checkers)

                # here robot should make move

            else:
                pass
                
                # here get and validate player move
    
    def __make_move(self, move):
        pass

    def __promote_pawn(self, pawn_pos):
        pass
