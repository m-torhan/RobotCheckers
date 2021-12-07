from web.apps.checkers.common.start_mode import StartMode
import random

class GameSettings:
    __automatic_pawns_placement_on_start: bool
    __difficulty: int
    __start_mode: StartMode

    def __init__(self):
        self.__automatic_pawns_placement_on_start = None
        self.__difficulty = None
        self.__start_mode = None

    def map_settings_from_dict(self, settings_dict):
        self.__automatic_pawns_placement_on_start = settings_dict['automatic_pawns_placement_on_start']
        self.__difficulty = settings_dict['difficulty']
        if StartMode(settings_dict['start_mode']) == StartMode.RANDOM:
            r = random.getrandbits(1)
            self.__start_mode = StartMode.ROBOT if r == 0 else StartMode.PLAYER
        else:
            self.__start_mode = StartMode(settings_dict['start_mode'])

    def clear_all(self):
        self.__automatic_pawns_placement_on_start = None
        self.__difficulty = None
        self.__start_mode = None

    def are_set(self) -> bool:
        return self.__difficulty is not None and \
               self.__start_mode is not None and \
               self.__automatic_pawns_placement_on_start is not None

    @property
    def automatic_pawns_placement_on_start(self):
        return self.__automatic_pawns_placement_on_start

    @property
    def difficulty(self):
        return self.__difficulty

    @property
    def start_mode(self):
        return self.__start_mode
