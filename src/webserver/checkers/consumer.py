import json
import threading
import time

import numpy as np
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer

from checkers.common.consts import GROUP_NAME
from checkers.common.game_status import GameStatus


class GameConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self._group_name = GROUP_NAME
        self._game_thread = None

    def game(self, settings):
        channel_layer = get_channel_layer()
        while channel_layer is None or self._group_name not in channel_layer.groups:
            channel_layer = get_channel_layer()
        end = False

        # trzeba by wysłać pierwszy game board
        for game_status in [GameStatus.BOARD_PREPARATION_STARTED,
                            GameStatus.BOARD_PREPARATION_ENDED,
                            GameStatus.READY_TO_PLAY]:

            self.group_send_game_status(game_status)
            time.sleep(1)

        PLAYER_STARTS_BOARD = "33333333333300000000111111111111"
        ROBOT_STARTS_BOARD = "11111111111100000000333333333333"

        # inicjalne wysłanie planszy
        move = {
                "id": -1,
                "new_board_status" : ROBOT_STARTS_BOARD,
                "move_steps": [],
                "taken_pawns": []
            }
        self.group_send_move(move)
        time.sleep(1)

        board_statuses = [  # porozdzielane rzędami dla czytelności podczas testowania
            "1111"+"1111"+"0111"+"1000"+"0000"+"3333"+"3333"+"3333",
            "1111"+"1111"+"0111"+"1000"+"3000"+"0333"+"3333"+"3333",
            "1111"+"1111"+"0011"+"1100"+"3000"+"0333"+"3333"+"3333",
            "1111"+"1111"+"0311"+"1000"+"0000"+"0333"+"3333"+"3333",
            ]

        moves = [
            [{"x": 1, "y": 2}, {"x": 0, "y": 3}],
            [{"x": 0, "y": 5}, {"x": 1, "y": 4}],
            [{"x": 3, "y": 2}, {"x": 2, "y": 3}],
            [{"x": 1, "y": 4}, {"x": 3, "y": 2}],
            ]

        taken_pawns = [[],[],[],[{"x": 2, "y": 3}]]

        move_ctr = 0
        while not end:
            status = GameStatus.ROBOTS_MOVE_STARTED if move_ctr % 2 == 0 else GameStatus.PLAYERS_MOVE_STARTED
            self.group_send_game_status(status)
            time.sleep(0.5)
            move = {
                "id": move_ctr,
                "new_board_status" : board_statuses[move_ctr],
                "move_steps": moves[move_ctr],
                "taken_pawns": taken_pawns[move_ctr]
            }
            self.group_send_move(move)
            time.sleep(3)

            move_ctr += 1
            end = move_ctr == 4
        self.group_send_game_status(game_status.GAME_FINISHED)

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self._group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self._group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.group_send_message(message)

    def group_send_game_status(self, status: GameStatus):
        self.group_send_message(
            {
                'type': 'game_status',
                'message': {'game_status': status.name}
            }
        )

    def group_send_move(self, move: dict):
        self.group_send_message(
            {
                'type': 'move',
                'message': move
            }
        )

    def group_send_message(self, message: dict):
        async_to_sync(self.channel_layer.group_send)(
            self._group_name, message
        )

    # Receive message from group
    def settings(self, event):
        message_content = event['message']
        if self._game_thread is None or not self._game_thread.is_alive():
            self._game_thread = threading.Thread(target=self.game, args=(message_content,),
                                                 kwargs={})
            self._game_thread.start()

    # Receive message from group
    def game_status(self, event):
        message_type = event['type']
        message_content = event['message']
        self.send_message(message_type, message_content)

    # Receive message from group
    def move(self, event):
        message_type = event['type']
        message_content = event['message']
        self.send_message(message_type, message_content)

    def send_message(self, message_type, message_content):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': message_type,
            'message': message_content
        }))
