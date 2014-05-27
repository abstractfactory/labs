"""
   client     _           _      server
 __________   |           |    __________
|          |  |           |   |          |
|   PUSH   |----------------->|   PULL   |---
|__________|  |           |   |__________|   |
              |           |                  |
 _________    |           |    _________     |
|         |   |           |   |         |<---
|   SUB   |<------------------|   PUB   |
|_________|   |           |   |_________|
              |           |
 _________    |           |    _________
|         |------------------>|         |
|   REQ   |<------------------|   REP   |  # Server-queries
|_________|   |           |   |_________|
              |           |

All messages are sent to all clients.

The client then filters messages based on who he has chosen
to listen to.

"""

import os
import sys
import zmq
import time
import threading
import subprocess

clear_console = lambda: subprocess.call('cls'
                                        if os.name == 'nt'
                                        else 'clear',
                                        shell=True)
context = zmq.Context()


def spawn(func, name=None):
    thread = threading.Thread(target=func, name=name)
    thread.daemon = True
    thread.start()


def incoming():
    """Receive and write incoming letters"""
    while True:
        message = sub.recv_json()
        peer, authors, body = (message['from'],
                               message['to'],
                               message['message'])

        # If the incoming message is from a new peer,
        # include this peer in list of outgoing recipients.
        if not peer in peers:
            peers.append(peer)

        if peer != author and author in authors:
            sys.stdout.write("\r{0}: {1}".format(peer, body))
            sys.stdout.write(" " * 10)  # Clear line
            sys.stdout.write("\n%s> " % author)


def outgoing():
    """Send letters and commands"""
    while True:
        sys.stdout.write("%s> " % author)
        says = raw_input()

        if not says:
            continue

        parts = says.split()
        action, args = parts[0], parts[1:]

        message = {'author': author,
                   'time': time.time()}

        if action == 'listen':
            peers.extend(args)

            # Inform swarm that peer is listening
            message['action'] = 'listening'
            message['recipients'] = peers
            message['body'] = args
            push.send_json(message)

        elif action == 'state':
            message['action'] = 'state'
            req.send_json(message)
            state = req.recv_json()
            print "State is: %s" % state

        else:
            message['action'] = 'says'
            message['body'] = says
            message['recipients'] = peers

            push.send_json(message)


def state():
    # Establish current state
    letters = {}
    for peer in peers:
        req.send_json({
            'action': 'state',
            'author': peer
        })

        state = req.recv_json()
        letters.update(state)

    for timestamp in sorted(letters):
        letter = letters[timestamp]
        if author in letter['to']:
            sys.stdout.write("\r%s: %s\n" % (letter['from'],
                                             letter['message']))
            time.sleep(0.01)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        author, peers = sys.argv[1], sys.argv[2:]

        push = context.socket(zmq.PUSH)
        push.connect("tcp://localhost:5555")

        sub = context.socket(zmq.SUB)
        sub.setsockopt(zmq.SUBSCRIBE, '')
        sub.connect("tcp://localhost:5556")

        req = context.socket(zmq.REQ)
        req.connect("tcp://localhost:5557")

        clear_console()
        state()

        spawn(incoming, 'incoming')
        spawn(outgoing, 'outgoing')

        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print "\nGood bye"
                break

            except Exception as e:
                print e
                break

    else:
        print "Usage: client.py my_name peer1_name peer2_name ..."
