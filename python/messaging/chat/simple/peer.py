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

The client then filters messages based on who he has
chosen to listen to.

"""
from __future__ import absolute_import

import os
import sys
import zmq
import time
import threading
import subprocess

# Local library
import protocol

clear_console = lambda: subprocess.call('cls'
                                        if os.name == 'nt'
                                        else 'clear',
                                        shell=True)
context = zmq.Context()


def spawn(func, name=None):
    thread = threading.Thread(target=func, name=name)
    thread.daemon = True
    thread.start()


def display(envelope=None):
    if envelope:
        sys.stdout.write("\r{0}: {1}".format(envelope.author,
                                             envelope.body.data))
    sys.stdout.write(" " * 10)  # Clear line
    sys.stdout.write("\n%s> " % author)


def incoming():
    """Receive and display incoming letters"""
    while True:
        message = sub.recv_json()
        assert message.get('type') == 'envelope'
        envelope = protocol.Envelope.from_message(message)

        # Only care about letters to this peer
        if not author in envelope.recipients:
            continue

        if type(envelope.body) is protocol.Letter:
            # If the incoming message is from a new peer,
            # include this peer in list of outgoing recipients.
            if not envelope.author in peers:
                peers.append(envelope.author)

            if envelope.author != author:
                display(envelope)

        elif type(envelope.body) is protocol.AllServices:
            print "Command received"

        elif type(envelope.body) is protocol.StateReply:
            state = envelope.body
            messages = state.data

            for timestamp in sorted(messages):
                message = messages[timestamp]
                envelope = protocol.Envelope.from_message(message)

                if author in envelope.recipients:
                    display(envelope)
                    time.sleep(0.01)

        else:
            print "Message not recognised: %r" % envelope


def outgoing(says):
    """Send letters and commands"""
    parts = says.split()
    header, remainder = parts[0], parts[1:]

    if header == 'invite':
        peers.extend(remainder)

        # Inform swarm that peer is listening
        # invite = protocol.Invitation(author=author,
        #                              body=remainder,
        #                              recipients=peers,
        #                              timestamp=time.time())
        # push.send_json(invite.dump())

    elif header == 'services':
        if not remainder:
            print "Your services: %s" % services.__dict__.keys()
        else:
            print "%s services: %s" % (remainder[0],
                                       services.__dict__.keys())

    elif header == 'state':
        state_request = protocol.StateRequest(data=remainder or [])
        envelope = protocol.Envelope(author=author,
                                     body=state_request,
                                     recipients=[author])
        push.send_json(envelope.dump())

    else:
        letter = protocol.Letter(data=says)
        envelope = protocol.Envelope(author=author,
                                     body=letter,
                                     recipients=peers)
        push.send_json(envelope.dump())


class Services(object):
    def funny_pic(self):
        return "-------> Funny pic <--------"


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        author, peers = sys.argv[1], sys.argv[2:]

        push = context.socket(zmq.PUSH)
        push.connect("tcp://192.168.1.2:5555")

        sub = context.socket(zmq.SUB)
        sub.setsockopt(zmq.SUBSCRIBE, '')
        sub.connect("tcp://192.168.1.2:5556")

        clear_console()
        services = Services()
        spawn(incoming, 'incoming')

        while True:
            try:
                sys.stdout.write("%s> " % author)
                says = raw_input()
                if not says:
                    continue
                outgoing(says)

            except KeyboardInterrupt:
                print "\nGood bye"
                break

            except Exception as e:
                print e
                break

    else:
        print "Usage: client.py my_name peer1_name peer2_name ..."
