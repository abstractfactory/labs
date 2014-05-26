"""The display part of a simply two process chat app."""

import zmq


def main(addrs):

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, "")
    for addr in addrs:
        print "Connecting to: ", addr
        socket.connect(addr)

    while True:
        msg = socket.recv_pyobj()
        print "%s: %s" % (msg[1], msg[0])


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print "usage: display.py <address> [,<address>...]"
        raise SystemExit
    main(sys.argv[1:])
