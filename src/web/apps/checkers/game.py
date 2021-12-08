import threading
import random
from time import sleep

from robot.robot import RobotCheckers
from web.apps.checkers.common.consts import ROBOT_STARTS_BOARD, PLAYER_STARTS_BOARD
from web.apps.checkers.common.game_settings import GameSettings
from web.apps.checkers.common.game_status import GameStatus
from web.apps.checkers.common.singleton import Singleton
from web.apps.checkers.common.start_mode import StartMode
from web.apps.checkers.common.user_action import UserAction
from web.apps.checkers.common.winner import Winner


@Singleton
class Game:
    def __init__(self):
        self.__consumer = None
        self.__robot = RobotCheckers()
        self.__settings = GameSettings()
        self.__run = False
        self.__cleanup_requested = False
        self.__thread = threading.Thread(target=self.__game_thread)
        self.__thread.start()

    @property
    def settings(self):
        return self.__settings

    @settings.setter
    def settings(self, settings_dict):
        if not self.__settings.are_set():
            self.__settings.map_settings_from_dict(settings_dict)

    @property
    def consumer(self):
        return self.__consumer

    @consumer.setter
    def consumer(self, value):
        if self.__consumer is None:
            self.__consumer = value

    def start_game(self):
        if not self.is_game_running():
            self.__run = True

    def is_game_running(self):
        return self.__run

    def is_consumer_set(self):
        return self.__consumer is not None

    def user_action(self, action):
        if action is UserAction.END_GAME and self.is_game_running():
            self.__run = False
            self.__cleanup_requested = True

    def send_game_board_status(self):
        if self.is_consumer_set():
            if self.__robot is None or self.__robot.board_from_checkers is None:
                board = ROBOT_STARTS_BOARD if self.__settings.start_mode == StartMode.ROBOT else PLAYER_STARTS_BOARD
                self.__consumer.group_send_move(board, 0, [], [])
            else:
                all_moves = self.__robot.all_moves
                if all_moves is not None and len(all_moves) > 0:
                    last_move = self.__robot.all_moves[-1]
                    self.__consumer.group_send_move(self.__robot.board_from_checkers,
                                                    self.__robot.turn_counter,
                                                    last_move.chain,
                                                    last_move.taken_figures)
                else:
                    self.__consumer.group_send_move(self.__robot.board_from_checkers,
                                                    self.__robot.turn_counter,
                                                    [],
                                                    [])

    def send_game_status(self, game_status: GameStatus, content: str = ''):
        if self.is_consumer_set():
            self.__consumer.group_send_game_status(game_status, game_status.name) #debug game_status.name, else content

    def __cleanup(self):
        self.__settings.clear_all()
        self.__consumer = None

    def __game_thread(self):
        self.__robot.start()
        try_counter = 0
        while True:
            if self.__robot.calibrated:
                break
            else:
                try_counter += 1
                if try_counter % 10 == 0:
                    self.send_game_status(GameStatus.BOARD_COULD_NOT_BE_CALIBRATED_BY_CV)
                sleep(0.5)
        self.send_game_status(GameStatus.CALIBRATION_FINISHED)

        while True:
            if not self.__run:
                sleep(1)
            else:
                self.send_game_status(GameStatus.BOARD_PREPARATION_STARTED)
                self.send_game_board_status()
                self.__robot.initialize_game(0 if self.__settings.start_mode == StartMode.ROBOT else 1,
                                             self.__settings.difficulty,
                                             self.__settings.automatic_pawns_placement_on_start)
                self.send_game_status(GameStatus.BOARD_PREPARATION_FINISHED)

                self.send_game_status(
                    GameStatus.PLAYERS_MOVE_STARTED if self.__settings.start_mode == StartMode.PLAYER else
                    GameStatus.ROBOTS_MOVE_STARTED
                )

                turn_ctr = self.__robot.turn_counter
                self.__robot.start_game()

                while not self.__robot.checkers_end and self.__run:
                    if self.__robot.turn_counter != turn_ctr and self.__robot.move_done:
                        turn_ctr = self.__robot.turn_counter
                        self.send_game_board_status()
                        sleep(1)
                        self.send_game_status(
                            GameStatus.PLAYERS_MOVE_STARTED if self.__robot.player_turn else
                            GameStatus.ROBOTS_MOVE_STARTED
                        )
                    sleep(.1)

                if self.__robot.checkers_end:
                    content = "Koniec gry, "
                    if self.__robot.winner in Winner.list_values():
                        winner = Winner(self.__robot.winner)
                        if winner == Winner.DRAW:
                            content += "remis"
                        elif winner == Winner.PLAYER1:
                            content += "wygrał gracz1"
                        elif winner == Winner.PLAYER2:
                            content += "wygrał gracz2"
                    self.__robot.abort_game()
                    self.send_game_status(GameStatus.GAME_FINISHED, content)
                    self.__run = False
                if not self.__run:
                    if self.__cleanup_requested:
                        self.__cleanup()
                        self.__cleanup_requested = False
                    # self.__robot.new_game()?
