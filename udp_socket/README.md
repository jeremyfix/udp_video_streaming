# Video streaming through UDP sockets

This repository provides a simple python implementation of video streaming through UDP sockets with JPEG compression. So far, it sends a single datagram. If the buffer is larger than what I think is the largest UDP datagram size, 65507, the client fails. 

A work in progress is to add an appropriate header to allow chunking an image into multiple datagrams.

# How to use it ?

In order to test it, run the server :

    python3 server.py --port 10080 

In another tab, start the client :

    python3 client.py --host localhost --port 10080

Pressing 'q' on the client side within the CV2 window will isue a quit command to the client and server.

