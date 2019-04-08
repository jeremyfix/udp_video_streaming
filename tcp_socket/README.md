This is a TCP client/server.

The client sends an image to the server which applies a processing and then sends back the result

The image is encoded/decoded using [libjpeg-turbo python wrapper](https://github.com/lilohuang/PyTurboJPEG.git)

To use it, run the server :

    python3 server.py --port 1081  --jpeg_quality 10

And then the client

    python3 client.py --host localhost --port 1081 --jpeg_quality 10


[https://docs.python.org/3/howto/sockets.html](Python3 how to on sockets)

