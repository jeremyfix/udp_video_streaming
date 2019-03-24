import cv2
import numpy as np
from threading import Thread, Lock
from time import sleep

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


if __name__ == '__main__':

    jpeg_quality = 10

    grabber = VideoGrabber(jpeg_quality)
    grabber.start()
    sleep(1)

    cv2.namedWindow("Image")

    for i in range(1000):
        data = grabber.get_buffer()
        if data is None:
            sleep(1)
            continue
        array = np.frombuffer(data, dtype=np.dtype('uint8'))
        img = cv2.imdecode(array, 1)
        cv2.imshow("Image", img)
        cv2.waitKey(1)

    print("Quitting")
    grabber.stop()

