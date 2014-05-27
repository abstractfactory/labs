from __future__ import absolute_import

# import os
import sys
import zmq
import time
# import subprocess

# Local library
import lib
import protocol

context = zmq.Context()


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

        lib.spawn(self.listen, name='listen')
        self.catchup()

    def catchup(self):
        """Request current state of messages already sent to `Peer`"""
        state = protocol.Envelope(payload=self.peers,
                                  type='staterequest')
        self.send(state)

    def send(self, envelope):
        envelope.author = self.author
        envelope.recipients = self.peers
        self.push.send_json(envelope.dump())

    def formatter(self, envelope):
        return "\r{0}: {1}".format(envelope.author,
                                   envelope.payload)

    def display(self, message=None):
        if message:
            sys.stdout.write(message)
            sys.stdout.write(" " * 10)  # Clear line
        sys.stdout.write("\n%s> " % author)

    def listen(self):
        """Receive and display incoming letters"""
        while True:
            message = self.sub.recv_json()
            envelope = protocol.Envelope.from_message(message)
            self.processor(envelope)

    def processor(self, envelope):
        if not self.author in envelope.recipients:
            return

        # Letter

        if envelope.type == 'letter':
            # If the incoming message is from a new peer,
            # include this peer in list of mediate recipients.
            if not envelope.author in self.peers:
                self.peers.append(envelope.author)

            if envelope.author != self.author:
                message = self.formatter(envelope)
                self.display(message)

        # Services

        elif envelope.type == 'allservices':
            print "Command received"

        # Invitation

        elif envelope.type == 'invitation':
            invitation = envelope.payload
            print "%s is inviting you" % invitation

        # State

        elif envelope.type == 'statereply':
            state = envelope.payload
            messages = state

            for timestamp in sorted(messages):
                message = messages[timestamp]
                envelope = protocol.Envelope.from_message(message)

                if self.author in envelope.recipients:
                    message = self.formatter(envelope)
                    self.display(message)
                    time.sleep(0.01)

        else:
            print "Message not recognised: %r" % envelope.type

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
            invite = protocol.Envelope(payload=args,
                                       type='invitation')
            self.send(invite)

        elif action == 'state':
            state_request = protocol.Envelope(payload=args or [],
                                              type='staterequest')
            self.send(state_request)

        elif action == 'say':
            letter = protocol.Envelope(payload=" ".join(args),
                                       type='letter')
            self.send(letter)

        elif action == 'peers':
            message = ', '.join(self.peers)
            self.display(message)
        else:
            print "Command not recognised"
