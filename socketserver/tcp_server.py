import socketserver
import cv2
import sys
from threading import Thread, Lock
import sys

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

class VideoGrabber(Thread):
        """A threaded video grabber.

        Attributes:
        encode_params ():
        cap (str):
        attr2 (:obj:`int`, optional): Description of `attr2`.

        """
        def __init__(self, jpeg_quality):
                """Constructor.

                Args:
                jpeg_quality (:obj:`int`): Quality of JPEG encoding, in 0, 100.

                """
                Thread.__init__(self)
                self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
                self.cap = cv2.VideoCapture(0)
                self.running = True
                self.buffer = None
                self.lock = Lock()

        def stop(self):
                self.running = False

        def get_buffer(self):
                """Method to access the encoded buffer.

                Returns:
                np.ndarray: the compressed image if one has been acquired. None otherwise.
                """
                if self.buffer is not None:
                        self.lock.acquire()
                        cpy = self.buffer.copy()
                        self.lock.release()
                        return cpy

        def run(self):
                while self.running:
                        success, img = self.cap.read()
                        if not success:
                                continue

                        # JPEG compression
                        # Protected by a lock
                        # As the main thread may asks to access the buffer
                        self.lock.acquire()
                        result, self.buffer = cv2.imencode('.jpg', img, self.encode_param)
                        self.lock.release()


grabber = VideoGrabber(jpeg_quality)
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

