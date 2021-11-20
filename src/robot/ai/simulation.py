import sys

sys.path.append('../../../')

import os
import pygame
from pygame.locals import *
from time import perf_counter, sleep
import threading
import cv2
import numpy as np

import ai_player
from src.robot.game_logic.model.checkers import Checkers
from src.robot.game_logic.common.enums.player_enum import PlayerEnum
from src.robot.game_logic.model.player.players import Player1, Player2
from src.robot.game_logic.common.enums.field_status import FieldStatus

window_width = 768
window_height = 512

player_1 = ai_player.AIPlayer('random')
player_2 = ai_player.AIPlayer('random')

players = [Player1(), Player2()]
checkers = Checkers()
for player in players:
    checkers.init_fields(player.get_starting_positions(), player.get_regular_pawn())

vid_idx = 0

while os.path.isfile(f'vids/vid_{vid_idx}.avi'):
    vid_idx += 1

out = cv2.VideoWriter(f'vids/vid_{vid_idx}.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (window_width, window_height))

available_moves = None

def game():
    global checkers
    global player_1
    global player_2
    global available_moves
    global run

    selected_pawn = None

    while not checkers.is_end() and run:
        print(f'is_end: {checkers.is_end()}')
        print(f'Player {checkers.player_turn} move')
        if checkers.player_turn == PlayerEnum.PLAYER_1:
            if selected_pawn is not None:
                checkers.calc_available_movements(selected_pawn)
                available_moves = checkers.neighbours
            else:
                available_moves = checkers.calc_available_movements_for_player(checkers.player_turn)

            print(len(available_moves))
            sleep(.25)
            move = player_1.get_next_move(checkers.board_status, available_moves)

        elif checkers.player_turn == PlayerEnum.PLAYER_2:
            if selected_pawn is not None:
                checkers.calc_available_movements(selected_pawn)
                available_moves = checkers.neighbours
            else:
                available_moves = checkers.calc_available_movements_for_player(checkers.player_turn)

            print(len(available_moves))
            sleep(.25)
            move = player_2.get_next_move(checkers.board_status, available_moves)
        
        print(f'move: {move.src} -> {move.dest}')
        checkers.calc_available_movements(move.src)
        checkers.take_action(move.src, move.dest)

        print(len(checkers.neighbours))
        if len(checkers.neighbours) == 0:
            checkers.next_player()
            selected_pawn = None
        
        else:
            selected_pawn = move.dest
        

game_thread = threading.Thread(target=game)

pygame.init()
window = pygame.display.set_mode((window_width, window_height), 0, 32)

pygame.display.set_caption('Pygame template')

def draw_text(text, size, color, surface, position, anchor=''):
    font = pygame.font.SysFont('consolas', size*3//4)
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if anchor == 'bottomleft':
        textrect.bottomleft = position
    elif anchor == 'topleft':
        textrect.topleft = position
    elif anchor == 'bottomright':
        textrect.bottomright = position
    elif anchor == 'topright':
        textrect.topright = position
    else:
        textrect.center = position
    surface.blit(textobj, textrect)

def terminate():
    pygame.quit()
    sys.exit()

time_0 = perf_counter()

clock = pygame.time.Clock()

run = True
while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        
        if event.type == KEYDOWN:
            if event.key == K_s:
                game_thread.start()
            if event.key == K_e:
                run = False
            
    delta_time, time_0 = perf_counter() - time_0, perf_counter()
    
    window.fill((0, 0, 0))
    
    for i in range(checkers.board_status.shape[0]):
        for j in range(checkers.board_status.shape[1]):
            pygame.draw.rect(window, ((192,)*3, (0, 255, 0))[(i + j) % 2], (32*i, 32*j, 32, 32), 0)
            status = checkers.board_status.get_field(i, j)
            col = None
            if status == FieldStatus.PLAYER_1_REGULAR_PAWN:
                col = (255,)*3
            elif status == FieldStatus.PLAYER_2_REGULAR_PAWN:
                col = (0,)*3
            elif status == FieldStatus.PLAYER_1_KING:
                col = (0, 0, 255)
            elif status == FieldStatus.PLAYER_2_KING:
                col = (255, 0, 0)
            if col is not None:
                pygame.draw.circle(window, col, (32*i + 16, 32*j + 16), 10, 0)

    if available_moves is not None:
        for move in available_moves:
            pygame.draw.line(window, (0, 128, 128), np.array(move.src)*32 + 16, np.array(move.dest)*32 + 16, 8)

    pygame.display.update()

    screen = pygame.display.get_surface()
    capture = pygame.surfarray.pixels3d(screen)
    capture = capture.transpose([1, 0, 2])
    capture_bgr = cv2.cvtColor(capture, cv2.COLOR_RGB2BGR)
    out.write(capture_bgr)
    
    clock.tick(30)

out.release()