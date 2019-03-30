import socketserver
import sys

import argparse

import cv2
import numpy as np

def get_ip(interface_name):
        """Helper to get the IP adress of the running server
        """
        import netifaces as ni
        ip = ni.ifaddresses(interface_name)[2][0]['addr']
        return ip


def decode_image_buffer(img_buffer):
    #img_array = np.frombuffer(img_buffer, dtype=np.dtype('uint8'))
    img_array = np.array(list(img_buffer), dtype=np.dtype('uint8'))
    # Decode a colored image
    return cv2.imdecode(img_array, 1)

def encode_image(cv2_img):
    global encode_params
    result, buf = cv2.imencode('.jpg', cv2_img, encode_params)
    return buf.tobytes()

class MyTCPHandler(socketserver.BaseRequestHandler):

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


                # For fun, we play with the image
                # and make its negative
                cv2_img = decode_image_buffer(img_bytes)
                cv2_img = 255 - cv2_img
                img_bytes = encode_image(cv2_img)

                # Build up the reply encoding the image
                msg = bytes('image{:010}'.format(len(img_bytes)), "ascii")
                self.request.sendall(msg)
                self.request.sendall(img_bytes)
                self.request.sendall('done!'.encode('ascii'))

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

encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), args.jpeg_quality]

with socketserver.TCPServer((host, port), MyTCPHandler) as server:
    print("Server listening on {}:{}".format(host, port))
    server_running = True
    while server_running:
        server.handle_request()

