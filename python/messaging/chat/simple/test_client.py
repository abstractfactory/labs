import zmq
import time
import random

context = zmq.Context()

consumer = context.socket(zmq.DEALER)
consumer.set_hwm(2000)
consumer.connect("tcp://localhost:5555")

messages = ['hello', 'world', 'something', 'else', '1', '2', '3']

while True:
    # msg = messages[random.randint(0, 6)]
    consumer.send_multipart([''])
    # time.sleep(random.random() * 0.001)
