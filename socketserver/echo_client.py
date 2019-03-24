
import cv2
import argparse
import socket
from time import sleep
import numpy as np

import video_grabber


parser = argparse.ArgumentParser()

parser.add_argument('--host', type=str, help='The IP of the echo server', required=True)
parser.add_argument('--port', type=int, help='The port on which the server is listening', required=True)

args = parser.parse_args()

host = args.host
port = args.port

jpeg_quality = 10
grabber = video_grabber.VideoGrabber(jpeg_quality)
grabber.start()
sleep(1)

get_buffer = lambda: grabber.get_buffer().tobytes()


cv2.namedWindow("Image")

keep_running = True

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((host, port))
    while keep_running:
        img_buffer = get_buffer()
        if img_buffer is None:
            continue

        msg = bytes("image"+len(img_buffer), "utf-8")
        sock.sendall(msg)

        print("Sending the image")
        #msg = img_buffer
        msg = bytes('stuff', 'utf-8')
        sock.sendall(msg)

        #print("Reading the message back")
        #data = sock.makefile('rb').readline()
        print("Reading the message back")
        data = sock.recv(4)
        print("Message : " + data.decode('utf-8'))
        #array = np.frombuffer(data, dtype=np.dtype('uint8'))
        #img = cv2.imdecode(array, 1)
        #print(img.height, img.width)
        #cv2.imshow("Image", img)
        #keep_running = not(cv2.waitKey(1) & 0&FF)
    #sock.close()
