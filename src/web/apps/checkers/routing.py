from django.urls import re_path

from . import game_consumer

websocket_urlpatterns = [
    re_path(r'ws/checkers/(?P<room_name>\w+)/$', game_consumer.GameConsumer.as_asgi()),
]
