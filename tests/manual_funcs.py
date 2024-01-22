# Basic tests for RTM data feed

import zmq
import numpy as np
import time


def main_datapacket():

    ctx = zmq.Context()
    sock = ctx.socket(zmq.PUB)
    sock.bind('tcp://127.0.0.1:25010')

    while True:
        v = np.random.randn(580 + 80).astype('<f4') + 1.0
        v[-80:] = 0.0
        sock.send_multipart((b'RTMFRAME', v.tobytes()))
        time.sleep(.01)
