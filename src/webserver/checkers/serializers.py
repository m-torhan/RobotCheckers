from rest_framework import serializers


class GameSettingsSerializer(serializers.Serializer):
    difficulty = serializers.IntegerField(required=True, min_value=1, max_value=10)
    start_mode = serializers.ChoiceField(choices=['player', 'robot', 'random'], default='random')
