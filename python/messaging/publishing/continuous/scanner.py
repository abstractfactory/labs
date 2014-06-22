"""
The scanner is the one observing available publishers.

Scenario:
    There are a bunch of unknown publishers out there. Each publisher
    is advertising its name and address. We'll tap into the common
    topic and gather who is there.

"""

import zmq


if __name__ == '__main__':
    context = zmq.Context()

    socket = context.socket(zmq.PULL)
    socket.bind("tcp://*:5555")

    print "I: Scanning 5555"

    while True:
        message = socket.recv_multipart()
        print "I: Receiving: {}".format(message)
