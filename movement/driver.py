from RPi import GPIO
import traceback
import threading
import datetime
import time

import config

class MovementHandler(object):
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(config.pin_endstop_X_min, GPIO.IN)
        GPIO.setup(config.pin_endstop_X_max, GPIO.IN)
        GPIO.setup(config.pin_endstop_Y_min, GPIO.IN)
        GPIO.setup(config.pin_endstop_Y_max, GPIO.IN)

        GPIO.setup(config.pin_motor_A_step, GPIO.OUT)
        GPIO.setup(config.pin_motor_A_dir, GPIO.OUT)
        GPIO.setup(config.pin_motor_B_step, GPIO.OUT)
        GPIO.setup(config.pin_motor_B_dir, GPIO.OUT)
        
        GPIO.output(config.pin_motor_A_step, GPIO.LOW)
        GPIO.output(config.pin_motor_A_dir, GPIO.LOW)
        GPIO.output(config.pin_motor_B_step, GPIO.LOW)
        GPIO.output(config.pin_motor_B_dir, GPIO.LOW)

        GPIO.setup(config.pin_magnet, GPIO.OUT)
        
        GPIO.output(config.pin_magnet, GPIO.LOW)

        GPIO.setup(config.pin_servo, GPIO.OUT)
        
        GPIO.output(config.pin_servo, GPIO.LOW)

        self.__pos = [0, 0]
        self.__X_range = 0
        self.__Y_range = 0
        self.__calibrated = False
        self.__run = True
        self.__instr_list = []
        self.__instr_handler_thread = threading.Thread(target=self.__instr_handler)
        self.__speed = 1000

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
    
    @property
    def instr_count(self):
        return len(self.__instr_list)

    def start(self):
        self.__instr_handler_thread.start()

    def stop(self):
        self.__run = False

        self.__instr_handler_thread.join()

        GPIO.cleanup()

    def endstop_state(self, axis, end):
        if axis == 'X':
            if end == 0:
                return GPIO.input(config.pin_endstop_X_min)
            if end == 1:
                return GPIO.input(config.pin_endstop_X_max)
        if axis == 'Y':
            if end == 0:
                return GPIO.input(config.pin_endstop_Y_min)
            if end == 1:
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
    
    def set_magnet(self, state):
        self.__instr_list.append(f's_m {state}')

    def set_servo(self, state):
        self.__instr_list.append(f's_s {state}')

    def calibrate(self):
        self.__instr_list.append(f'c')

    def __instr_handler(self):
        while self.__run:
            if len(self.__instr_list):
                try:
                    instr = self.__instr_list.pop(0).split()
                    if instr[0] == 'mv':
                        self.__move_to_inner(int(instr[1]), int(instr[2]))

                    elif instr[0] == 'mv_sq':
                        self.__move_to_square_inner(int(instr[1]), int(instr[2]))
                    
                    elif instr[0] == 'sxf':
                        self.__step_X_forward_inner()
                    
                    elif instr[0] == 'sxb':
                        self.__step_X_backward_inner()
                    
                    elif instr[0] == 'syf':
                        self.__step_Y_forward_inner()
                    
                    elif instr[0] == 'syb':
                        self.__step_Y_backward_inner()
                    
                    elif instr[0] == 's_m':
                        self.__set_magnet_inner(int(instr[1]))
                        
                    elif instr[0] == 's_s':
                        self.__set_servo_inner(int(instr[1]))

                    elif instr[0] == 'c':
                        self.__calibrate_inner()
                    
                    else:
                        self.__log(f'Unknown instruction: {instr}')

                except Exception as ex:
                    self.__log(f'Instr handling error: {traceback.format_exc()}')

    def __step_X_forward_inner(self):
        if self.__pos[0] >= self.__X_range[1]:
            return
        GPIO.output(config.pin_motor_A_dir, GPIO.HIGH)
        GPIO.output(config.pin_motor_B_dir, GPIO.HIGH)
        GPIO.output(config.pin_motor_A_step, GPIO.HIGH)
        GPIO.output(config.pin_motor_B_step, GPIO.HIGH)
        time.sleep(1./self.__speed)
        GPIO.output(config.pin_motor_A_step, GPIO.LOW)
        GPIO.output(config.pin_motor_B_step, GPIO.LOW)
        time.sleep(1./self.__speed)
        self.__pos[0] += 1

    def __step_X_backward_inner(self):
        if self.__pos[0] <= self.__X_range[0]:
            return
        GPIO.output(config.pin_motor_A_dir, GPIO.LOW)
        GPIO.output(config.pin_motor_B_dir, GPIO.LOW)
        GPIO.output(config.pin_motor_A_step, GPIO.HIGH)
        GPIO.output(config.pin_motor_B_step, GPIO.HIGH)
        time.sleep(1./self.__speed)
        GPIO.output(config.pin_motor_A_step, GPIO.LOW)
        GPIO.output(config.pin_motor_B_step, GPIO.LOW)
        time.sleep(1./self.__speed)
        self.__pos[0] -= 1
    
    def __step_Y_forward_inner(self):
        if self.__pos[1] >= self.__Y_range[1]:
            return
        GPIO.output(config.pin_motor_A_dir, GPIO.LOW)
        GPIO.output(config.pin_motor_B_dir, GPIO.HIGH)
        GPIO.output(config.pin_motor_A_step, GPIO.HIGH)
        GPIO.output(config.pin_motor_B_step, GPIO.HIGH)
        time.sleep(1./self.__speed)
        GPIO.output(config.pin_motor_A_step, GPIO.LOW)
        GPIO.output(config.pin_motor_B_step, GPIO.LOW)
        time.sleep(1./self.__speed)
        self.__pos[1] += 1

    def __step_Y_backward_inner(self):
        if self.__pos[1] <= self.__Y_range[0]:
            return
        GPIO.output(config.pin_motor_A_dir, GPIO.HIGH)
        GPIO.output(config.pin_motor_B_dir, GPIO.LOW)
        GPIO.output(config.pin_motor_A_step, GPIO.HIGH)
        GPIO.output(config.pin_motor_B_step, GPIO.HIGH)
        time.sleep(1./self.__speed)
        GPIO.output(config.pin_motor_A_step, GPIO.LOW)
        GPIO.output(config.pin_motor_B_step, GPIO.LOW)
        time.sleep(1./self.__speed)
        self.__pos[1] -= 1

    def __move_to_inner(self, x, y):
        delta_x = abs(x - self.pos[0])
        delta_y = abs(y - self.pos[1])

        p = [0, 0]

        for _ in range(delta_x + delta_y):
            if delta_y - p[1] == 0 or delta_x*p[1] - delta_y*p[0] > 0:
                if x > self.pos[0]:
                    self.__step_X_forward_inner()
                else:
                    self.__step_X_backward_inner()
                p[0] += 1
            else:
                if y > self.pos[1]:
                    self.__step_Y_forward_inner()
                else:
                    self.__step_Y_backward_inner()
                p[1] += 1

    def __move_to_square_inner(self, row, col):
        if row < 0 or row > 7:
            raise Exception(f'Wrong row: {row}')

        if col < 0 or col > 7:
            raise Exception(f'Wrong column: {col}')

        pass
    
    def __set_magnet_inner(self, state):
        GPIO.output(config.pin_magnet, GPIO.HIGH if state else GPIO.LOW)

    def __set_servo_inner(self, state):
        GPIO.output(config.pin_servo, GPIO.HIGH if state else GPIO.LOW)

    def __calibrate_inner(self):
        self.__X_range = [-float('inf'), float('inf')]
        # calibrate X max
        while not GPIO.input(config.pin_endstop_X_max):
            self.__step_X_forward_inner()
         
        # calibrate X min
        X_range = 0
        while not GPIO.input(config.pin_endstop_X_min):
            self.__step_X_backward_inner()
            X_range += 1
        
        self.__pos[0] = 0
        self.__X_range = [0, X_range]

        self.__Y_range = [-float('inf'), float('inf')]
        # calibrate Y max
        while not GPIO.input(config.pin_endstop_Y_max):
            self.__step_Y_forward_inner()

        # calibrate Y min
        Y_range = 0
        while not GPIO.input(config.pin_endstop_Y_min):
            self.__step_Y_backward_inner()
            Y_range += 1
        
        self.__pos[1] = 0
        self.__Y_range = [0, Y_range]

    def __log(self, log):
        with open('logs/movement_handler.txt', 'a') as log_file:
            log = log.replace('\n', ' ').replace('\r', ' ')
            log_file.write(f'{datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")} {log}\n')