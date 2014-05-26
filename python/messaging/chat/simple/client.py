
import os
import zmq
import time
import threading
import subprocess

clear = lambda: subprocess.call('cls' if os.name == 'nt' else 'clear',
                                shell=True)
context = zmq.Context()


if __name__ == '__main__':
    import sys
    who, peers = sys.argv[1], sys.argv[2:]

    push = context.socket(zmq.PUSH)
    push.connect("tcp://localhost:5555")

    sub = context.socket(zmq.SUB)

    for peer in peers:
        sub.setsockopt(zmq.SUBSCRIBE, peer)

    sub.connect("tcp://localhost:5556")

    clear()

    def listen():
        while True:
            print "\r%s" % sub.recv()
            sys.stdout.write("%s> " % who)

    thread = threading.Thread(target=listen)
    thread.daemon = True
    thread.start()

    while True:
        sys.stdout.write("%s> " % who)
        says = raw_input()

        message = {
            'who': who,
            'time': time.asctime(),
            'action': 'says',
            'data': says
        }

        push.send_json(message)
