# Video streaming through UDP sockets

This repository provides a simple python implementation of video streaming through UDP sockets with JPEG compression.

# How to use it ?

In order to test it, identify the interface on which the socket must be opened, say eth0, then run the server :

    python3 server.py eth0

Identify the IP adress to contact the server. When the server is running, the IP is displayed, e.g. 
"starting up on 192.168.0.39 port 1080"

In another tab, start the client :

    python3 client.py 192.168.0.39 1080

The server accepts two commands : get, quit .

If you wish to quit the server, simply send the command to it, in bash :

    echo -n "quit" > /dev/udp/192.168.0.39/1080

Or using netcat :

    echo -n "quit" | nc -u -q1 192.168.0.39 1080
