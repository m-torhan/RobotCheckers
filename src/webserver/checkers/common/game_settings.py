from webserver.checkers.common.start_mode import StartMode


class GameSettings:
    __difficulty: int
    __start_mode: StartMode

    def __init__(self):
        self.__difficulty = None
        self.__start_mode = None

    def map_settings_from_dict(self, settings_dict):
        self.__difficulty = settings_dict['difficulty']
        self.__start_mode = StartMode(settings_dict['start_mode'])

    def clear_all(self):
        self.__difficulty = None
        self.__start_mode = None

    def are_set(self) -> bool:
        return self.__difficulty is not None and \
               self.__start_mode is not None

    @property
    def difficulty(self):
        return self.__difficulty

    @property
    def start_mode(self):
        return self.__start_mode
