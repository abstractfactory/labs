from __future__ import absolute_import

import sys
import zmq
import time
import random

# Local library
import lib
import protocol
# import service

context = zmq.Context()

CORES = random.randint(1, 12)
MEMORY = random.randrange(0.0, 16000.0)


def local_stats():
    """Return stats from machine"""
    available_cores = CORES - random.randint(1, 12)
    if available_cores <= 0:
        available_cores = 0

    available_memory = MEMORY - random.randrange(0.0, 16000.0)
    if available_memory <= 0:
        available_memory = 0

    return {'cores': CORES,
            'available_cores': available_cores,
            'memory': MEMORY,
            'available_memory': available_memory}


class Peer(object):
    """Peer API"""

    def __init__(self, name='unknown', peers=None, services=None):
        self.name = name
        self.peers = set()  # Filled up below
        self.services = services or list()

        push = context.socket(zmq.PUSH)
        push.connect("tcp://localhost:5555")

        sub = context.socket(zmq.SUB)
        sub.setsockopt(zmq.SUBSCRIBE, '')
        sub.connect("tcp://localhost:5556")

        self.push = push
        self.sub = sub

        lib.spawn(self.listen, name='listen')

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
            message = self.sub.recv_json()
            envelope = protocol.Envelope.from_dict(message)
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

        if type == 'letter':
            # If the incoming message is from a new peer,
            # include this peer in list of route_command recipients.
            self.peers.add(envelope.author)

            if envelope.author != self.name:
                message = self.formatter(envelope)
                self.display_remote_message(message)

        elif type == 'service':
            result = envelope.payload
            self.display_remote_message("%s" % result)

        elif type == 'receipt':
            order = protocol.Order.from_dict(envelope.payload)
            dic = order.to_dict()

            message = "Your receipt:\n"
            message += lib.pformat(dic, level=1)

            self.display_remote_message(message)

        elif type == 'status':
            statuses = envelope.payload
            message = "Status:"
            for id, status in sorted(statuses.iteritems()):
                message += '\n  {id}: {status}'.format(
                    id=id,
                    status=status)
            self.display_remote_message(message)

        elif type == 'services':
            query = envelope.payload
            self.display_remote_message(query)

        elif type == 'invitation':
            invitation = envelope.author
            self.peers.add(invitation)
            self.display_remote_message("%s invited you" % invitation)

        elif type == 'state':
            state = envelope.payload
            messages = state

            for timestamp in sorted(messages):
                message = messages[timestamp]
                envelope = protocol.Envelope.from_dict(message)

                if self.name in envelope.recipients:
                    message = self.formatter(envelope)
                    self.display_remote_message(message)
                    time.sleep(0.01)

        elif type == 'peers':
            peers = envelope.payload
            message = 'All peers:'

            for peer in peers:
                message += "\n    %s" % peer

            self.display_remote_message(message)

        elif type == 'error':
            error = envelope.payload
            self.display_remote_message(str(error))

        elif type == '__swarmQuery__':
            """Peer answers swarm (computer-to-computer)

            PEER A
             _             SWARM
            | |   query     _
            | |----------->| |
            | |            | |             PEER B
            | |            | |    query     _
            | |            | |------------>|\|
            | |            | |             |\|
            | |            | |             |\|
            | |            | |             |\|
            | |            | |             |\|
            | |            | |    stats    |\|
            | |            | |<============|_|
            | |            | |
            | |   stats    | |
            | |<-----------|_|
            |_|

            """
            envelope.payload.pop('type')
            query = protocol.Query.from_dict(envelope.payload)

            self.display_remote_message("- %s is asking about you"
                                        % query.questioner)

            if query.name == 'stats':

                services = []
                for service in self.services:
                    services.append(service.__name__)

                statistics = {'mood': 'happy',
                              'services': services}
                statistics.update(local_stats())

                # construct results
                results = {
                    'peer': self.name,
                    'stats': statistics,
                    'questioner': query.questioner,
                }

                # Return results in a peerResults envelope
                envelope = protocol.Envelope(payload=results,
                                             type='__peerResults__')
                self.send(envelope)

            elif query.name == 'sing':
                self.display_local_message("Singing")

            else:
                self.display_local_message("Got an odd query: %s" % query)

        elif type == '__queryResults__':
            """Display results of query (computer-to-computer)

            PEER A
             _             SWARM
            |\|   query     _
            |\|----------->| |
            |\|            | |             PEER B
            |\|            | |    query     _
            |\|            | |------------>| |
            |\|            | |             | |
            |\|            | |             | |
            |\|            | |             | |
            |\|            | |             | |
            |\|            | |    stats    | |
            |\|            | |<------------|_|
            |\|            | |
            |\|   stats    | |
            |\|<===========|_|
            |_|

            """

            results = envelope.payload
            print "__queryResults__: displaying results: %s" % results

            type = results['type']

            if type == 'stats':
                print "Received: %s" % results
                stats = results['stats']

                message = "\n%s <Statistics>:\n" % results['peer'].title()
                message += lib.pformat(stats, level=1, title=True)
                self.display_remote_message(message)
            else:
                self.display_remote_message("Got results, but don't know "
                                            "what for?: %s" % results)

        else:
            self.display_remote_message("Message not recognised: %r"
                                        % type)

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

        if command == 'say':
            instant_message = " ".join(args)
            peers = list(self.peers)
            letter = protocol.Envelope(payload=instant_message,
                                       type='letter',
                                       recipients=peers)
            self.send(letter)

        elif command == 'invite':
            peers = args
            self.peers.update(peers)

            # Inform swarm that peer is listening
            invite = protocol.Envelope(payload=peers,
                                       type='invitation')
            self.send(invite)

        elif command == 'order':
            """Order a coffee"""
            order = args

            if not order:
                print "- Order what?"
                return

            envelope = protocol.Envelope(payload=order,
                                         type='orderPlacement')
            self.send(envelope)

        elif command == 'peer':
            """Ask PEER for something

            PEER A
             _             SWARM
            |\|   query     _
            |\|===========>| |
            |\|            | |             PEER B
            |\|            | |    query     _
            |\|            | |------------>| |
            |\|            | |             | |
            |\|            | |             | |
            |\|            | |             | |
            |\|            | |             | |
            |\|            | |    stats    | |
            |\|            | |<------------|_|
            |\|            | |
            |\|   stats    | |
            |\|<-----------|_|
            |_|

            """

            try:
                peers = [args[0]]
                name = args[1]
                questioneer = self.name
                query = protocol.Query(name=name,
                                       questioner=questioneer,
                                       args=args[2:])

                envelope = protocol.Envelope(payload=(peers, query.to_dict()),
                                             type='peerQuery')
                self.send(envelope)

            except IndexError:
                self.display_local_message("Query not formatted correctly")

        elif command == 'peers':
            query = args[0] if args else None

            if query == 'all':
                allpeers = protocol.Envelope(type='peersQuery')
                self.send(allpeers)
            else:
                peers = self.peers
                message = 'Invited peers:'

                for peer in peers:
                    message += "\n    %s" % peer

                self.display_local_message(message)

        elif command == 'services':
            """Query peer for services"""
            peer = args[0] if args else None

            if peer:
                envelope = protocol.Envelope(payload=peer,
                                             type='servicesQuery')
                self.send(envelope)
            else:
                self.display_local_message("Who's services?")

        elif command == 'state':
            peers = args
            state_request = protocol.Envelope(payload=peers,
                                              type='stateQuery')
            self.send(state_request)

        elif command == 'stats':
            """Peer queries peer

            PEER A
             _             SWARM
            |\|   query     _
            |\|===========>| |
            |\|            | |             PEER B
            |\|            | |    query     _
            |\|            | |------------>| |
            |\|            | |             | |
            |\|            | |             | |
            |\|            | |             | |
            |\|            | |             | |
            |\|            | |    stats    | |
            |\|            | |<------------|_|
            |\|            | |
            |\|   stats    | |
            |\|<-----------|_|
            |_|

            """

            peers = args
            if peers:
                query = protocol.Query('stats', questioner=self.name)
                envelope = protocol.Envelope(payload=(peers, query.to_dict()),
                                             type='statsQuery')
                self.send(envelope)
            else:
                self.display_local_message("Which peer?")

        else:
            print "%r not a valid command" % command
