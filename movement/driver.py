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
        
        self.__servo_pwm = GPIO.PWM(config.pin_servo, 50)
        self.__servo_pwm.start(0)

        self.__pos = [0, 0]
        self.__X_range = 0
        self.__Y_range = 0
        self.__calibrated = False
        self.__run = True
        self.__instr_list = []
        self.__instr_handler_thread = threading.Thread(target=self.__instr_handler)
        self.__speed = 2000

    @property
    def pos(self):
        return (self.__pos[0]/config.steps_per_cm, self.__pos[1]/config.steps_per_cm)

    @property
    def X_range(self):
        return (self.__X_range[0]/config.steps_per_cm, self.__X_range[1]/config.steps_per_cm)

    @property
    def Y_range(self):
        return (self.__Y_range[0]/config.steps_per_cm, self.__Y_range[1]/config.steps_per_cm)
    
    @property
    def calibrated(self):
        return self.__calibrated

    def start(self):
        self.__instr_handler_thread.start()

    def stop(self):
        self.__run = False

        self.__instr_handler_thread.join()

        self.__servo_pwm.stop()

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
        self.__instr_list.append(f'mt {x} {y}')

    def move_to_square(self, row, col):
        self.__instr_list.append(f'mts {row} {col}')
    
    def set_magnet(self, state):
        self.__instr_list.append(f'sm {state}')

    def set_servo(self, value):
        self.__instr_list.append(f'ss {value}')
    
    def put_pawn(self):
        self.__instr_list.append(f'pp')

    def take_pawn(self):
        self.__instr_list.append(f'tp')

    def calibrate(self):
        self.__instr_list.append(f'c')

    def __instr_handler(self):
        while self.__run:
            if len(self.__instr_list):
                try:
                    instr = self.__instr_list.pop(0).split()
                    if instr[0] == 'mt':
                        self.__move_to_inner(float(instr[1]), int(float[2]))

                    elif instr[0] == 'mts':
                        self.__move_to_square_inner(int(instr[1]), int(instr[2]))
                    
                    elif instr[0] == 'sxf':
                        self.__step_X_forward_inner()
                    
                    elif instr[0] == 'sxb':
                        self.__step_X_backward_inner()
                    
                    elif instr[0] == 'syf':
                        self.__step_Y_forward_inner()
                    
                    elif instr[0] == 'syb':
                        self.__step_Y_backward_inner()
                    
                    elif instr[0] == 'sm':
                        self.__set_magnet_inner(int(instr[1]))
                        
                    elif instr[0] == 'ss':
                        self.__set_servo_inner(int(instr[1]))
                        
                    elif instr[0] == 'pp':
                        self.__put_pawn_inner()
                        
                    elif instr[0] == 'tp':
                        self.__take_pawn_inner()

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
        step_x = int(x*config.steps_per_cm)
        step_y = int(y*config.steps_per_cm)

        if step_x < self.__X_range[0]:
            step_x = self.__X_range[0]
        if step_x > self.__X_range[1]:
            step_x = self.__X_range[1]

        if step_y < self.__Y_range[0]:
            step_y = self.__Y_range[0]
        if step_y > self.__Y_range[1]:
            step_y = self.__Y_range[1]

        delta_x = step_x - self.pos[0]
        delta_y = step_y - self.pos[1]

        a_dir = 0
        b_dir = 0

        a_const = False
        b_const = False

        if delta_x == 0 and delta_y == 0:
            return

        if delta_x == 0:
            if delta_y < 0:
                a_dir = 1
                b_dir = -1
            else:
                a_dir = -1
                b_dir = 1
        elif delta_y == 0:
            if delta_x < 0:
                a_dir = -1
                b_dir = -1
            else:
                a_dir = 1
                b_dir = 1
        else:
            if delta_x < 0:
                if delta_y < 0:
                    b_const = True
                    b_dir = -1
                    if delta_x < delta_y:
                        a_dir = 1
                    elif delta_x > delta_y:
                        a_dir = -1
                    else:
                        a_dir = 0
                else:
                    a_const = True
                    a_dir = 1
                    if delta_x < delta_y:
                        b_dir = 1
                    elif delta_x > delta_y:
                        b_dir = -1
                    else:
                        b_dir = 0
            else:
                if delta_y < 0:
                    a_const = True
                    a_dir = -1
                    if delta_x < delta_y:
                        b_dir = -1
                    elif delta_x > delta_y:
                        b_dir = +1
                    else:
                        b_dir = 0
                else:
                    b_const = True
                    b_dir = 1
                    if delta_x < delta_y:
                        a_dir = -1
                    elif delta_x > delta_y:
                        a_dir = 1
                    else:
                        a_dir = 0

        if a_dir != 0:
            GPIO.output(config.pin_motor_A_dir, GPIO.HIGH if a_dir == 1 else GPIO.LOW)
        
        if b_dir != 0:
            GPIO.output(config.pin_motor_B_dir, GPIO.HIGH if b_dir == 1 else GPIO.LOW)

        p = [0, 0]

        if b_dir == 0:
            while p[0] != 2*delta_x or p[1] != 2*delta_y:
                GPIO.output(config.pin_motor_A_step, GPIO.HIGH)
                time.sleep(1./self.__speed)
                GPIO.output(config.pin_motor_A_step, GPIO.LOW)
                time.sleep(1./self.__speed)

                p[0] += a_dir
                p[1] += -a_dir

        elif a_dir == 0:
            while p[0] != 2*delta_x or p[1] != 2*delta_y:
                GPIO.output(config.pin_motor_B_step, GPIO.HIGH)
                time.sleep(1./self.__speed)
                GPIO.output(config.pin_motor_B_step, GPIO.LOW)
                time.sleep(1./self.__speed)

                p[0] += b_dir
                p[1] += b_dir
        
        elif delta_x == 0 or delta_y == 0:
            while p[0] != 2*delta_x or p[1] != 2*delta_y:
                GPIO.output(config.pin_motor_B_step, GPIO.HIGH)
                time.sleep(1./self.__speed)
                GPIO.output(config.pin_motor_B_step, GPIO.LOW)
                time.sleep(1./self.__speed)

                p[0] += b_dir
                p[1] += b_dir

                GPIO.output(config.pin_motor_A_step, GPIO.HIGH)
                time.sleep(1./self.__speed)
                GPIO.output(config.pin_motor_A_step, GPIO.LOW)
                time.sleep(1./self.__speed)

                p[0] += a_dir
                p[1] += -a_dir

        elif a_const:
            while p[0] != 2*delta_x or p[1] != 2*delta_y:
                if (delta_x - delta_y)*(delta_x*p[1] - delta_y*p[0]) > 0:
                    GPIO.output(config.pin_motor_B_step, GPIO.HIGH)
                    time.sleep(1./self.__speed)
                    GPIO.output(config.pin_motor_B_step, GPIO.LOW)
                    time.sleep(1./self.__speed)

                    p[0] += b_dir
                    p[1] += b_dir
                else:
                    GPIO.output(config.pin_motor_A_step, GPIO.HIGH)
                    time.sleep(1./self.__speed)
                    GPIO.output(config.pin_motor_A_step, GPIO.LOW)
                    time.sleep(1./self.__speed)

                    p[0] += a_dir
                    p[1] += -a_dir

        elif b_const:
            while p[0] != 2*delta_x or p[1] != 2*delta_y:
                if (delta_x - delta_y)*(delta_x*p[1] - delta_y*p[0]) > 0:
                    GPIO.output(config.pin_motor_A_step, GPIO.HIGH)
                    time.sleep(1./self.__speed)
                    GPIO.output(config.pin_motor_A_step, GPIO.LOW)
                    time.sleep(1./self.__speed)

                    p[0] += a_dir
                    p[1] += -a_dir
                else:
                    GPIO.output(config.pin_motor_B_step, GPIO.HIGH)
                    time.sleep(1./self.__speed)
                    GPIO.output(config.pin_motor_B_step, GPIO.LOW)
                    time.sleep(1./self.__speed)
                    
                    p[0] += b_dir
                    p[1] += b_dir

        self.__pos[0] = x
        self.__pos[1] = y

    def __move_to_square_inner(self, row, col):
        if row < 0 or row > 7:
            raise Exception(f'Wrong row: {row}')

        if col < 0 or col > 7:
            raise Exception(f'Wrong column: {col}')

        pass
    
    def __set_magnet_inner(self, state):
        GPIO.output(config.pin_magnet, GPIO.HIGH if state else GPIO.LOW)

    def __set_servo_inner(self, value):
        self.__servo_pwm.ChangeDutyCycle(value)

    def __put_pawn_inner(self):
        self.__set_servo_inner(2)
        time.sleep(1.2)
        self.__set_magnet_inner(0)
        time.sleep(.5)
        self.__set_servo_inner(12)
        # time.sleep(1.2)
        # self.__set_servo_inner(0)

    def __take_pawn_inner(self):
        self.__set_servo_inner(2)
        time.sleep(1.2)
        self.__set_magnet_inner(1)
        time.sleep(.5)
        self.__set_servo_inner(12)
        # time.sleep(1.2)
        # self.__set_servo_inner(0)

    def __calibrate_inner(self):
        self.__X_range = [-float('inf'), float('inf')]
        # calibrate X max
        self.__speed = config.max_speed
        while not GPIO.input(config.pin_endstop_X_max):
            self.__step_X_forward_inner()
        
        self.__speed = config.max_speed/8
        for _ in range(config.steps_per_cm):
            self.__step_X_backward_inner()
            
        while not GPIO.input(config.pin_endstop_X_max):
            self.__step_X_forward_inner()
         
        # calibrate X min
        X_range = 0
        self.__speed = config.max_speed
        while not GPIO.input(config.pin_endstop_X_min):
            self.__step_X_backward_inner()
            X_range += 1
        
        self.__speed = config.max_speed/8
        for _ in range(config.steps_per_cm):
            self.__step_X_forward_inner()
            X_range -= 1
        
        while not GPIO.input(config.pin_endstop_X_min):
            self.__step_X_backward_inner()
            X_range += 1

        self.__pos[0] = 0
        self.__X_range = [0, X_range]

        self.__Y_range = [-float('inf'), float('inf')]
        # calibrate Y max
        self.__speed = config.max_speed
        while not GPIO.input(config.pin_endstop_Y_max):
            self.__step_Y_forward_inner()

        self.__speed = config.max_speed/8
        for _ in range(config.steps_per_cm):
            self.__step_Y_backward_inner()
            
        while not GPIO.input(config.pin_endstop_Y_max):
            self.__step_Y_forward_inner()

        # calibrate Y min
        Y_range = 0
        self.__speed = config.max_speed
        while not GPIO.input(config.pin_endstop_Y_min):
            self.__step_Y_backward_inner()
            Y_range += 1
        
        self.__speed = config.max_speed/8
        for _ in range(config.steps_per_cm):
            self.__step_Y_forward_inner()
            Y_range -= 1
            
        while not GPIO.input(config.pin_endstop_Y_min):
            self.__step_Y_backward_inner()
            Y_range += 1

        self.__pos[1] = 0
        self.__Y_range = [0, Y_range]

    def __log(self, log):
        with open('logs/movement_handler.txt', 'a') as log_file:
            log = log.replace('\n', '\n  ')
            log_file.write(f'{datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")} {log}\n')