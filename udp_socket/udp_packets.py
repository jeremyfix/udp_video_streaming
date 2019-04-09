import math

class UdpPacket:

    header_size = 16 # in bytes

    def __init__(self, msg_idx: int, pkt_idx: int, num_pkts: int, data: memoryview):
        self.msg_idx = msg_idx     # The current message idx
        self.pkt_idx = pkt_idx     # The current packet idx
        self.num_pkts = num_pkts   # The total number of packets
        self.data = data           # The data buffer
        self.header = self.msg_idx.to_bytes  (4, 'big')+\
                      self.pkt_idx.to_bytes  (4, 'big')+\
                      self.num_pkts.to_bytes (4, 'big')+\
                      len(self.data).to_bytes(4, 'big')


    def decode(msg: bytes):
        msg_idx   = int.from_bytes(msg[:4],    'big')
        pkt_idx   = int.from_bytes(msg[4:8],   'big')
        num_pkts  = int.from_bytes(msg[8:12],   'big')
        data_size = int.from_bytes(msg[12:16], 'big')

        p = UdpPacket(msg_idx, pkt_idx, num_pkts, msg[16:16+data_size])
        return p

    def encode(self):
        return self.header + self.data

class UdpPacketsHandler:

    def __init__(self):
        self.current_msg_idx = None
        self.packets = []
        self.awaited_packets = None


    def process_packet(self, p: UdpPacket):
        if (self.current_msg_idx is None) or\
           (p.msg_idx > self.current_msg_idx):
            # This is the first time we receive a packet
            # or we get more recent packets and therefore drop all the
            # packets collected so far
            self.current_msg_idx = p.msg_idx
            self.packets = [b''] * p.num_pkts
            self.awaited_packets = p.num_pkts

        if p.msg_idx < self.current_msg_idx:
            # Drop the frame if too old
            return

        # We now place the current piece at the right place
        self.packets[p.pkt_idx] = p.data
        self.awaited_packets -= 1

        # If we collected all the packets, we can build up the full message
        if self.awaited_packets == 0:
            return b''.join(self.packets)

    def split_data(msg_idx: int, data: bytes, max_packet_size: int):
        """
        return : a list of UdpPacket ready to be sent
        """

        data_chunk_size = max_packet_size - UdpPacket.header_size
        num_packets = math.ceil(len(data) / data_chunk_size)
        packets = []

        # We build a memory view to a get 0 copy
        dataview = memoryview(data)

        print("Building {} packets".format(num_packets))

        for i in range(num_packets - 1):
            packets.append(UdpPacket(msg_idx, i, num_packets, dataview[i*data_chunk_size:(i+1)*data_chunk_size]))
        # The last packet
        packets.append(UdpPacket(msg_idx, num_packets - 1, num_packets, dataview[(num_packets-1)*data_chunk_size:]))
        return packets


if __name__ == '__main__':

    import random
    import utils
    import cv2

    img = cv2.imread('monarch.png')

    # Build up a collection of messages
    packets = []

    img0_jpeg = utils.cv2_encode_image(img, 10)
    img1_jpeg = utils.cv2_encode_image(img, 100)

    packets += UdpPacketsHandler.split_data(msg_idx=0, data=img0_jpeg, max_packet_size=2048)
    packets += UdpPacketsHandler.split_data(msg_idx=1, data=img1_jpeg, max_packet_size=60000)

    # Shuffle the packets to see if we can handle disordered packets
    random.shuffle(packets)

    print("A total of {} packets are considered sequentially".format(len(packets)))
    #

    packet_processor = UdpPacketsHandler()
    for p in packets:
        data = packet_processor.process_packet(p)
        if data is not None:
            print("Got a frame !")
            img = utils.cv2_decode_image_buffer(data)
            cv2.imshow('Image', img)
            cv2.waitKey()


