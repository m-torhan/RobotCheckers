import sys
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '../../../'))

import cv2
import time

import src.robot.computer_vision.camera as camera

cam = camera.CameraHandler()
cam.start()

time.sleep(1)

img = cam.read_frame()

if not os.path.isdir('./imgs'):
    os.mkdir('imgs')

img_files = []
for _, _, files in os.walk('imgs'):
    img_files.extend(files)
    break

img_idx = 0

while os.path.isfile(f'imgs/img_{img_idx}.png'):
    img_idx += 1

cv2.imwrite(f'imgs/img_{img_idx}.png', img)

cam.stop()

print(f'Photo saved to: imgs/img_{img_idx}.png')