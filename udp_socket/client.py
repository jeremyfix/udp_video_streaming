#!/usr/bin/env python
# coding: utf-8

import socket
import cv2
import numpy as np
import sys
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str, help='The IP at the server is listening', required=True)
parser.add_argument('--port', type=int, help='The port on which the server is listening', required=True)
parser.add_argument('--jpeg_quality', type=int, help='The JPEG quality for compressing the reply', default=50)
parser.add_argument('--encoder', type=str, choices=['cv2','turbo'], help='Which library to use to encode/decode in JPEG the images', default='cv2')

args = parser.parse_args()




# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = args.host
port = args.port
server_address = (host, port)

cv2.namedWindow("Image")

t0 = time.time()
frame_idx = 0

while(True):
    sent = sock.sendto("get".encode('utf-8'), server_address)

    data, server = sock.recvfrom(65507)
    if len(data) == 4:
        # This is a message error sent back by the server
        if(data == "FAIL"):
            continue
    array = np.frombuffer(data, dtype=np.dtype('uint8'))
    img = cv2.imdecode(array, 1)
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Asking the server to quit")
        sock.sendto("quit".encode('utf-8'), server_address)
        print("Quitting")
        break
    frame_idx += 1

    if frame_idx == 30:
        t1 = time.time()
        sys.stdout.write('\r Framerate : {:.2f} frames/s.     '.format(30 / (t1 - t0)))
        sys.stdout.flush()
        t0 = t1
        frame_idx = 0
