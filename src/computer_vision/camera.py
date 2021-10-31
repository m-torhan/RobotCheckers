import numpy as np
import cv2
import threading

class CameraHandler(object):
    def __init__(self):
        self.__cam = cv2.VideoCapture(0)
        self.__frame = None
        self.__run = True
        self.__cam_thread = threading.Thread(target=self.__cam_handler)
    
    def start(self):
        self.__cam_thread.start()
        
    def stop(self):
        self.__run = False
        self.__cam_thread.join()

    def read_frame(self):
        #cv2.normalize(frame, frame, 0, 255, cv2.NORM_MINMAX)
        return self.__frame.copy()
    
    def read_board(self):
        frame = self.__frame.copy()
        
        # process frame

        return np.zeros((8, 8), dtype=np.uint8)
    
    def __cam_handler(self):
        while self.__run:
            self.__frame = self.__cam.read()[1]
