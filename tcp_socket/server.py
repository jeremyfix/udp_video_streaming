
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

class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server, jpeg_quality, image_process):
        self.jpeg_quality = jpeg_quality
        self.image_process = image_process
        super(MyTCPHandler, self).__init__(request, client_address, server)

    def handle(self):
        print("Connection established")
        while True:
            cmd = self.request.recv(5).decode('ascii')
            if cmd == 'image':
                # Read the number of bytes to be read
                buffer_size = int(self.request.recv(10).decode('ascii'))
                # Read the image buffer
                img_bytes = self.request.recv(buffer_size)

                cmd = self.request.recv(5).decode('ascii')
                if cmd != 'done!':
                    raise RuntimeError('Unexpected client info. Expected "done!", go "{}"'.format(cmd))

                # Decode the image
                cv2_img = utils.decode_image_buffer(img_bytes)
                # Make some processing on it
                cv2_img = self.image_process(cv2_img)
                # JPEG encode the result
                img_bytes = utils.encode_image(cv2_img, self.jpeg_quality)

                # Build up the reply encoding the image
                msg = bytes('image{:010}'.format(len(img_bytes)), "ascii")
                self.request.sendall(msg)
                self.request.sendall(img_bytes)
                self.request.sendall('enod!'.encode('ascii'))

            else:
                self.request.sendall('fail!'.encode('ascii'))
                break
        print("Connection closed")

parser = argparse.ArgumentParser()

parser.add_argument('--port', type=int, help='The port to contact the server', required=True)
parser.add_argument('--interface', type=str, help='The interface on which to listen', required=True)
parser.add_argument('--jpeg_quality', type=int, help='The JPEG quality for compressing the reply', default=50)
args = parser.parse_args()

host = get_ip(args.interface)
port = args.port


MyHandlerBuilder = lambda request, client_address, server: MyTCPHandler(request, client_address, server, args.jpeg_quality, image_process)

with socketserver.TCPServer((host, port), MyHandlerBuilder) as server:
    print("Server listening on {}:{}".format(host, port))
    server_running = True
    while server_running:
        server.handle_request()

