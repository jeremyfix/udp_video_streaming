import socketserver
import sys

import video_grabber

# How to properly handle the shutdown ??

if(len(sys.argv) != 2):
        print("Usage : {} interface".format(sys.argv[0]))
        print("e.g. {} eth0".format(sys.argv[0]))
        sys.exit(-1)


def get_ip(interface_name):
        """Helper to get the IP adresse of the running server
        """
        import netifaces as ni
        ip = ni.ifaddresses(interface_name)[2][0]['addr']
        return ip  # should print "192.168.100.37"

jpeg_quality = 100
host = get_ip(sys.argv[1])
port = 1080

grabber = video_grabber.VideoGrabber(jpeg_quality)
grabber.start()
get_message = lambda: grabber.get_buffer().tobytes()



class MyTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        command = self.rfile.readline().strip().decode('utf-8')

        if(command == 'quit'):
            print("Asked to quit")
            self.server.request_shutdown()
            return
            #raise Exception("End")
        elif(command == 'get'):
            print("Sent")
            self.wfile.write(get_message())

        # Likewise, self.wfile is a file-like object used to write back
        # to the client
        #self.wfile.write(self.data.upper())

    def finish(self):
        print("finishing....")

if __name__ == "__main__":

    # Create the server, binding to localhost on port 9999
    server_running = True
    with socketserver.TCPServer((host, port), MyTCPHandler) as server:
        while server_running:
            server.handle_request()
            print("Loop")
        server.shutdown()

