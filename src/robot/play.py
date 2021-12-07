import sys
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '../'))
sys.path.append(os.path.join(dir_path, './'))

import random
from time import sleep

from robot import RobotCheckers

level = 6
if len(sys.argv) > 1:
    try:
        level = int(sys.argv[1])
    except:
        pass

robotCheckers = RobotCheckers()
robotCheckers.start()

while not robotCheckers.calibrated:
    sleep(.1)

print('Robot calibrated')

robot_num = int(random.getrandbits(1) == 0)
robotCheckers.initialize_game(robot_num, level, False)
print(f'Game iniitialized, level={level}')

robotCheckers.start_game()
print('Game started')

while not robotCheckers.checkers_end:
    sleep(.1)

print(('Player', 'Robot')[robotCheckers.winner == robot_num] + ' won!')