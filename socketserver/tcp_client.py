import cv2
import numpy as np
import socket
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--port', type=int, help='Port to contact the server', required=True)
parser.add_argument('--host', type=str, help='IP to contact the server', required=True)

args = parser.parse_args()

host = args.host
port = args.port


cv2.namedWindow("Image")

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((host, port))
        sock.sendall(bytes("get\n", "utf-8"))

        # Receive data from the server and shut down
        #received = str(sock.recv(1024), "utf-8")
        data = sock.makefile('rb').read()
        array = np.frombuffer(data, dtype=np.dtype('uint8'))
        img = cv2.imdecode(array, 1)
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Asking the server to quit")
            sock.sendall(bytes("quit\n", 'utf-8'))
            print("Quitting")
            break

