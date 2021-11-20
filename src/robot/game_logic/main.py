# TODO turn priority
# TODO loop taking (return on the same field as started should be available from both sites) e.g (diamond)
# TODO when game ends
# TODO prepare gui the same as in figma
__package__

import sys
import pygame
import os
import inspect

from src.robot.game_logic.model.checkers import Checkers
from src.robot.game_logic.model.player.players import Player1, Player2
from src.robot.game_logic.view.board_partial_view import BoardPartialView

def main():
    board_view = BoardPartialView()
    board_view.init()

    players = [Player1(), Player2()]
    checkers = Checkers()
    for player in players:
        checkers.init_fields(player.get_starting_positions(), player.get_regular_pawn())
    selected_pawn = None

    board_status = checkers.get_board_status()
    board_view.draw(board_status)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()

                if selected_pawn is None:
                    selected_pawn = checkers.clicked_pawn(pos)
                    if selected_pawn is not None:
                        print(f"Pawn {selected_pawn} selected for move")
                        checkers.calc_available_movements(selected_pawn)
                        neighbours = checkers.neighbours
                        board_view.draw_available_moves(selected_pawn, neighbours)

                else:
                    selected_field = checkers.clicked_field(pos)
                    if checkers.is_movement_valid(selected_pawn, selected_field):
                        checkers.take_action(selected_pawn, selected_field)
                        board_status = checkers.get_board_status()
                        board_view.draw(board_status)
                        if len(checkers.neighbours) > 0:
                            neighbours = checkers.neighbours
                            board_view.draw_available_moves(selected_pawn, neighbours)
                            selected_pawn = selected_field
                        else:
                            selected_pawn = None
                            checkers.next_player()

        pygame.display.update()


if __name__ == "__main__":
    main()
