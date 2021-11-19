import os
import numpy as np
import cv2
import threading

import config

class CameraHandler(object):
    def __init__(self, debug=False):
        self.__debug = debug
        self.__cam = cv2.VideoCapture(0)
        self.__frame = None
        self.__warpPerspectiveMatrix = None
        self.__run = True
        self.__cam_thread = threading.Thread(target=self.__cam_handler)
        self.__debug_out = None

        # square size in pixels
        self.__sq_side = 64
        sq_side_cm = config.board_size[0]//8
        px_per_cm = self.__sq_side//sq_side_cm

        # board borders in pixels
        self.__x_min = px_per_cm*(config.gamearea_size[0] - config.board_size[0]) + self.__sq_side*3//2
        self.__y_min = self.__sq_side*3//2
        xy_delta = self.__sq_side*6
        self.__x_max = self.__x_min + xy_delta
        self.__y_max = self.__y_min + xy_delta

        self.__bottom_right_corner = (self.__x_max + xy_delta//6, self.__y_max + xy_delta//6)

        # board size in pixels
        self.__out_width = self.__sq_side*8*config.gamearea_size[0]//config.board_size[0] + self.__sq_side//2
        self.__out_height = self.__sq_side*8*config.gamearea_size[1]//config.board_size[1] + self.__sq_side//2
    
    @property
    def initialized(self):
        return self.__warpPerspectiveMatrix is not None
    
    def start(self):
        self.__cam_thread.start()
        
        if self.__debug:
            vid_idx = 0

            while os.path.isfile(f'vids/debug_vid_{vid_idx}.avi'):
                vid_idx += 1

            self.__debug_out = cv2.VideoWriter(f'vids/debug_vid_{vid_idx}.avi', cv2.VideoWriter_fourcc(*'XVID'), fps, (640,480))
        
    def stop(self):
        self.__run = False
        self.__cam_thread.join()

        if self.__debug:
            self.__debug_out.release()

    def read_frame(self):
        return self.__frame.copy()
    
    def read_board(self):
        objects_positions = self.detect_objects_positions()

        board_code = np.zeros((8, 8), dtype=np.uint8)
        board_pos = np.zeros((8, 8, 2), dtype=np.float64)

        free_pawns = {}

        for color, code in config.pawns_colors_code.items():
            free_pawns[color] = []
            for x, y in objects_positions[color]:
                pawn_on_board = False
                if self.__x_min - self.__sq_side/2 < x < self.__x_max + self.__sq_side/2 and\
                   self.__y_min - self.__sq_side/2 < y < self.__y_max + self.__sq_side/2:
                   for i in range(min(0, int(x) - 1), max(8, int(x) + 2)):
                       for j in range(min(0, int(y) - 1), max(8, int(y) + 2)):
                           if (x - i)**2 + (y - j)**2 < 1/4:
                               pawn_on_board = True
                               board_code[i, j] = code
                               board_pos[i, j, 0] = x
                               board_pos[i, j, 1] = y
                               
                if not pawn_on_board:
                    free_pawns[color].append((x, y))

        return board_code, board_pos, free_pawns, len(objects_positions['hand']) > 0

    def detect_objects_positions(self):
        if self.__warpPerspectiveMatrix is None or self.__frame is None:
            return None
        
        frame = self.__frame.copy()

        frame_perp_crop = cv2.warpPerspective(frame, self.__warpPerspectiveMatrix, (self.__out_width, self.__out_height), flags=cv2.INTER_LINEAR)

        frame_perp_crop_hsv = cv2.cvtColor(frame_perp_crop, cv2.COLOR_RGB2HSV)

        colors_hsv_ranges = {
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

        frame_filtered_colors = {}

        for c, v in colors_hsv_ranges.items():
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

        if self.__debug:
            debug_img_rects = np.zeros_like(frame_perp_crop)

            colors = {
                'white': (255,)*3,
                'blue' : (7, 42, 88),
                'black': (32,)*3,
                'red'  : (175, 32, 38),
                'hand' : (255, 255, 0)
            }

        objects_positions = {}

        for col in colors_hsv_ranges.keys():
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

                    if self.__debug:
                        cv2.rectangle(debug_img_rects, (x - 8, y - 8), (x + w + 8, y + h + 8), colors[col], 2)
        
        if self.__debug:
            debug_img_rects_unperp = cv2.warpPerspective(debug_img_rects, self.__warpPerspectiveMatrix, (640, 480), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)

            frame_masked = frame.copy()
            frame_masked[cv2.cvtColor(debug_img_rects_unperp, cv2.COLOR_RGB2GRAY) > 0] = 0

            self.__debug_out.write(debug_img_rects_unperp + frame_masked)

        return objects_positions

    def __cam_handler(self):
        while self.__run:
            ret, frame = self.__cam.read()
            if ret:
                self.__frame = frame
            
            if not self.initialized:
                self.__initialize()
    
    def __initialize(self):
        if self.__frame is None:
            return None

        frame = self.__frame.copy()

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

        out_a = [self.__x_min, self.__y_min]
        out_b = [self.__x_max, self.__y_min]
        out_c = [self.__x_max, self.__y_max]
        out_d = [self.__x_min, self.__y_max]
        out_pts = np.float32([out_a, out_b, out_c, out_d])

        self.__warpPerspectiveMatrix = cv2.getPerspectiveTransform(in_pts, out_pts)
