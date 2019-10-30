#!/usr/bin/env python3

# Standard modules
import argparse
import socket
import sys
import time
import functools
# External modules
import cv2
# Local modules
import video_grabber
import utils

parser = argparse.ArgumentParser()

parser.add_argument('--host', type=str,
                    help='The IP of the echo server',
                    required=True)
parser.add_argument('--port', type=int,
                    help='The port on which the server is listening',
                    required=True)
parser.add_argument('--jpeg_quality', type=int,
                    help='The JPEG quality for compressing the reply',
                    default=50)
parser.add_argument('--resize', type=float,
                    help='Resize factor of the image',
                    default=1.0)
parser.add_argument('--encoder', type=str, choices=['cv2', 'turbo'],
                    help='Library to use to encode/decode in JPEG the images',
                    default='cv2')

args = parser.parse_args()

host         = args.host
port         = args.port
jpeg_quality = args.jpeg_quality
resize_factor = args.resize

cv2.namedWindow("Image")

keep_running = True

if args.encoder == 'turbo':
    from turbojpeg import TurboJPEG

    jpeg                   = TurboJPEG()
    jpeg_encode_func = lambda img, jpeg_quality=jpeg_quality: utils.turbo_encode_image(img, jpeg, jpeg_quality)
    jpeg_decode_func = lambda buf: utils.turbo_decode_image_buffer(buf, jpeg)
else:
    jpeg_encode_func = lambda img, jpeg_quality=jpeg_quality: utils.cv2_encode_image(img, jpeg_quality)
    jpeg_decode_func = lambda buf: utils.cv2_decode_image_buffer(buf)

# A lambda function to get a cv2 image
# encoded as a JPEG compressed byte sequence
grabber = video_grabber.VideoGrabber(jpeg_quality, args.encoder, resize_factor)
grabber.start()

get_buffer = lambda: grabber.get_buffer()
#get_buffer = lambda: utils.encode_image(cv2.imread("monarch.png",cv2.IMREAD_UNCHANGED), jpeg, jpeg_quality)

# A temporary buffer in which the received data will be copied
# this prevents creating a new buffer all the time
tmp_buf = bytearray(7)
tmp_view = memoryview(tmp_buf) # this allows to get a reference to a slice of tmp_buf

# Creates a temporary buffer which can hold the largest image we can transmit
img_buf = bytearray(9999999)
img_view = memoryview(img_buf)

idx = 0
t0  = time.time()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((host, port))
    while keep_running:

        # Grab and encode the image
        img_buffer = get_buffer()
        if img_buffer is None:
            continue

        # Prepare the message with the number of bytes going to be sent
        msg = bytes("image{:07}".format(len(img_buffer)), "ascii")

        utils.send_data(sock, msg)

        # Send the buffer
        utils.send_data(sock, img_buffer)

        # Read the reply command
        utils.recv_data_into(sock, tmp_view[:5], 5)
        cmd = tmp_buf[:5].decode('ascii')

        if cmd != 'image':
            raise RuntimeError("Unexpected server reply")

        # Read the image buffer size
        utils.recv_data_into(sock, tmp_view, 7)
        img_size = int(tmp_buf.decode('ascii'))

        # Read the image buffer
        utils.recv_data_into(sock, img_view[:img_size], img_size)

        # Read the final handshake
        cmd = utils.recv_data(sock, 5).decode('ascii')
        if cmd != 'enod!':
            raise RuntimeError("Unexpected server reply. Expected 'enod!', got '{}'".format(cmd))

        # Transaction is done, we now process/display the received image
        img = jpeg_decode_func(img_view[:img_size])
        cv2.imshow("Image", img)
        keep_running = not(cv2.waitKey(1) & 0xFF == ord('q'))
        if not keep_running:
            sock.sendall('quit!'.encode('ascii'))

        idx += 1
        if idx == 30:
            t1 = time.time()
            sys.stdout.write("\r {:.3} images/second ; msg size : {}    ".format(30/(t1-t0), img_size))
            sys.stdout.flush()
            t0 = t1
            idx = 0
    print()
    print("Closing the socket")
    print("Stopping the grabber")
    grabber.stop()

