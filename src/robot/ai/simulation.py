import sys

sys.path.append('../../../')

import os
import pygame
from pygame.locals import *
from time import perf_counter, sleep
import threading
import cv2
import numpy as np
import random

import ai_player
from src.robot.game_logic.checkers import Checkers

rec_vid = False
if '-v' in sys.argv:
    rec_vid = True

window_width = 512
window_height = 256

board = np.array([[0,0,0,1,0,0,0,0],
                  [0,0,0,0,3,0,0,0],
                  [0,0,0,0,0,0,0,0],
                  [0,0,0,0,3,0,0,0],
                  [0,0,0,0,0,0,0,0],
                  [0,0,0,0,3,0,0,0],
                  [0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0]], dtype=np.uint8).transpose(1, 0)

checkers = Checkers()

if rec_vid:
    vid_idx = 0

    while os.path.isfile(f'vids/vid_{vid_idx}.avi'):
        vid_idx += 1

    out = cv2.VideoWriter(f'vids/vid_{vid_idx}.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (window_width, window_height))

available_moves = None
score = [0, 0]

def game():
    global checkers
    global available_moves
    global run
    global score

    while run:

        checkers = Checkers()
        r = random.getrandbits(1)
        player_1_num = int(r == 0)
        player_2_num = int(r != 0)
        #player_1 = ai_player.AIPlayerRandom(player_1_num)
        player_1 = ai_player.AIPlayerMinimax(player_1_num, 3)
        player_2 = ai_player.AIPlayerRandom(player_2_num)
        #player_2 = ai_player.AIPlayerMonteCarlo(player_2_num, 30)
        #player_2 = ai_player.AIPlayerMinimax(player_2_num, 5)

        while not checkers.end and run:
            available_moves = checkers.calc_available_moves_for_player(checkers.player_turn)

            if checkers.player_turn == player_1.num:
                move, ret = player_1.make_move(checkers)

            elif checkers.player_turn == player_2.num:
                move, ret = player_2.make_move(checkers)
            
        if checkers.winner == player_1_num:
            score[0] += 1
        else:
            score[1] += 1

game_thread = threading.Thread(target=game)
thread_started = False

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
            if event.key == K_s and not thread_started:
                game_thread.start()
                thread_started = True

            if event.key == K_e:
                run = False
            
    delta_time, time_0 = perf_counter() - time_0, perf_counter()
    
    window.fill((0, 0, 0))
    
    for i in range(checkers.board.shape[0]):
        for j in range(checkers.board.shape[1]):
            pygame.draw.rect(window, ((192,)*3, (0, 192, 0))[(i + j) % 2], (32*i, 32*j, 32, 32), 0)
            square = checkers.board[i,j]
            col = None
            if square == 1:
                col = (255,)*3
            elif square == 3:
                col = (0,)*3
            elif square == 2:
                col = (0, 0, 255)
            elif square == 4:
                col = (255, 0, 0)
            if col is not None:
                pygame.draw.circle(window, col, (32*i + 16, 32*j + 16), 10, 0)

    if available_moves is not None:
        for move in available_moves:
            for i in range(len(move.chain) - 1):
                pygame.draw.line(window, (0, 128, 128), np.array(move.chain[i])*32 + 16, np.array(move.chain[i + 1])*32 + 16, 8)

    draw_text(f'{score}', 32, (255,)*3, window, (384, 128))

    pygame.display.update()

    if rec_vid:
        screen = pygame.display.get_surface()
        capture = pygame.surfarray.pixels3d(screen)
        capture = capture.transpose([1, 0, 2])
        capture_bgr = cv2.cvtColor(capture, cv2.COLOR_RGB2BGR)
        out.write(capture_bgr)
        del capture
    
    clock.tick(30)

if rec_vid:
    out.release()