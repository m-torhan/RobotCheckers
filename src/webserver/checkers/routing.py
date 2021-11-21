from django.urls import re_path

from . import consumer

websocket_urlpatterns = [
    re_path(r'ws/checkers/(?P<room_name>\w+)/$', consumer.GameConsumer.as_asgi()),
]
