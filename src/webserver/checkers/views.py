import json
import urllib.parse

from django.http import JsonResponse
from django.shortcuts import render, redirect

from webserver.checkers.game import Game
from webserver.checkers.serializers import GameSettingsSerializer

settings_thread = None


def index(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Expected GET request'})
    return render(request, 'checkers/index.html')


def game(request):
    if not Game.instance().settings.are_set():
        return redirect('index')

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

    game_instance = Game.instance()
    if game_instance.settings.are_set():
        return redirect_params('index', {'status': 'settings-already-set'})

    game_instance.settings.map_settings_from_dict(serializer.validated_data)
    return redirect('game')


def redirect_params(url, params=None):
    response = redirect(url)
    if params:
        query_string = urllib.parse.urlencode(params)
        response['Location'] += '?' + query_string
    return response
