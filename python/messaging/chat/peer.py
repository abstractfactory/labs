from __future__ import absolute_import

# standard library
import sys
import json
import time

# dependencies
import zmq

# local library
import chat.lib
import chat.service
import chat.protocol
import chat.mediator.peer
import chat.router.peer

context = zmq.Context()


class Peer(object):
    """Peer API"""

    services = {'add': chat.service.add}

    def __init__(self,
                 name='unknown',
                 peers=None,
                 services=None):
        """
        Arguments:
            name(str): Name of author
            peers(list): Authors to chat with
            services(list): Exposed services

        """
        self.name = name
        self.peers = set()  # Filled up below

        push = context.socket(zmq.PUSH)
        push.connect("tcp://localhost:5555")

        sub = context.socket(zmq.SUB)
        sub.setsockopt(zmq.SUBSCRIBE, 'default')
        sub.connect("tcp://localhost:5556")

        self.push = push
        self.sub = sub

        chat.lib.spawn(self.listen, name='listen')
        chat.lib.spawn(self.heartbeat, name='heartbeat')

        # Catchup
        self.route_command('state')

        for peer in peers or []:
            self.route_command('invite %s' % peer)

    def send(self, envelope):
        envelope.author = self.name
        self.push.send_json(envelope.to_dict())

    def formatter(self, envelope):
        return "\r{0}: {1}".format(envelope.author,
                                   envelope.payload)

    def display_remote_message(self, message=None):
        self.display_local_message(message)
        self.init_shell()

    def display_local_message(self, message=None):
        sys.stdout.write("\r" + " " * 30)  # Clear line

        if message:
            sys.stdout.write("\r" + message + "\n")

    def init_shell(self):
        sys.stdout.write("%s> " % self.name)

    def listen(self):
        """Incoming messages event-loop

        Receive and display incoming messages.

        """

        while True:
            header, body = self.sub.recv_multipart()
            message = json.loads(body)
            envelope = chat.protocol.Envelope.from_dict(message)
            self.processor(envelope)

    def processor(self, envelope):
        """Process incoming envelope
                   ___________
        envelope  |           | local output
        --------->|  Process  |--------------->
                  |___________|

        """

        if not self.name in envelope.recipients:
            return

        type = envelope.type

        factory = chat.mediator.peer.Factory()

        try:
            factory.mediate(type, self, envelope)
        except ValueError as e:
            self.display_remote_message(str(e))

    def route_command(self, command):
        """Resolve command from shell and send to appropriate destination
                                       _
         _______        .------------>|_|---->
        |       |    ___|____
        |       |   |        |         _
        | shell |-->| router |------->|_|---->
        |       |   |________|
        |_______|       |              _
                        '------------>|_|---->

        Example:
            markus> say hi
            = route_command(command='say hi')

        Available commands:
            invite(peer)    - invite `peer` to conversation
            state           - retrieve state
            say(something)  - say `something` to invited peers
            peers           - list invited peers
            allpers         - list all available peers

        """

        parts = command.split()
        command, args = parts[0], parts[1:]

        factory = chat.router.peer.Factory()

        try:
            factory.route(command, self, args)
        except ValueError as e:
            self.display_local_message(str(e))

    def heartbeat(self):
        envelope = chat.protocol.Envelope(type='heartbeat',
                                          trace=['Peer.heartbeat'])

        while True:
            self.send(envelope)
            time.sleep(2)
