import numpy as np
import cv2

class CameraHandler(object):
    def __init__(self):
        self.__cam = cv2.VideoCapture(0)
    
    def read_frame(self):
        return self.__cam.read()[1]
    
    def read_board(self):
        frame = self.read_frame()
        
        # process frame

        return np.zeros((8, 8), dtype=np.uint8)