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

        # factory = chat.mediator.peer.Factory()

        # try:
        #     factory.process(type, self, envelope)
        # except ValueError:

        if type == 'letter':
            """Letter was sent from another PEER

            PEER A
             _             SWARM
            | |             _             PEER B
            | |            |/|             _
            | |            |/|            | |
            | |            |/|   letter   | |
            | |   letter   |/|<-----------|_|
            | |<===========|_|
            |_|

            """

            # If the incoming message is from a new peer,
            # include this peer in list of route_command recipients.
            self.peers.add(envelope.author)

            if envelope.author != self.name:
                message = self.formatter(envelope)
                self.display_remote_message(message)

        elif type == 'orderReceipt':
            """A receipt was returned from SWARM order. (event)

            PEER A
             _             SWARM
            | |             _
            | |            |/|
            | |            |/|
            | |            |/|
            | |  receipt   |/|
            | |<===========|_|
            |_|

            Note: messages are received indirectly, as a result
                  of an earlier/remote request.

            """

            order = chat.protocol.Order.from_dict(envelope.payload)
            dic = order.to_dict()

            message = "Your receipt:\n"
            message += chat.lib.pformat(dic, level=1)

            self.display_remote_message(message)

        elif type == 'orderStatus':
            """Order status was returned from SWARM order(s)

            PEER A
             _             SWARM
            | |   query     _
            | |----------->|/|
            | |            |/|
            | |            |/|
            | |   status   |/|
            | |<===========|_|
            |_|

            """

            statuses = envelope.payload
            message = "Status:"
            for id, status in sorted(statuses.iteritems()):
                message += '\n  {id}: {status}'.format(
                    id=id,
                    status=status)
            self.display_remote_message(message)

        elif type == 'invitation':
            """Invitation sent from another PEER

            PEER A
             _             SWARM
            | |             _             PEER B
            | |            |/|             _
            | |            |/|            | |
            | |            |/| invitation | |
            | | invitation |/|<-----------|_|
            | |<===========|_|
            |_|

            """

            invitation = envelope.author
            self.peers.add(invitation)
            self.display_remote_message("%s invited you" % invitation)

        elif type == 'state':
            """State was returned from SWARM

            PEER A
             _             SWARM
            | |   query     _
            | |----------->|/|
            | |            |/|
            | |            |/|
            | |   state    |/|
            | |<===========|_|
            |_|

            """

            state = envelope.payload
            messages = state

            for timestamp in sorted(messages):
                message = messages[timestamp]
                envelope = chat.protocol.Envelope.from_dict(message)

                if self.name in envelope.recipients:
                    message = self.formatter(envelope)
                    self.display_remote_message(message)
                    time.sleep(0.01)

        elif type == 'peers':
            """All peers was returned from swarm

            PEER A
             _             SWARM
            | |   query     _
            | |----------->|/|
            | |            |/|
            | |            |/|
            | |   peers    |/|
            | |<===========|_|
            |_|

            """
            peers = envelope.payload
            message = 'All peers:'

            for peer in peers:
                message += "\n    %s" % peer

            self.display_remote_message(message)

        elif type == 'error':
            """An error was received. (even)

            PEER A
             _             SWARM
            | |             _
            | |            |/|
            | |            |/|
            | |            |/|
            | |    error   |/|
            | |<===========|_|
            |_|

            Note: errors are received asynchronously

            """

            error = envelope.payload
            self.display_remote_message(str(error))

        elif type == '__swarmQuery__':
            """Peer answers swarm (computer-to-computer)

            PEER A
             _             SWARM
            | |   query     _             PEER B
            | |----------->|/|   query     _
            | |            |/|===========>| |
            | |            |/|            | |
            | |            |/|            |_|
            | |            |_|
            |_|

            """

            query = chat.protocol.Query.from_dict(envelope.payload)

            self.display_remote_message("- %s is asking about you"
                                        % query.questioner)

            if query.name == 'stats':
                """Swarm queries statistics"""
                statistics = chat.lib.local_stats()
                results = query.reply(peer=self.name,
                                      payload=statistics)
                trace = envelope.trace
                trace.append('Peer.processor<stats>')
                envelope = chat.protocol.Envelope(payload=results,
                                                  type='__peerResults__',
                                                  trace=trace)
                self.send(envelope)

            elif query.name == 'mood':
                """Swarm queries mood"""
                results = query.reply(peer=self.name,
                                      payload='happy')
                trace = envelope.trace
                trace.append('Peer.processor<mood>')
                envelope = chat.protocol.Envelope(payload=results,
                                                  type='__peerResults__',
                                                  trace=trace)
                self.send(envelope)

            elif query.name == 'service':
                """Perform service"""
                results = query.reply(peer=self.name,
                                      payload='Performed service')
                trace = envelope.trace
                trace.append('Peer.processor<service>')
                envelope = chat.protocol.Envelope(payload=results,
                                                  type='__peerResults__',
                                                  trace=trace)
                self.send(envelope)

            elif query.name == 'services':
                results = query.reply(peer=self.name,
                                      payload=self.services.keys())
                trace = envelope.trace
                trace.append('Peer.processor<services>')
                envelope = chat.protocol.Envelope(payload=results,
                                                  type='__peerResults__',
                                                  trace=trace)
                self.send(envelope)

            else:
                """Swarm queries something unknown"""
                results = query.reply(peer=self.name,
                                      payload=query.name)
                results.name = 'invalid'

                trace = envelope.trace
                trace.append('Peer.processor<unknown>')
                envelope = chat.protocol.Envelope(payload=results,
                                                  type='__peerResults__',
                                                  trace=trace)
                self.send(envelope)

        elif type == '__queryResults__':
            """Display results of query (computer-to-computer)

            PEER A
             _             SWARM
            | |             _             PEER B
            | |            |/|             _
            | |            |/|            | |
            | |            |/|   results  | |
            | |   results  |/|<-----------|_|
            | |<===========|_|
            |_|

            """

            results = envelope.payload
            results = chat.protocol.QueryResults.from_dict(results)

            if results.name == 'stats':
                """
                Display statistics returned from query

                CPU (ghz)
                CORES (n)
                MEMORY (mb)

                """

                stats = results.payload

                message = "\n%s <Statistics>:\n" % results.peer.title()
                message += chat.lib.pformat(stats, level=1, title=True)
                self.display_remote_message(message)

            elif results.name == 'mood':
                """
                    _     _
                   |_|   |_|
                  \_________/

                """

                self.display_remote_message(results.payload)

            elif results.name == 'service':
                self.display_remote_message(results.payload)

            elif results.name == 'services':
                services = results.payload

                if not services:
                    message = ("%s did not provide any services."
                               % results.peer.title())

                else:
                    message = "\n%s <Services>:\n" % results.peer.title()
                    for service_ in services:
                        title = service_.replace("_", " ")
                        title = title.title()
                        message += "    %s (%s)\n" % (title, service_)

                self.display_remote_message(message)

            elif results.name == 'invalid':
                self.display_remote_message(
                    "%s didn't know how to answer '%s'"
                    % (results.peer.title(), results.payload))

            else:
                self.display_remote_message(
                    "Got results for {query} from {peer}, but don't know "
                    "what for.".format(query=results.name,
                                       peer=results.peer))

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
            letter = chat.protocol.Envelope(
                payload=instant_message,
                type='letter',
                recipients=peers,
                trace=['Peer.route_command<say>'])
            self.send(letter)

        elif command == 'wait':
            time.sleep(args[0])

        elif command == 'invite':
            peers = args
            self.peers.update(peers)

            # Inform swarm that peer is listening
            invite = chat.protocol.Envelope(
                payload=peers,
                type='invitation',
                trace=['Peer.route_comamnd<invite>'])
            self.send(invite)

        elif command == 'order':
            """Place an order to the swarm

            PEER A
             _             SWARM
            |\|   order     _
            |\|===========>| |
            |\|            | |
            |\|            | |
            |\|     id     | |
            |\|<-----------|_|
            |_|

            Note: This will be delegated to dedicated WORKER instances.
            In the case of COFFEE, a BARISTA will provide such a service.

            """

            order = args

            if not order:
                return self.display_local_message("- Order what?")

            envelope = chat.protocol.Envelope(
                payload=order,
                type='orderPlacement',
                trace=['Peer.route_command<order>'])
            self.send(envelope)

        elif command == 'peer':
            """Ask PEER for something

            PEER A
             _             SWARM
            |\|   query     _
            |\|===========>| |             PEER B
            |\|            | |    query     _
            |\|            | |------------>| |
            |\|            | |             | |
            |\|            | |             | |
            |\|            | |             |_|
            |\|            |_|
            |_|

            """

            try:
                peers = [args[0]]
                name = args[1]
                questioneer = self.name
                query = chat.protocol.Query(name=name,
                                            questioner=questioneer,
                                            payload=args[2:])

                envelope = chat.protocol.Envelope(
                    payload=(peers, query.to_dict()),
                    type='peerQuery',
                    trace=['Peer.route_command<peer>'])
                self.send(envelope)

            except IndexError:
                self.display_local_message("Query not formatted correctly")

        elif command == 'peers':
            """Query all or invited peers"""
            query = args[0] if args else None

            if query == 'all':
                allpeers = chat.protocol.Envelope(type='peersQuery')
                self.send(allpeers)

            else:
                peers = self.peers
                message = 'Invited peers:'

                for peer in peers:
                    message += "\n    %s" % peer

                self.display_local_message(message)

        elif command == 'state':
            peers = args
            state_request = chat.protocol.Envelope(
                payload=peers,
                type='stateQuery',
                trace=['Peer.route_command<state>'])

            self.send(state_request)

        else:
            print "%r not a valid command" % command

    def heartbeat(self):
        envelope = chat.protocol.Envelope(author=self.name,
                                          type='heartbeat')
        while True:
            self.send(envelope)
            time.sleep(2)
