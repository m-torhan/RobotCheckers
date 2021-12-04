import json

import numpy as np
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from typing import List, Tuple

from webserver.checkers.common.consts import GROUP_NAME
from webserver.checkers.common.game_status import GameStatus
from webserver.checkers.common.user_action import UserAction
from webserver.checkers.common.utils import map_board_to_playable_fields_str
from webserver.checkers.game import Game


class GameConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self._group_name = GROUP_NAME
        self._game: Game = Game.instance()
        self._game.consumer = self

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self._group_name,
            self.channel_name
        )
        self.accept()

        self._game.send_game_board_status()
        self._game.start_game()


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self._group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        self.group_send_message(text_data_json)

    def group_send_game_status(self, status: GameStatus, content: str = ''):
        self.group_send_message(
            {
                'type': 'game_status',
                'message': {
                    'game_status': status.name,
                    'content': content
                }
            }
        )

    def group_send_move(self, board_status: np.ndarray,
                        move_id: int = 0,
                        move_steps: List[Tuple[int, int]] = None,
                        taken_pawns: List[Tuple[int, int]] = None):

        playable_fields_status = board_status if isinstance(board_status, str) and len(board_status) == 32 \
            else map_board_to_playable_fields_str(board_status)

        self.group_send_message(
            {
                'type': 'move',
                'message': {
                    "id": move_id,
                    "new_board_status": playable_fields_status,
                    "move_steps": [{"x": x, "y": y} for (x, y) in move_steps],
                    "taken_pawns": [{"x": x, "y": y} for (x, y) in taken_pawns]
                }
            }
        )

    def group_send_message(self, message: dict):
        async_to_sync(self.channel_layer.group_send)(
            self._group_name, message
        )

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

    # Receive message from group
    def user_action(self, event):
        message_content = event['message']['content']
        if message_content not in UserAction.list_values():
            return

        self._game.user_action(UserAction(message_content))

    def send_message(self, message_type, message_content):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': message_type,
            'message': message_content
        }))
