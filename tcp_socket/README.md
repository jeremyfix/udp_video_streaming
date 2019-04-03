This is a TCP client/server.

The client sends an image to the server which applies a processing and then sends back the result

To use it, run the server :

    python3 server.py --port 1081  --jpeg_quality 10

And then the client

    python3 client.py --host localhost --port 1081 --jpeg_quality 10
