import time
# import checkersrobot.src.main
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render


def index(request):
    import threading
    t = threading.Thread(target=start_game_process, args=(), kwargs={})
    t.setDaemon(True)
    t.start()

    return render(request, 'checkers/index.html')


def start_game_process():
    print("game started")
    time.sleep(2)
    #main() #game logic main


def test_websocket_process():
    print("websocket message test")
    time.sleep(2)
    channel_layer = get_channel_layer()
    while channel_layer is None:
        channel_layer = get_channel_layer()
    switch = True
    while True:
        switch = not switch
        pawn = 1 if switch else 2
        fields = [pawn] * 32
        async_to_sync(channel_layer.group_send)(
            "checkers_default",
            {
                'type': 'chat_message',
                'message': fields
            }
        )
        time.sleep(1)
