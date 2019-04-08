#!/usr/bin/env python
# coding: utf-8

import socket
import cv2
import sys
import argparse

import video_grabber

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, help='The port on which the server is listening', required=True)
parser.add_argument('--jpeg_quality', type=int, help='The JPEG quality for compressing the reply', default=50)
parser.add_argument('--encoder', type=str, choices=['cv2','turbo'], help='Which library to use to encode/decode in JPEG the images', default='cv2')

args = parser.parse_args()

jpeg_quality = args.jpeg_quality
host         = ''
port         = args.port
encoder      = args.encoder

# The grabber of the webcam
grabber = video_grabber.VideoGrabber(jpeg_quality, encoder)
grabber.start()
get_message = lambda: grabber.get_buffer()

keep_running = True

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = (host, port)

print('starting up on %s port %s\n' % server_address)

sock.bind(server_address)

while(keep_running):
    data, address = sock.recvfrom(4)
    data = data.decode('utf-8')
    if(data == "get"):
        buffer = get_message()
        if buffer is None:
            continue
        if len(buffer) > 65507:
            print("The message is too large to be sent within a single UDP datagram. We do not handle splitting the message in multiple datagrams")
            sock.sendto("FAIL".encode('utf-8'),address)
            continue
        # We send back the buffer to the client
        sock.sendto(buffer, address)
    elif(data == "quit"):
        grabber.stop()
        keep_running = False

print("Quitting..")
grabber.join()
sock.close()
