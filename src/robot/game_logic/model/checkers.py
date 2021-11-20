import sys
from typing import Tuple
import numpy as np

sys.path.append('../../../../')

from src.robot.game_logic.model.board.board_status import BoardStatus
from src.robot.game_logic.model.board.move import Move
from src.robot.game_logic.common.enums.field_status import FieldStatus
from src.robot.game_logic.common.constants.consts import *
from src.robot.game_logic.common.enums.player_enum import PlayerEnum
from src.robot.game_logic.common.utils.utils import *

class Checkers(object):
    def __init__(self, board_size=BOARD_SIZE):
        self._end = False
        self.neighbours = []
        self.visited = np.full((board_size, board_size), False, dtype=bool)
        self._board_size = board_size
        self.player_turn = PlayerEnum.PLAYER_1
        self._board_status = BoardStatus(self._board_size)

    @property
    def board_status(self):
        return self._board_status

    @property
    def end(self):
        return self._end

    def is_end(self):
        pawns = (FieldStatus.PLAYER_1_REGULAR_PAWN, FieldStatus.PLAYER_1_KING) if PlayerEnum.PLAYER_1 == self.player_turn else\
                (FieldStatus.PLAYER_2_REGULAR_PAWN, FieldStatus.PLAYER_2_KING)
        
        if np.sum(self._board_status.fields == pawns[0]) + np.sum(self._board_status.fields == pawns[1]) == 0:
            print('is_end TRUE no pawns')
            return True

        any_move_possible = False
        for i in range(self._board_status.shape[0]):
            for j in range(self._board_status.shape[1]):
                if self._board_status.get_field(i, j) in pawns:
                    self.calc_available_movements((i, j))
                    if len(self.neighbours) > 0:
                        any_move_possible = True

        if not any_move_possible:
            print('is_end TRUE no move')
            return True
        
        print('is_end FALSE')
        return False

    def get_board_status(self):
        return self._board_status

    def init_fields(self, fields: Tuple[int, int], status: FieldStatus):
        for x, y in fields:
            self._board_status.set_field(x, y, status)

    def clicked_pawn(self, pos) -> Tuple[int, int] or None:
        mouse_x, mouse_y = pos
        x, y = self.clicked_field(pos)
        middle_point_x = WINDOW_BORDER + BOARD_FIELD_WIDTH*x + BOARD_FIELD_WIDTH/2
        middle_point_y = WINDOW_BORDER + BOARD_FIELD_HEIGHT*y + BOARD_FIELD_HEIGHT/2
        radius = 35

        field_status = self._board_status.get_field(x, y)
        player = map_field_to_player(field_status)

        if player == self.player_turn and \
           point_inside_circle(mouse_x, mouse_y, middle_point_x, middle_point_y, radius):
            return x, y
        return None

    def clicked_field(self, pos) -> Tuple[int, int] or None:
        x, y = pos
        x_temp = x // BOARD_FIELD_WIDTH
        y_temp = y // BOARD_FIELD_HEIGHT
        return x_temp, y_temp

    def is_movement_valid(self, origin_pos, dest_pos, moves=None):
        if moves is None:
            moves = self.neighbours

        for move in moves:
            position = move._dest
            if position == dest_pos:
                return True
            if len(move.next_move) and point_same_line(origin_pos, dest_pos, position):
                return self.is_movement_valid(origin_pos, dest_pos, move.next_move)

        return False

    def take_action(self, origin_pos, destination_pos):
        x_origin, y_origin = origin_pos
        x_dest, y_dest = destination_pos
        pawn = self._board_status.get_field(x_origin, y_origin)

        row_index = 0 if self.player_turn == PlayerEnum.PLAYER_2 else self._board_size - 1
        new_pawn = pawn
        if y_dest == row_index and self.is_field_regular(x_origin, y_origin):
            new_pawn = FieldStatus.PLAYER_2_KING if self.player_turn == PlayerEnum.PLAYER_2 else FieldStatus.PLAYER_1_KING
        self._board_status.set_field(x_dest, y_dest, new_pawn)

        self._board_status.set_field(x_origin, y_origin, FieldStatus.EMPTY_FIELD)

        next_move_available = False
        move_ended = False

        while not move_ended:
            for move in self.neighbours:
                position = move._dest
                move_ended = position == (x_dest, y_dest)
                if move_ended or point_same_line(origin_pos, destination_pos,
                                                 position):
                    for opponent_position in move.pawns_for_taking:
                        x_opponent, y_opponent = opponent_position
                        self._board_status.set_field(x_opponent, y_opponent,
                                                     FieldStatus.EMPTY_FIELD)

                    if len(move.next_move) > 0:
                        self.neighbours = move.next_move
                        next_move_available = True
                        break
                    elif move_ended:
                        next_move_available = False
                        break

            if not next_move_available:
                self.neighbours = []

    def next_player(self):
        self.player_turn = self.opponent_player()

    def calc_available_movements_for_player(self, player):
        pawns = (FieldStatus.PLAYER_1_REGULAR_PAWN, FieldStatus.PLAYER_1_KING) if PlayerEnum.PLAYER_1 == player else\
                (FieldStatus.PLAYER_2_REGULAR_PAWN, FieldStatus.PLAYER_2_KING)

        moves = []
        
        for i in range(self._board_status.shape[0]):
            for j in range(self._board_status.shape[1]):
                if self._board_status.get_field(i, j) in pawns:
                    self.calc_available_movements((i, j))
                    moves.extend(self.neighbours)
        
        return moves

    def calc_available_movements(self, selected_pawn):
        x, y = selected_pawn
        self.neighbours = []
        status = self._board_status.get_field(x, y)
        if status in [FieldStatus.PLAYER_1_REGULAR_PAWN, FieldStatus.PLAYER_2_REGULAR_PAWN]:
            self.calc_available_regular_movements(selected_pawn)
        elif status in [FieldStatus.PLAYER_1_KING, FieldStatus.PLAYER_2_KING]:
            self.calc_available_king_movements(selected_pawn)

    def calc_available_regular_movements(self, selected_pawn, current_move=None):
        if current_move is not None:
            selected_pawn = current_move._dest

        player = self.player_turn

        x, y = selected_pawn

        y_direction = 1 if player == PlayerEnum.PLAYER_1 else -1
        if self._board_status.get_field(x, y) in [FieldStatus.PLAYER_1_REGULAR_PAWN,
                                                  FieldStatus.PLAYER_2_REGULAR_PAWN] or \
                (current_move is not None and self._board_status.get_field(x, y) == FieldStatus.EMPTY_FIELD):
            if self.coordinate_inside(y + 2*y_direction):
                for new_x, new_y in [(x + 2, y + 2*y_direction), (x - 2, y + 2*y_direction)]:
                    middle_point = point_between(x, y, new_x, new_y)
                    if self.coordinate_inside(new_x) and \
                       self.is_field_opponent(middle_point.x, middle_point.y) and \
                       self.is_field_empty(new_x, new_y):

                        move = Move((x, y), (new_x, new_y), [(middle_point.x, middle_point.y)])
                        self.calc_available_regular_movements((new_x, new_y),
                                                              move)
                        if current_move is None:
                            self.neighbours.append(move)
                        else:
                            current_move.add_next_move(move)

            if self.coordinate_inside(y + y_direction) and current_move is None:
                for new_x, new_y in [(x + 1, y + y_direction), (x - 1, y + y_direction)]:
                    if self.coordinate_inside(new_x) and \
                            self.is_field_empty(new_x, new_y):
                        self.neighbours.append(Move((x, y), (new_x, new_y)))

    def calc_available_king_movements(self, selected_pawn,
                                      current_move=None):
        if current_move is None:
            self.visited = np.full((self._board_size, self._board_size), False, dtype=bool)

        x, y = selected_pawn
        self.visited[y, x] = 1

        for y_direction in [-1, 1]:
            for x_direction in [-1, 1]:
                new_y = y
                new_x = x
                pawns_for_taking = []
                next_must_be_empty = False
                while True:
                    new_y += y_direction
                    new_x += x_direction
                    if not self.point_inside_board(new_x, new_y):
                        break  # end of board
                    if self.visited[new_y, new_x]:
                        break  # end of board
                    self.visited[new_y, new_x] = 1
                    if self.is_field_current_player(new_x, new_y):
                        break  # players own pawn
                    if self.is_field_empty(new_x, new_y):
                        next_must_be_empty = False
                        continue_move = len(pawns_for_taking) > 0
                        move = Move((x, y), (new_x, new_y), pawns_for_taking.copy())
                        if continue_move:
                            self.calc_available_king_movements((new_x, new_y), move)
                        if current_move is None:
                            self.neighbours.append(move)  # empty field
                        elif continue_move:
                            current_move.next_move.append(move)
                    elif self.is_field_opponent(new_x, new_y) and not next_must_be_empty:
                        pawns_for_taking.append((new_x, new_y))
                        next_must_be_empty = True

    def opponent_player(self):
        return PlayerEnum.PLAYER_1 if self.player_turn == PlayerEnum.PLAYER_2 else PlayerEnum.PLAYER_2

    def point_inside_board(self, x, y):
        return self.coordinate_inside(x) and self.coordinate_inside(y)

    def coordinate_inside(self, x):
        return self._board_size > x >= 0

    def is_field_opponent(self, x, y):
        return map_field_to_player(self._board_status.get_field(x, y)) == self.opponent_player()

    def is_field_current_player(self, x, y):
        return map_field_to_player(self._board_status.get_field(x, y)) == self.player_turn

    def is_field_empty(self, x, y):
        return self._board_status.get_field(x, y) == FieldStatus.EMPTY_FIELD

    def is_field_regular(self, x, y):
        return self._board_status.get_field(x, y) in [FieldStatus.PLAYER_1_REGULAR_PAWN,
                                                      FieldStatus.PLAYER_2_REGULAR_PAWN]

    def is_field_king(self, x, y):
        return self._board_status.get_field(x, y) in [FieldStatus.PLAYER_1_KING,
                                                      FieldStatus.PLAYER_2_KING]