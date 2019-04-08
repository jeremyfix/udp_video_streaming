import sys
import argparse
import socket

import cv2
import numpy as np

import utils

def image_process(cv2_img):
    # For fun, we play with the image
    cv2_img = 255 - cv2_img
    return cv2_img

parser = argparse.ArgumentParser()

parser.add_argument('--port', type=int, help='The port on which to listen for incoming connections', required=True)
parser.add_argument('--jpeg_quality', type=int, help='The JPEG quality for compressing the reply', default=50)
args = parser.parse_args()

host         = '' # any interface
port         = args.port
jpeg_quality = args.jpeg_quality

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            cmd = utils.recv_data(conn, 5).decode('ascii')
            if(cmd == 'image'):
                # Read the image buffer size
                img_size = int(utils.recv_data(conn, 7).decode('ascii'))

                # Read the buffer content
                img_buffer = utils.recv_data(conn, img_size)

                # Decode the image
                img = utils.decode_image_buffer(img_buffer)

               # Process it
                res = image_process(img)

                # Encode the image
                res_buffer = utils.encode_image(res, jpeg_quality)

                # Make the reply
                reply = bytes("image{:07}".format(len(res_buffer)), "ascii")
                utils.send_data(conn, reply)
                utils.send_data(conn, res_buffer)
                utils.send_data(conn, bytes('enod!', 'ascii'))
            elif cmd == 'quit!':
                break
            else:
                print("Got something else")
        print("Quitting")

