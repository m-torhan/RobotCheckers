from typing_extensions import runtime
from RPi import GPIO
import traceback
import threading
import datetime

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
        self.__speed = 100

    @property
    def pos(self):
        return self.__pos

    @property
    def X_range(self):
        return self.__X_range

    @property
    def Y_range(self):
        return self.__Y_range
    
    @property
    def calibrated(self):
        return self.__calibrated

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
        self.__instr_list.append(f'sxf')

    def step_X_backward(self):
        self.__instr_list.append(f'sxb')
    
    def step_Y_forward(self):
        self.__instr_list.append(f'syf')

    def step_Y_backward(self):
        self.__instr_list.append(f'syb')
    
    def move_to(self, x, y):
        self.__instr_list.append(f'mv {x} {y}')

    def move_to_square(self, row, col):
        self.__instr_list.append(f'mv_sq {row} {col}')

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
                try:
                    instr = self.__instr_list.pop(0).split()
                    if instr[0] == 'mv':
                        self.__move_to_inner(float(instr[1]), float(instr[2]))

                    elif instr[0] == 'mv_sq':
                        self.__move_to_square_inner(int(instr[1]), int(instr[2]))
                    
                    elif instr[0] == 'sxf':
                        self.__step_X_forward_inner()
                    
                    elif instr[0] == 'sxb':
                        self.__step_X_backward_inner()
                    
                    elif instr[0] == 'syf':
                        self.__step_Y_forward_inner()
                    
                    elif instr[0] == 'syfb':
                        self.__step_Y_backward_inner()
                    
                    else:
                        self.__log(f'Unknown instruction: {instr}')

                except Exception as ex:
                    self.__log(f'Instr handling error: {traceback.format_exc()}')
    
    def __step_X_forward_inner(self):
        pass

    def __step_X_backward_inner(self):
        pass
    
    def __step_Y_forward_inner(self):
        pass

    def __step_Y_backward_inner(self):
        pass

    def __move_to_inner(self, x, y):
        pass
    
    def __move_to_square_inner(self, row, col):
        if row < 0 or row > 7:
            raise Exception(f'Wrong row: {row}')

        if col < 0 or col > 7:
            raise Exception(f'Wrong column: {col}')

        pass
    
    def __log(self, log):
        with open('logs/movement_handler.txt') as log_file:
            log = log.replace('\n\r', ' ')
            log_file.write(f'{datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")} {log}\n')