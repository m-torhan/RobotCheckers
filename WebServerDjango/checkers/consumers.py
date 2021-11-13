import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self._room_name = 'default'
        self._room_group_prefix = 'checkers'
        self._room_group_name = f'{self._room_group_prefix}_{self._room_name}'

    def connect(self):
        # #Custom rooms
        # self._room_name = self.scope['url_route']['kwargs']['room_name']
        # self._room_group_name = f'{self._room_group_prefix}_{self._room_name}'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self._room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self._room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self._room_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
