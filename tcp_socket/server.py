import sys
import argparse
import socket

import cv2
import numpy as np

from turbojpeg import TurboJPEG

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

jpeg = TurboJPEG()

# A temporary buffer in which the received data will be copied
# this prevents creating a new buffer all the time
tmp_buf = bytearray(7)
tmp_view = memoryview(tmp_buf) # this allows to get a reference to a slice of tmp_buf

# Creates a temporary buffer which can hold the largest image we can transmit
img_buf = bytearray(9999999)
img_view = memoryview(img_buf)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            utils.recv_data_into(conn, tmp_view[:5], 5)
            cmd = tmp_buf[:5].decode('ascii')
            if(cmd == 'image'):
                # Read the image buffer size
                utils.recv_data_into(conn, tmp_view, 7)
                img_size = int(tmp_buf.decode('ascii'))

                # Read the buffer content
                utils.recv_data_into(conn, img_view[:img_size], img_size)

                # Decode the image
                img = utils.decode_image_buffer(img_view[:img_size], jpeg)

                # Process it
                res = image_process(img)

                # Encode the image
                res_buffer = utils.encode_image(res, jpeg, jpeg_quality)

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

