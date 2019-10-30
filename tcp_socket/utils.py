# External modules
import cv2
import numpy as np
try:
    from turbojpeg import TurboJPEG
except ImportError:
    print("Warning, failed to import turbojpeg")


class CV2JpegHandler:
    """JPEG compression/decompression handled with CV2"""
    def __init__(self, jpeg_quality):
        self.encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]

    def compress(self, cv2_img):
        _, buf = cv2.imencode('.jpg', cv2_img, self.encode_params)
        return buf.tobytes()

    def decompress(self, img_buffer):
        img_array = np.frombuffer(img_buffer, dtype=np.dtype('uint8'))
        # Decode a colored image
        return cv2.imdecode(img_array, flags=cv2.IMREAD_UNCHANGED)


class TurboJpegHandler(object):
    """The object handling JPEG compression/decompression"""
    def __init__(self, jpeg_quality):
        self.jpeg_quality = jpeg_quality
        self.jpeg = TurboJPEG()

    def compress(self, cv2_img):
        return self.jpeg.encode(cv2_img, quality=self.jpeg_quality)

    def decompress(self, img_buffer):
        return self.jpeg.decode(img_buffer)


def make_jpeg_handler(name, jpeg_quality):
    if name == 'cv2':
        return CV2JpegHandler(jpeg_quality)
    elif name == 'turbo':
        return TurboJpegHandler(jpeg_quality)
    else:
        raise ValueError("Unknow Jpeg handler {}".format(name))


def send_data(sock, msg):
    totalsent = 0
    tosend = len(msg)
    while totalsent < tosend:
        numsent = sock.send(msg[totalsent:])
        if numsent == 0:
            raise RuntimeError("Socket connection broken")
        totalsent += numsent


def recv_data(sock, torecv):
    msg = b''
    while torecv > 0:
        chunk = sock.recv(torecv)
        if chunk == b'':
            raise RuntimeError("Socket connection broken")
        msg += chunk
        torecv -= len(chunk)
    return msg


def recv_data_into(sock, buf_view, torecv):
    while torecv > 0:
        numrecv = sock.recv_into(buf_view[-torecv:], torecv)
        if numrecv == 0:
            raise RuntimeError("Socket connection broken")
        torecv -= numrecv
