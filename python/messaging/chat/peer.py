from __future__ import absolute_import

import sys
import zmq
import time
# import argparse

# Local library
import lib
import protocol
# import service

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
        self.push.send_json(envelope.to_dict())

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
            envelope = protocol.Envelope.from_dict(message)
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

        elif envelope.type == 'service':
            result = envelope.payload
            self.remote_display("%s" % result)

        elif envelope.type == 'ordered':
            order_id = protocol.OrderId.from_dict(envelope.payload)
            message = "Your receipt:\n"
            message += "  Order id: %s" % order_id.id
            self.remote_display(message)

        elif envelope.type == 'status':
            statuses = envelope.payload
            message = "Status:"
            for id, status in sorted(statuses.iteritems()):
                message += '\n  {id}: {status}'.format(
                    id=id,
                    status=status)
            self.remote_display(message)

        elif envelope.type == 'services':
            query = envelope.payload
            self.remote_display(query)

        elif envelope.type == 'invitation':
            invitation = envelope.payload
            print "%s is inviting you" % invitation

        elif envelope.type == 'state':
            state = envelope.payload
            messages = state

            for timestamp in sorted(messages):
                message = messages[timestamp]
                envelope = protocol.Envelope.from_dict(message)

                if self.author in envelope.recipients:
                    message = self.formatter(envelope)
                    self.remote_display(message)
                    time.sleep(0.01)

        elif envelope.type == 'peers':
            peers = envelope.payload
            message = 'All peers:\n'
            message += ' '.join(["  %s\n" % peer for peer in peers])
            self.remote_display(message)

        elif envelope.type == 'error':
            error = envelope.payload
            self.remote_display(error)

        else:
            self.remote_display("Message not recognised: %r" % envelope.type)

    def mediate(self, command):
        """Resolve command from shell and send
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

        elif action == 'order':
            """Order a coffee"""

            if not args:
                print "- Order what?"
                return

            envelope = protocol.Envelope(payload=args,
                                         type='order')
            self.send(envelope)

        elif action == 'services':
            query = args[0] if args else None
            envelope = protocol.Envelope(payload=query,
                                         type='queryServices')
            self.send(envelope)

        elif action == 'state':
            state_request = protocol.Envelope(payload=args,
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
