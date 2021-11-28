from rest_framework import serializers

from webserver.checkers.common.start_mode import StartMode


class GameSettingsSerializer(serializers.Serializer):
    difficulty = serializers.IntegerField(required=True, min_value=1, max_value=10)
    start_mode = serializers.ChoiceField(choices=StartMode.list_values(), default=StartMode.ROBOT)
