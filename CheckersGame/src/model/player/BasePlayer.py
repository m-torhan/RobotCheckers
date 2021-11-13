class BasePlayer:
    def __init__(self):
        pass

    def get_starting_positions(self):
        raise NotImplementedError

    def get_regular_pawn(self):
        raise NotImplementedError

    def get_king_pawn(self):
        raise NotImplementedError
