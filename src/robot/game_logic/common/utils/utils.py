from src.common.enums.FieldStatus import FieldStatus
from src.common.enums.PlayerEnum import PlayerEnum


class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y


def point_between(origin_x, origin_y, dest_x, dest_y):
    return Point((origin_x + dest_x) // 2, (origin_y + dest_y) // 2)


class Pawn:
    def __init__(self):
        pass


class Field:
    def __init__(self):
        pass


class Move:
    def __init__(self):
        pass


class Player:
    def __init__(self):
        pass


def point_inside_circle(x, y, center_x, center_y, radius):
    return (x - center_x) ** 2 + (y - center_y) ** 2 < radius ** 2


def map_field_to_player(field_status):
    for player in PlayerEnum.list():
        if player.name in field_status.name:
            return player
    return None


def map_pawn_to_player(pawn):
    for player in PlayerEnum.list_names():
        if player in pawn:
            return player
    return None


def map_field_to_pawn_type(pawn):
    for pawn_type in ["REGULAR", "KING"]:
        if pawn_type in pawn:
            return pawn_type
    return None


def map_filed_to_pawn_color(field):
    if field == FieldStatus.PLAYER_1_REGULAR_PAWN:
        return (255, 255, 255), (180, 180, 180)
    if field == FieldStatus.PLAYER_1_KING:
        return (0, 0, 255), (180, 180, 180)
    if field == FieldStatus.PLAYER_2_REGULAR_PAWN:
        return (60, 60, 60), (160, 160, 160)
    if field == FieldStatus.PLAYER_2_KING:
        return (255, 0, 0), (180, 180, 180)
    return None


def point_same_line(start_position, end_position, point_position):
    x_start, y_start = start_position
    x_end, y_end = end_position
    x, y = point_position

    dxc = x - x_start
    dyc = y - y_start

    dxl = x_end - x_start
    dyl = y_end - y_start

    return dxc * dyl == dyc * dxl
