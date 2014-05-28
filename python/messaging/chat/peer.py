from __future__ import absolute_import

import sys
import zmq
import time

# Local library
import lib
import protocol

context = zmq.Context()


class Peer(object):
    """Peer API"""

    def __init__(self, author, peers):
        self.author = author
        self.peers = list()

        push = context.socket(zmq.PUSH)
        push.connect("tcp://192.168.1.2:5555")

        sub = context.socket(zmq.SUB)
        sub.setsockopt(zmq.SUBSCRIBE, '')
        sub.connect("tcp://192.168.1.2:5556")

        self.push = push
        self.sub = sub

        lib.spawn(self.listen, name='listen')
        self.catchup()

        for peer in peers:
            self.mediate('invite %s' % peer)

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

    def remote_display(self, message=None):
        self.local_display(message)
        self.init_shell()

    def local_display(self, message=None):
        sys.stdout.write("\r" + " " * 30)  # Clear line

        if message:
            sys.stdout.write("\r" + message + "\n")

    def init_shell(self):
        sys.stdout.write("%s> " % self.author)

    def listen(self):
        """Incoming messages event-loop

        Receive and display incoming messages.

        """

        while True:
            message = self.sub.recv_json()
            envelope = protocol.Envelope.from_message(message)
            self.processor(envelope)

    def processor(self, envelope):
        """
                   ___________
        message   |           |
        --------->|  Process  |
                  |___________|
        """

        if not self.author in envelope.recipients:
            return

        if envelope.type == 'letter':
            # If the incoming message is from a new peer,
            # include this peer in list of mediate recipients.
            if not envelope.author in self.peers:
                self.peers.append(envelope.author)

            if envelope.author != self.author:
                message = self.formatter(envelope)
                self.remote_display(message)

        elif envelope.type == 'services':
            print "Command received"

        elif envelope.type == 'invitation':
            invitation = envelope.payload
            print "%s is inviting you" % invitation

        elif envelope.type == 'state':
            state = envelope.payload
            messages = state

            for timestamp in sorted(messages):
                message = messages[timestamp]
                envelope = protocol.Envelope.from_message(message)

                if self.author in envelope.recipients:
                    message = self.formatter(envelope)
                    self.remote_display(message)
                    time.sleep(0.01)

        elif envelope.type == 'peers':
            peers = envelope.payload
            message = 'All peers:\n'
            message += ' '.join(["  %s\n" % peer for peer in peers])
            self.remote_display(message)

        else:
            print "Message not recognised: %r" % envelope.type

    def mediate(self, command):
        """Resolve command and send
         ___________
        |           | send
        |  Command  |------>
        |___________|

        Example:
            markus> say hi
            = mediate(command='say hi')

        Available commands:
            invite(peer)    - invite `peer` to conversation
            state           - retrieve state
            say(something)  - say `something` to invited peers
            peers           - list invited peers
            allpers         - list all available peers

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
                                              type='queryState')
            self.send(state_request)

        elif action == 'say':
            letter = protocol.Envelope(payload=" ".join(args),
                                       type='letter')
            self.send(letter)

        elif action == 'peers':
            message = 'Invited peers:\n'
            message += ' '.join(["  %s\n" % peer for peer in self.peers])
            self.local_display(message)

        elif action == 'allpeers':
            allpeers = protocol.Envelope(type='queryPeers')
            self.send(allpeers)

        else:
            print "Command not recognised"
