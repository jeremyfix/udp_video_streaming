import cv2
import numpy as np

def decode_image_buffer(img_buffer):
    #img_array = np.frombuffer(img_buffer, dtype=np.dtype('uint8'))
    img_array = np.array(list(img_buffer), dtype=np.dtype('uint8'))
    # Decode a colored image
    return  cv2.imdecode(img_array, flags=cv2.IMREAD_UNCHANGED)

def encode_image(cv2_img, jpeg_quality):
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
    result, buf = cv2.imencode('.jpg', cv2_img, encode_params)
    return buf.tobytes()

