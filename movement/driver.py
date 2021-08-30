from typing_extensions import runtime
from RPi import GPIO
import threading

import config

class MovementHandler(object):
    def __init__(self):
        GPIO.setup(config.pin_endstop_X_min, GPIO.IN)
        GPIO.setup(config.pin_endstop_X_max, GPIO.IN)
        GPIO.setup(config.pin_endstop_Y_min, GPIO.IN)
        GPIO.setup(config.pin_endstop_Y_max, GPIO.IN)

        GPIO.setup(config.pin_motor_A_step, GPIO.OUT)
        GPIO.setup(config.pin_motor_A_dir, GPIO.OUT)
        GPIO.setup(config.pin_motor_B_step, GPIO.OUT)
        GPIO.setup(config.pin_motor_B_dir, GPIO.OUT)

        GPIO.setup(config.pin_magnet, GPIO.OUT)

        GPIO.setup(config.pin_servo, GPIO.OUT)

        self.__pos = [0, 0]
        self.__X_range = 0
        self.__Y_range = 0
        self.__calibrated = False
        self.__run = True
        self.__instr_list = []
        self.__instr_handler_thread = threading.Thread(target=self.__instr_handler)

    def start(self):
        self.__instr_handler_thread.start()

    def stop(self):
        self.__run = False

        self.__instr_handler_thread.join()

        GPIO.cleanup()

    def endstop_state_X_min(self):
        return GPIO.input(config.pin_endstop_X_min)
        
    def endstop_state_X_max(self):
        return GPIO.input(config.pin_endstop_X_max)
        
    def endstop_state_Y_min(self):
        return GPIO.input(config.pin_endstop_Y_min)
        
    def endstop_state_Y_max(self):
        return GPIO.input(config.pin_endstop_Y_max)

    def step_X_forward(self):
        pass

    def step_X_backward(self):
        pass
    
    def step_Y_forward(self):
        pass

    def step_Y_backward(self):
        pass

    def calibrate(self):
        # calibrate X max
        while not self.endstop_state_X_max():
            self.step_X_forward()
        
        # calibrate X min
        X_range = 0
        while not self.endstop_state_X_min():
            self.step_X_backward()
            X_range += 1
        
        self.__pos[0] = 0
        self.__X_range = X_range

        # calibrate Y max
        while not self.endstop_state_Y_max():
            self.step_Y_forward()

        # calibrate Y min
        Y_range = 0
        while not self.endstop_state_Y_min():
            self.step_Y_backward()
            Y_range += 1
        
        self.__pos[1] = 0
        self.__Y_range = Y_range

    def __instr_handler(self):
        while self.__run:
            if len(self.__instr_list):
                instr = self.__instr_list.pop(0)
