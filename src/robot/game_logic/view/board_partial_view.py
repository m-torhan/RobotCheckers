import pygame
import sys

sys.path.append('../../../../')

from src.robot.game_logic.common.constants.consts import *
from src.robot.game_logic.common.utils.utils import *
from src.robot.game_logic.view.view import View

class BoardPartialView(View):
    def __init__(self):
        self._display = None
        self._board_size = BOARD_SIZE

    def init(self):
        pygame.init()
        pygame.display.set_caption('checkers')

        self._display = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)

        self._display.fill(WHITE)

    def draw(self, board_status):
        _x, _y, _w, _h = 0, 0, WIDTH, HEIGHT
        pygame.draw.rect(self._display, RED, (_x, _y, _w, _h), WINDOW_BORDER, border_radius=1)

        self.draw_grid()
        self.draw_pawns(board_status)

    def draw_pawns(self, board_status):
        for x in range(self._board_size):
            for y in range(self._board_size):
                field_status = board_status.get_field(x, y)
                player = map_field_to_player(field_status)
                if player is None:
                    continue
                pawn_color = map_filed_to_pawn_color(field_status)
                self.draw_pawn(pawn_color, x, y)

    def draw_grid(self):
        for x in range(self._board_size):
            for y in range(self._board_size):
                self.draw_field_border(x, y)
                self.draw_field(x, y)

    def draw_field_border(self, x, y):
        pygame.draw.rect(self._display, BOARD_FIELD_BORDER_COLOR, (
            WINDOW_BORDER + BOARD_FIELD_WIDTH * x,
            WINDOW_BORDER + BOARD_FIELD_HEIGHT * y,
            BOARD_FIELD_WIDTH,
            BOARD_FIELD_HEIGHT,
        ))

    def draw_field(self, x, y):
        pygame.draw.rect(self._display,
                         BOARD_0_FIELD_COLOR if (x + y) % 2 == 1 else BOARD_1_FIELD_COLOR,
                         (
                             WINDOW_BORDER + BOARD_FIELD_WIDTH * x + BOARD_BORDER,
                             WINDOW_BORDER + BOARD_FIELD_HEIGHT * y + BOARD_BORDER,
                             BOARD_FIELD_WIDTH - 2 * BOARD_BORDER,
                             BOARD_FIELD_WIDTH - 2 * BOARD_BORDER,
                         ))

    def redraw(self):
        pass

    def draw_available_moves(self, origin_pos, neighbours):
        for move in neighbours:
            position = move.get_position()
            x, y = position
            self.draw_dot(x, y)
            moves = move.next_move
            while len(moves) > 0:
                next_depth = False
                for inner_move in moves:
                    destination_pos = inner_move.get_position()
                    inner_x, inner_y = destination_pos
                    if point_same_line(origin_pos, destination_pos, position):
                        self.draw_dot(inner_x, inner_y)
                        moves = inner_move.next_move
                        next_depth = True
                        break
                if not next_depth:
                    moves = []

    # ___________________________
    # def draw_square(self):
    # def draw_pawn(self):

    def draw_pawn(self, colors, x, y):
        pawn_color, pawn_shadow_color = colors
        middle_point_x = WINDOW_BORDER + BOARD_FIELD_WIDTH * x + BOARD_FIELD_WIDTH / 2
        middle_point_y = WINDOW_BORDER + BOARD_FIELD_HEIGHT * y + BOARD_FIELD_HEIGHT / 2
        pygame.draw.circle(self._display, pawn_shadow_color, (middle_point_x + 3, middle_point_y + 3), 35)
        pygame.draw.circle(self._display, pawn_color, (middle_point_x, middle_point_y), 35)

    def draw_dot(self, x, y):
        middle_point_x = WINDOW_BORDER + BOARD_FIELD_WIDTH * x + BOARD_FIELD_WIDTH / 2
        middle_point_y = WINDOW_BORDER + BOARD_FIELD_HEIGHT * y + BOARD_FIELD_HEIGHT / 2
        pygame.draw.circle(self._display, (100, 0, 100), (middle_point_x, middle_point_y), 10)
