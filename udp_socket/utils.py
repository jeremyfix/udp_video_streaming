import cv2
import numpy as np

def cv2_decode_image_buffer(img_buffer):
    img_array = np.frombuffer(img_buffer, dtype=np.dtype('uint8'))
    # Decode a colored image
    return  cv2.imdecode(img_array, flags=cv2.IMREAD_UNCHANGED)

def cv2_encode_image(cv2_img, jpeg_quality):
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
    result, buf = cv2.imencode('.jpg', cv2_img, encode_params)
    return buf.tobytes()

def turbo_decode_image_buffer(img_buffer, jpeg):
	return jpeg.decode(img_buffer)

def turbo_encode_image(cv2_img, jpeg, jpeg_quality):
	return jpeg.encode(cv2_img, quality=jpeg_quality)

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
