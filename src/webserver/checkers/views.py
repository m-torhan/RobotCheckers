import json
import threading
import time
import urllib.parse

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.shortcuts import render, redirect

from checkers.common.consts import GROUP_NAME
from checkers.serializers import GameSettingsSerializer

settings_thread = None


def index(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Expected GET request'})
    return render(request, 'checkers/index.html')


def game(request):
    return render(request, 'checkers/game.html')


def settings(request):
    global settings_thread
    if request.method != "POST":
        return redirect_params('index', {'status': 'invalid-request'})
    try:
        json_response = json.loads(request.body)
    except:
        return redirect_params('index', {'status': 'settings-invalid-structure'})
    serializer = GameSettingsSerializer(data=json_response)
    if not serializer.is_valid():
        return redirect_params('index', {'status': 'settings-validation-failed'})


    if settings_thread is not None and settings_thread.is_alive():

        return redirect_params('index', {'status': 'settings-already-set'})

    settings_thread = threading.Thread(target=channel_send_settings, args=(serializer.validated_data,),
                                       kwargs={})
    settings_thread.start()
    return redirect('game')


def channel_send_settings(game_settings: dict):
    max_tries = 10
    group_exists = False

    while True:
        channel_layer = get_channel_layer()
        if channel_layer is not None and GROUP_NAME in channel_layer.groups:
            group_exists = True
            break

        if max_tries == 0:
            break

        time.sleep(1)
        max_tries -= 1

    if group_exists:
        async_to_sync(channel_layer.group_send)(
            GROUP_NAME,
            {
                'type': 'settings',
                'message': game_settings
            }
        )


def redirect_params(url, params=None):
    response = redirect(url)
    if params:
        query_string = urllib.parse.urlencode(params)
        response['Location'] += '?' + query_string
    return response
