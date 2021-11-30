import socket
import sys
import cv2
import pickle
import numpy as np
import struct ## new

HOST = '192.168.1.23'

stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

stream_socket.connect((HOST, 8089))

data = bytes()
payload_size = struct.calcsize('L') 

i = 0
while True:
    try:
        print(f'\rReceiving frame {i} size... ', end='')
        while len(data) < payload_size:
            data += stream_socket.recv(4096)
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack('L', packed_msg_size)[0]
        print(f'size={msg_size} ', end='')
        print(f'Receiving frame {i}... ', end='')
        while len(data) < msg_size:
            data += stream_socket.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        print(f'Frame received... ', end='')

        frame = pickle.loads(frame_data)
        cv2.imshow('Debug camera', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        cv2.waitKey(100)

        print(f'Frame displayed', end='')
        i += 1
    except:
        print('\nConnection lost')
        break
