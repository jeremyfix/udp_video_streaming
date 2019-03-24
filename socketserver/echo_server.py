import socketserver
import sys

import argparse

# How to properly respond to "quit" ? and shutdown the server

def get_ip(interface_name):
        """Helper to get the IP adress of the running server
        """
        import netifaces as ni
        ip = ni.ifaddresses(interface_name)[2][0]['addr']
        return ip


import numpy as np
import cv2

cv2.namedWindow('Server')
def save_image(buf):
    array = np.frombuffer(buf, dtype=np.dtype('uint8'))
    img = cv2.imdecode(array, 1)
    cv2.imshow("Server", img)
    cv2.waitKey(1)


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        while True:
            print("Reading the command)")
            cmd = self.request.recv(5).decode('utf-8')
            print("Commande : " + cmd)
            cmd = self.request.recv(5).decode('utf-8')
            print("Commande : " + cmd)
            self.request.sendall('toto'.encode('utf-8'))

class MyTCPHandler2(socketserver.StreamRequestHandler):

    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        while True:
            print("Reading the command")
            command = self.rfile.readline().strip().decode('utf-8')
            if(command == 'quit'):
                print("Asked to quit")
                #?? self.server.request_shutdown()
                return
            elif(command == 'image'):
                print("image")
                img_buffer = self.rfile.readline()

                print(img_buffer.decode('utf-8'))
                self.wfile.write('yoop'.encode('utf-8'))
                #print("Show the image")
                #save_image(img_buffer)

                #print('Sending back the image')
                #self.wfile.write(img_buffer + "\n".encode('utf-8'))


parser = argparse.ArgumentParser()

parser.add_argument('--port', type=int, help='The port to contact the server', required=True)
parser.add_argument('--interface', type=str, help='The interface on which to listen', required=True)

args = parser.parse_args()

host = get_ip(args.interface)
port = args.port

with socketserver.TCPServer((host, port), MyTCPHandler) as server:
    print("Server listening on {}:{}".format(host, port))
    server_running = True
    while server_running:
        server.handle_request()
    #?? server.shutdown()

