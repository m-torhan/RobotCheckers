import threading
import random
from time import sleep

from robot.ai import ai_player
from robot.game_logic.checkers import Checkers
from webserver.checkers.common.consts import ROBOT_STARTS_BOARD, PLAYER_STARTS_BOARD
from webserver.checkers.common.game_settings import GameSettings
from webserver.checkers.common.game_status import GameStatus
from webserver.checkers.common.singleton import Singleton
from webserver.checkers.common.start_mode import StartMode
from webserver.checkers.common.user_action import UserAction
from webserver.checkers.common.winner import Winner


@Singleton
class Game:
    def __init__(self):
        self.__consumer = None
        self.__checkers = None
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

    def user_action(self, action):
        if action is UserAction.END_GAME and self.is_game_running():
            self.__run = False
            self.__cleanup_requested = True

    def send_game_board_status(self):
        if self.__checkers is None:
            board = ROBOT_STARTS_BOARD if self.__settings.start_mode == StartMode.ROBOT else PLAYER_STARTS_BOARD
            self.__consumer.group_send_move(board, 0, [], [])
        else:
            all_moves = self.__checkers.all_moves
            if len(all_moves) > 0:
                last_move = self.__checkers.all_moves[-1]
                self.__consumer.group_send_move(self.__checkers.board,
                                                self.__checkers.turn_counter,
                                                last_move.chain,
                                                last_move.taken_figures)
            else:
                self.__consumer.group_send_move(self.__checkers.board,
                                                self.__checkers.turn_counter,
                                                [],
                                                [])

    def __cleanup(self):
        self.__settings.clear_all()
        self.__consumer = None

    def __game_thread(self):
        self.__checkers = Checkers()
        while True:
            if not self.__run:
                sleep(1)
            else:
                if not self.__settings.are_set():
                    print("kupa")
                    raise Exception()

                if self.__settings.start_mode == StartMode.RANDOM:
                    r = random.getrandbits(1)
                    start_states = (int(r == 0), int(r != 0))
                else:
                    start_states = (0 if self.__settings.start_mode == StartMode.PLAYER else 1,
                                    0 if self.__settings.start_mode == StartMode.ROBOT else 1)

                player_1_num, player_2_num = start_states
                # player_1 = ai_player.AIPlayerRandom(player_1_num)
                player_1 = ai_player.AIPlayerMinimax(player_1_num, 2)
                # player_2 = ai_player.AIPlayerRandom(player_2_num)
                player_2 = ai_player.AIPlayerMonteCarlo(player_2_num, 30)
                # player_2 = ai_player.AIPlayerMinimax(player_2_num, 2)

                while not self.__checkers.end and self.__run:
                    sleep(4)

                    if self.__checkers.player_turn == player_1.num:
                        self.__consumer.group_send_game_status(GameStatus.PLAYERS_MOVE_STARTED)
                        _ = player_1.make_move(self.__checkers)

                    elif self.__checkers.player_turn == player_2.num:
                        self.__consumer.group_send_game_status(GameStatus.ROBOTS_MOVE_STARTED)
                        _ = player_2.make_move(self.__checkers)

                    self.send_game_board_status()

                if self.__checkers.end:
                    content = "Koniec gry, "
                    if self.__checkers.winner in Winner.list_values():
                        winner = Winner(self.__checkers.winner)
                        if winner == Winner.DRAW:
                            content += "remis"
                        elif winner == Winner.PLAYER1:
                            content += "wygrał gracz1"
                        elif winner == Winner.PLAYER2:
                            content += "wygrał gracz2"

                    self.__consumer.group_send_game_status(GameStatus.GAME_FINISHED, content)
                    self.__run = False
                if not self.__run:
                    if self.__cleanup_requested:
                        self.__cleanup()
                        self.__cleanup_requested = False
                    self.__checkers = Checkers()
