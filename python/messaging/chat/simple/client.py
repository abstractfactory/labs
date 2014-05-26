
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
    author, peers = sys.argv[1], sys.argv[2:]

    push = context.socket(zmq.PUSH)
    push.connect("tcp://localhost:5555")

    sub = context.socket(zmq.SUB)

    for peer in peers:
        sub.setsockopt(zmq.SUBSCRIBE, peer)

    sub.connect("tcp://localhost:5556")

    clear()

    def listen():
        while True:
            peer, data = sub.recv_multipart()
            sys.stdout.write("\r{0}: {1}".format(peer, data))
            sys.stdout.write(" " * 10)  # Clear line
            sys.stdout.write("\n%s> " % author)

    thread = threading.Thread(target=listen)
    thread.daemon = True
    thread.start()

    while True:
        sys.stdout.write("%s> " % author)
        says = raw_input()

        message = {'author': author,
                   'time': time.time()}

        parts = says.split()

        if parts[0] == 'listen':
            sys.stdout.write("\rNow also chatting with:\n")
            for peer in parts[1:]:
                sub.setsockopt(zmq.SUBSCRIBE, peer)
                sys.stdout.write("\t%s\n" % peer)

        elif parts[0] == 'mute':
            sys.stdout.write("\rMuting:\n")
            for peer in parts[1:]:
                sub.setsockopt(zmq.UNSUBSCRIIBE, peer)
                sys.stdout.write("\t%s\n" % peer)

        else:
            message['action'] = 'says'
            message['data'] = says

            push.send_json(message)
