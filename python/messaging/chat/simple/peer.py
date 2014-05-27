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


def spawn(func, **kwargs):
    thread = threading.Thread(target=func, **kwargs)
    thread.daemon = True
    thread.start()


class Peer(object):
    """Peer API"""

    def __init__(self, author, peers):
        self.author = author
        self.peers = peers

        push = context.socket(zmq.PUSH)
        push.connect("tcp://192.168.1.2:5555")

        sub = context.socket(zmq.SUB)
        sub.setsockopt(zmq.SUBSCRIBE, '')
        sub.connect("tcp://192.168.1.2:5556")

        self.push = push
        self.sub = sub

        spawn(self.listen, name='listen')
        self.catchup()

    def start(self):
        while True:
            try:
                sys.stdout.write("%s> " % self.author)
                command = raw_input()

                if not command:
                    continue

                self.mediate(command)

            except KeyboardInterrupt:
                print "\nGood bye"
                break

            except Exception as e:
                print e
                break

    def catchup(self):
        """Request current state of messages already sent to `Peer`"""
        state = protocol.StateRequest(data=self.peers)
        self.send(state)

    def send(self, payload):
        envelope = protocol.Envelope(author=self.author,
                                     body=payload,
                                     recipients=self.peers)
        self.push.send_json(envelope.dump())

    def display(self, envelope=None):
        if envelope:
            sys.stdout.write("\r{0}: {1}".format(envelope.author,
                                                 envelope.body.data))
        sys.stdout.write(" " * 10)  # Clear line
        sys.stdout.write("\n%s> " % author)

    def listen(self):
        """Receive and display incoming letters"""
        while True:
            message = self.sub.recv_json()
            assert message.get('type') == 'envelope'
            envelope = protocol.Envelope.from_message(message)

            # Only care about letters to this peer
            if not self.author in envelope.recipients:
                continue

            if type(envelope.body) is protocol.Letter:
                # If the incoming message is from a new peer,
                # include this peer in list of mediate recipients.
                if not envelope.author in self.peers:
                    self.peers.append(envelope.author)

                if envelope.author != self.author:
                    self.display(envelope)

            elif type(envelope.body) is protocol.AllServices:
                print "Command received"

            elif type(envelope.body) is protocol.Invitation:
                invitation = envelope.body
                print "%s is inviting you" % invitation.data

            elif type(envelope.body) is protocol.StateReply:
                state = envelope.body
                messages = state.data

                for timestamp in sorted(messages):
                    message = messages[timestamp]
                    envelope = protocol.Envelope.from_message(message)

                    if self.author in envelope.recipients:
                        self.display(envelope)
                        time.sleep(0.01)

            else:
                print "Message not recognised: %r" % envelope

    def mediate(self, command):
        """Resolve command and send

        Example:
            markus> say hi
            = mediate(command='say hi')

        """

        parts = command.split()
        action, args = parts[0], parts[1:]

        if action == 'invite':
            self.peers.extend(args)

            # Inform swarm that peer is listening
            invite = protocol.Invitation(data=args)
            self.send(invite)

        elif action == 'state':
            state_request = protocol.StateRequest(data=args or [])
            self.send(state_request)

        else:
            letter = protocol.Letter(data=command)
            self.send(letter)


# class Services(object):
#     def funny_pic(self):
#         return "-------> Funny pic <--------"


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        author, peers = sys.argv[1], sys.argv[2:]

        clear_console()
        peer = Peer(author, peers)
        peer.start()

    else:
        print "Usage: client.py my_name peer1_name peer2_name ..."
