
import cv2
import argparse
import socket
from time import sleep
import numpy as np

import video_grabber


parser = argparse.ArgumentParser()

parser.add_argument('--host', type=str, help='The IP of the echo server', required=True)
parser.add_argument('--port', type=int, help='The port on which the server is listening', required=True)
parser.add_argument('--jpeg_quality', type=int, help='The JPEG quality for compressing the reply', default=50)

args = parser.parse_args()

host = args.host
port = args.port

jpeg_quality = args.jpeg_quality
grabber = video_grabber.VideoGrabber(jpeg_quality)
grabber.start()
sleep(1)

get_buffer = lambda: grabber.get_buffer().tobytes()


def decode_image_buffer(img_buffer):
    #img_array = np.frombuffer(img_buffer, dtype=np.dtype('uint8'))
    img_array = np.array(list(img_buffer), dtype=np.dtype('uint8'))
    # Decode a colored image
    return cv2.imdecode(img_array, 1)

cv2.namedWindow("Image")

keep_running = True

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((host, port))
    while keep_running:
        # Grab and encode the image
        img_buffer = get_buffer()
        if img_buffer is None:
            continue

        # Prepare the message with the number of bytes going to be sent
        msg = bytes("image{:010}".format(len(img_buffer)), "ascii")
        sock.sendall(msg)
        # Send the buffer
        sock.sendall(img_buffer)
        sock.sendall('done!'.encode('ascii'))

        # Read the reply command
        cmd = sock.recv(5).decode('ascii')
        if cmd != 'image':
            raise RuntimeError("Unexpected server reply")
        # Read the image buffer size
        img_size = int(sock.recv(10).decode('ascii'))

        # Read the image buffer
        img_reply_bytes = sock.recv(img_size)

        # Read the final handshake
        cmd = sock.recv(5).decode('ascii')
        if cmd != 'done!':
            raise RuntimeError("Unexpected server reply. Expected 'done!', got '{}'".format(cmd))

        # Transaction is done, we now process/display the received image
        img = decode_image_buffer(img_reply_bytes)
        cv2.imshow("Image", img)
        keep_running = not(cv2.waitKey(1) & 0xFF == ord('q'))
    print("Closing the socket")

# Stopping the video grabber thread
grabber.stop()
