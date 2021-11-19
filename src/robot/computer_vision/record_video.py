import cv2
import time
import os
import sys

import camera

rec_duration = 10

try:
    rec_duration = int(sys.argv[1])
except:
    pass

fps = 20

cam = camera.CameraHandler()
cam.start()

if not os.path.isdir('./vids'):
    os.mkdir('vids')

vid_files = []
for _, _, files in os.walk('vids'):
    vid_files.extend(files)
    break

vid_idx = 0

while os.path.isfile(f'vids/vid_{vid_idx}.avi'):
    vid_idx += 1

out = cv2.VideoWriter(f'vids/vid_{vid_idx}.avi', cv2.VideoWriter_fourcc(*'XVID'), fps, (640,480))

time.sleep(1)

start_time = time.perf_counter()
fps_time = time.perf_counter()

frames = 0
while time.perf_counter() - start_time < rec_duration:
    if fps_time - time.perf_counter() < 1./fps:
        frame = cam.read_frame()

        frame = cv2.flip(frame, 0)

        out.write(frame)

        fps_time += 1./fps
        frames += 1

out.release()
cam.stop()

print(f'Video saved to: vids/vid_{vid_idx}.avi. {frames} frames')