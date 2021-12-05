import sys
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '../../../'))

import numpy as np
import cv2
import threading
import time
import random
import socket
import pickle
import struct

import src.robot.computer_vision.camera_config as camera_config

class CameraHandler(object):
    def __init__(self, debug_mode=0):
        self.__debug_mode = debug_mode
        self.__cam = cv2.VideoCapture(0)
        self.__frame = None
        self.__warpPerspectiveMatrix = None
        self.__run = True
        self.__cam_thread = threading.Thread(target=self.__cam_handler)
        self.__debug_thread = threading.Thread(target=self.__stream_handler)
        self.__debug_out = None
        self.__debug_frame = None

        # square size in pixels
        self.__sq_side = 64
        sq_side_cm = camera_config.board_size[0]//8
        px_per_cm = self.__sq_side//sq_side_cm

        # figures and hand colors
        self.__colors = {
            'white': (255,)*3,
            'blue' : (1, 1, 255),
            'black': (1,)*3,
            'red'  : (255, 1, 1),
            'hand' : (255, 255, 1)
        }

        self.__colors_hsv_ranges = {
            'white': (np.array((  0,   0, 160), dtype=np.uint8),
                      np.array((255,  55, 255), dtype=np.uint8)),
            'blue':  (np.array(( 90,  90,  50), dtype=np.uint8),
                      np.array((120, 255, 255), dtype=np.uint8)),
            'black': (np.array((  0,   0,   0), dtype=np.uint8),
                      np.array((255, 255,  50), dtype=np.uint8)),
            'red':   (np.array((160,  90,  80), dtype=np.uint8),
                      np.array(( 30, 255, 255), dtype=np.uint8)),
            'hand':  (np.array((180,  40, 100), dtype=np.uint8),
                      np.array(( 30, 100, 220), dtype=np.uint8))
        }

        # gamearea and board positions
        x_min = px_per_cm*(camera_config.gamearea_size[0] - camera_config.board_size[0]) + self.__sq_side//2
        y_min = self.__sq_side//2
        xy_delta = self.__sq_side*8
        x_max = x_min + xy_delta
        y_max = y_min + xy_delta

        self.__board_range = [
            [x_min, x_max],
            [y_min, y_max]
        ]
        self.__gamearea_range = [
            [x_max - (x_max - x_min)*camera_config.gamearea_size[0]//camera_config.board_size[0], x_max],
            [y_min, y_min + (y_max - y_min)*camera_config.gamearea_size[1]//camera_config.board_size[1]]
        ]

        self.__bottom_right_corner = (x_max + xy_delta//8, y_max + xy_delta//8)

        # kernel used in free space detection
        kernel_diameter = self.__sq_side*5//4
        self.__kernel = np.zeros((kernel_diameter,)*2)

        for x in range(kernel_diameter):
            for y in range(kernel_diameter):
                if (x - kernel_diameter/2)**2 + (y - kernel_diameter/2)**2 <= (kernel_diameter/2)**2:
                    self.__kernel[x,y] = 1

        self.__kernel /= np.sum(self.__kernel)

        # board size in pixels
        self.__out_width = self.__sq_side*8*camera_config.gamearea_size[0]//camera_config.board_size[0] + self.__sq_side
        self.__out_height = self.__sq_side*8*camera_config.gamearea_size[1]//camera_config.board_size[1] + self.__sq_side
    
    @property
    def initialized(self):
        return self.__warpPerspectiveMatrix is not None
    
    def start(self):
        self.__cam_thread.start()
        
        if 1 == self.__debug_mode:
            vid_idx = 0

            while os.path.isfile(f'debug_vid_{vid_idx}.avi'):
                vid_idx += 1

            self.__debug_out = cv2.VideoWriter(f'debug_vid_{vid_idx}.avi', cv2.VideoWriter_fourcc(*'XVID'), 2, (640, 480))
        
        elif 2 == self.__debug_mode:
            self.__debug_thread.start()
        
    def stop(self):
        if 1 == self.__debug_mode:
            self.__debug_out.release()

        self.__run = False
        self.__cam_thread.join()
        
        if 2 == self.__debug_mode:
            self.__debug_thread.join()

        self.__cam.release()

        self.__warpPerspectiveMatrix = None

    def read_frame(self):
        if self.__frame is not None:
            return self.__frame.copy()
        else:
            return None
        
    def read_debug_frame(self):
        if self.__debug_frame is not None:
            return self.__debug_frame.copy()
    
    def read_board(self):
        objects_positions = self.__detect_objects_positions()
        
        if objects_positions is None:
            return None

        board_code = np.zeros((8, 8), dtype=np.uint8)
        board_pos = np.zeros((8, 8, 2), dtype=np.float64)

        free_figures = {}

        for color, code in camera_config.pawns_colors_code.items():
            free_figures[color] = []
            for x, y in objects_positions[color]:
                pawn_on_board = False
                if -.25 <= x <= 8.25 and\
                   -.25 <= y <= 8.25:
                    for i in range(max(0, int(x) - 1), min(8, int(x) + 2)):
                        for j in range(max(0, int(y) - 1), min(8, int(y) + 2)):
                            if (i + j) % 2 == 1:
                                # check only + pattern
                                if i != int(x) and j != int(y):
                                    continue
                                # calculate distance from square center
                                if (x - (i + .5))**2 + (y - (j + .5))**2 < 1/2:
                                    pawn_on_board = True
                                    board_code[i, j] = code
                                    board_pos[i, j, 0] = x
                                    board_pos[i, j, 1] = y
                               
                if not pawn_on_board:
                    free_figures[color].append((x, y))

        return board_code, board_pos, free_figures, len(objects_positions['hand']) > 0
    
    def find_free_pos_outside_board(self, debug=False):
        frame_filtered_colors, frame_perp_crop = self.__fiter_frame_by_colors()

        if frame_filtered_colors is None:
            return None

        free_area_mask = np.ones_like(frame_perp_crop[:,:,0])

        for _, img in frame_filtered_colors.items():
            free_area_mask[img > 0] = 0

        free_area_mask[self.__board_range[1][0]:self.__board_range[1][1],
                       self.__board_range[0][0]:self.__board_range[0][1]] = 0

        gamearea_mask = np.zeros_like(free_area_mask)
        gamearea_mask[self.__gamearea_range[1][0]:self.__gamearea_range[1][1],
                      self.__gamearea_range[0][0]:self.__gamearea_range[0][1]] = 1

        free_area_mask[gamearea_mask == 0] = 0

        temp = free_area_mask.astype(np.float64)

        temp = 1 - temp
        temp = cv2.filter2D(temp, -1, self.__kernel)
        temp = 1 - temp
        temp -= temp.min()
        temp /= temp.max()

        free_area_mask_bold = temp > .999

        free_area_mask_grad = cv2.filter2D(free_area_mask_bold.astype(np.float64), -1, self.__kernel)

        free_area_mask_grad = 1 - free_area_mask_grad
        free_area_mask_grad -= free_area_mask_grad.min()
        free_area_mask_grad /= free_area_mask_grad.max()

        free_area_mask_grad[free_area_mask_bold == 0] = 0

        if (free_area_mask_grad > .7).sum() == 0:
            return None

        w = np.where(free_area_mask_grad > .7)
        i = random.randint(0, w[0].shape[0] - 1)

        x = self.__bottom_right_corner[0] - w[1][i]/self.__sq_side
        y = self.__bottom_right_corner[1] - w[0][i]/self.__sq_side
        
        if debug or 0 != self.__debug_mode:
            free_area_mask_grad_rgb = cv2.cvtColor((255*free_area_mask_grad).astype(np.uint8), cv2.COLOR_GRAY2BGR)
            free_area_mask_grad_rgb = cv2.circle(free_area_mask_grad_rgb, (w[1][i], w[0][i]), self.__sq_side//4, (0, 255, 0), -1)
            free_area_mask_grad_unperp = cv2.warpPerspective(free_area_mask_grad_rgb, self.__warpPerspectiveMatrix, (640, 480), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)

            frame_masked = self.__frame.copy()
            frame_masked[cv2.cvtColor(free_area_mask_grad_unperp, cv2.COLOR_RGB2GRAY) > 0] = 0

            if 1 == self.__debug_mode and self.__debug_out is not None and self.__debug_out.isOpened():
                self.__debug_out.write(cv2.cvtColor(free_area_mask_grad_unperp + frame_masked, cv2.COLOR_RGB2BGR))
            
            if debug:
                return free_area_mask_grad_unperp

        return x, y

    def __detect_objects_positions(self, debug=False):
        frame_filtered_colors, frame_perp_crop = self.__fiter_frame_by_colors()

        if frame_filtered_colors is None:
            return None

        if 0 != self.__debug_mode:
            debug_img_rects = np.zeros_like(frame_perp_crop)

        objects_positions = {}

        for col in self.__colors_hsv_ranges.keys():
            objects_positions[col] = []
            contours, _ = cv2.findContours(frame_filtered_colors[col], cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

            for c in contours:
                x, y, w, h = cv2.boundingRect(c)
                if (col != 'hand' and (self.__sq_side//2 < w < self.__sq_side and self.__sq_side//2 < h < self.__sq_side)) or\
                   (col == 'hand' and (w > self.__sq_side or h > self.__sq_side)):
                    objects_positions[col].append(
                        ((self.__bottom_right_corner[0] - (x + w/2))/self.__sq_side,
                         (self.__bottom_right_corner[1] - (y + h/2))/self.__sq_side)
                    )

                    if 0 != self.__debug_mode:
                        cv2.rectangle(debug_img_rects, (x - 8, y - 8), (x + w + 8, y + h + 8), self.__colors[col], 2)
        
        if debug or 0 != self.__debug_mode:
            cv2.rectangle(debug_img_rects, (self.__board_range[0][0], self.__board_range[1][0]),
                                           (self.__board_range[0][1], self.__board_range[1][1]), (255,)*3, 4)
            cv2.rectangle(debug_img_rects, (self.__gamearea_range[0][0], self.__gamearea_range[1][0]),
                                           (self.__gamearea_range[0][1], self.__gamearea_range[1][1]), (255,)*3, 4)
            debug_img_rects_unperp = cv2.warpPerspective(debug_img_rects, self.__warpPerspectiveMatrix, (640, 480), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)

            frame_masked = self.__frame.copy()
            frame_masked[cv2.cvtColor(debug_img_rects_unperp, cv2.COLOR_RGB2GRAY) > 0] = 0

            if self.__debug_out is not None and self.__debug_out.isOpened():
                self.__debug_out.write(cv2.cvtColor(debug_img_rects_unperp + frame_masked, cv2.COLOR_RGB2BGR))

            if debug:
                return debug_img_rects_unperp + frame_masked

        return objects_positions

    def __fiter_frame_by_colors(self):
        if self.__warpPerspectiveMatrix is None or self.__frame is None:
            return None, None
        
        frame = self.__frame.copy()

        frame_perp_crop = cv2.warpPerspective(frame, self.__warpPerspectiveMatrix, (self.__out_width, self.__out_height), flags=cv2.INTER_LINEAR)

        frame_perp_crop_hsv = cv2.cvtColor(frame_perp_crop, cv2.COLOR_RGB2HSV)

        frame_filtered_colors = {}

        for c, v in self.__colors_hsv_ranges.items():
            if v[0][0] < v[1][0]:
                frame_filtered_colors[c] = cv2.inRange(frame_perp_crop_hsv, v[0], v[1])
            else:
                u_0 = v[0].copy()
                u_0[0] = 0
                frame_range_1 = cv2.inRange(frame_perp_crop_hsv, u_0, v[1])

                u_1 = v[1].copy()
                u_1[0] = 255
                frame_range_2 = cv2.inRange(frame_perp_crop_hsv, v[0], u_1)

                frame_filtered_colors[c] = cv2.bitwise_or(frame_range_1, frame_range_2)
        
        return frame_filtered_colors, frame_perp_crop

    def __cam_handler(self):
        while self.__run:
            ret, frame = self.__cam.read()
            if ret:
                self.__frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                if 2 == self.__debug_mode:
                    frame_with_positions = self.__detect_objects_positions(debug=True)
                    if  frame_with_positions is not  None:
                        free_area_grad = self.find_free_pos_outside_board(debug=True)
                        if free_area_grad is not None:
                            frame_with_positions_masked = frame_with_positions.copy()
                            frame_with_positions_masked[free_area_grad > 0] = 0
                            free_area_grad[:,:,0] = 0

                            self.__debug_frame = frame_with_positions_masked + free_area_grad
            
            if not self.initialized:
                self.__initialize()
            
            time.sleep(.05)
    
    def __initialize(self):
        if self.__frame is None:
            return None

        frame = self.__frame.copy()

        if 1 == self.__debug_mode and self.__debug_out is not None and self.__debug_out.isOpened():
            self.__debug_out.write(frame)

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frame_gray_float = frame_gray.astype(np.float64)/255.

        frame_gray_float -= frame_gray_float.min()
        frame_gray_float /= frame_gray_float.max()

        frame_gray_norm = (255*frame_gray_float).astype(np.uint8)

        _, frame_gray_norm_thresh_1 = cv2.threshold(frame_gray_norm, 32, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
        _, frame_gray_norm_thresh_2 = cv2.threshold(frame_gray_norm, 100, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C)

        frame_gray_norm_thresh = (255*(frame_gray_norm_thresh_2 - frame_gray_norm_thresh_1)).astype(np.uint8)
        frame_gray_norm_thresh = 255 - frame_gray_norm_thresh
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        try:
            _, corners = cv2.findChessboardCorners(frame_gray_norm_thresh, (7, 7), None)
            corners2 = cv2.cornerSubPix(frame_gray_norm_thresh, corners, (11, 11), (-1, -1), criteria)
        except:
            return None

        corners2 = list(map(lambda c: c[0], corners))

        in_pts = np.float32([corners2[42], corners2[0], corners2[6], corners2[48]])

        out_pts = np.float32([
            [self.__board_range[0][0] + self.__sq_side, self.__board_range[1][0] + self.__sq_side],
            [self.__board_range[0][1] - self.__sq_side, self.__board_range[1][0] + self.__sq_side],
            [self.__board_range[0][1] - self.__sq_side, self.__board_range[1][1] - self.__sq_side], 
            [self.__board_range[0][0] + self.__sq_side, self.__board_range[1][1] - self.__sq_side]
        ])

        self.__warpPerspectiveMatrix = cv2.getPerspectiveTransform(in_pts, out_pts)

    def __stream_handler(self):
        ip_address = 'localhost'

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip_address = s.getsockname()[0]
            s.close()
        except:
            try:
                s.close()
            except:
                pass

        stream_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        for i in range(8089, 8089 + 20):
            try:
                stream_socket.bind((ip_address, i))
                print(f"camera debug socket {i}")
                break
            except:
                pass
        stream_socket.listen(10)
        stream_socket.settimeout(1)

        while self.__run:
            try:
                conn, _ = stream_socket.accept()

                while self.__run:
                    time.sleep(.01)
                    try:
                        frame = self.read_debug_frame()

                        if frame is None:
                            frame = self.read_frame()

                        if frame is not None:
                            data = pickle.dumps(frame)
                            conn.sendall(struct.pack('L', len(data)) + data)

                    except:
                        break

                try:
                    conn.close()
                except:
                    pass

            except:
                pass
        
        stream_socket.close()

if __name__ == '__main__':
    camera = CameraHandler(debug_mode=2)
    camera.start()

    try:
        while True:
            time.sleep(.1)
    except:
        camera.stop()