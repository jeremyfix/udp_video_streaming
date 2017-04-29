#!/usr/bin/env python
# coding: utf-8

import socket
import cv2
import numpy as np
import sys
import time

if(len(sys.argv) != 3):
    print("Usage : {} hostname port".format(sys.argv[0]))
    print("e.g.   {} 192.168.0.39 1080".format(sys.argv[0]))
    sys.exit(-1)


cv2.namedWindow("Image")

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = sys.argv[1]
port = int(sys.argv[2])
server_address = (host, port)

while(True):
    
    sent = sock.sendto("get", server_address)

    data, server = sock.recvfrom(30000)

    array = np.frombuffer(data, dtype=np.dtype('uint8'))
    img = cv2.imdecode(array, 1)
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("The client is quitting. If you wish to quite the server, simply call : \n")
print("echo -n \"quit\" > /dev/udp/{}/{}".format(host, port))
