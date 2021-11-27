import cv2
import time
import os

import camera

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