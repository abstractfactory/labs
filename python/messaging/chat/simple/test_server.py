import sys
import zmq
import time

context = zmq.Context()

producer = context.socket(zmq.ROUTER)
producer.set_hwm(2000)
producer.bind("tcp://*:5555")

mps = 0
t = 0

while True:
    ctime = time.time()
    producer.recv_multipart()[1]
    dtime = time.time() - ctime

    try:
        mps = 1 / dtime
    except ZeroDivisionError:
        pass

    t += dtime
    if t > 0.1:
        sys.stdout.write("\rmps: %s" % mps)
        t = 0
