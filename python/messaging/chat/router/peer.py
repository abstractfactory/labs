from __future__ import absolute_import

# standard library
import time

# local library
import chat.lib
import chat.protocol

__all__ = [
    'Say',
    'Wait',
    'Invite',
    'Order',
    'Peer',
    'Peers',
    'State'
]


class Factory(object):
    __metaclass__ = chat.lib.DynamicRegistry

    def route(self, command, receiver, args):
        try:
            processor = self.registry[command]()
            processor.route(receiver, args)
        except KeyError:
            raise ValueError("Unhandled route: %s" % command)


class Say(Factory):
    def route(self, receiver, args):
        instant_message = " ".join(args)
        peers = list(receiver.peers)
        letter = chat.protocol.Envelope(payload=instant_message,
                                        type='letter',
                                        recipients=peers,
                                        trace=['Peer.route_command<say>'])
        receiver.send(letter)


class Wait(Factory):
    def route(self, receiver, args):
        time.sleep(args[0])


class Invite(Factory):
    def route(self, receiver, args):
        peers = args
        receiver.peers.update(peers)

        # Inform swarm that peer is listening
        invite = chat.protocol.Envelope(
            payload=peers,
            type='invitation',
            trace=['Peer.route_comamnd<invite>'])
        receiver.send(invite)


class Order(Factory):
    def route(self, receiver, args):
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
            return receiver.display_local_message("- Order what?")

        envelope = chat.protocol.Envelope(
            payload=order,
            type='orderPlacement',
            trace=['Peer.route_command<order>'])
        receiver.send(envelope)


class Peer(Factory):
    def route(self, receiver, args):
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
            questioneer = receiver.name
            query = chat.protocol.Query(name=name,
                                        questioner=questioneer,
                                        payload=args[2:])

            envelope = chat.protocol.Envelope(
                payload=(peers, query.to_dict()),
                type='peerQuery',
                trace=['Peer.route_command<peer>'])
            receiver.send(envelope)

        except IndexError:
            receiver.display_local_message("Query not formatted correctly")


class Peers(Factory):
    def route(self, receiver, args):
        """Query all or invited peers"""
        query = args[0] if args else None

        if query == 'all':
            allpeers = chat.protocol.Envelope(type='peersQuery')
            receiver.send(allpeers)

        else:
            peers = receiver.peers
            message = 'Invited peers:'

            for peer in peers:
                message += "\n    %s" % peer

            receiver.display_local_message(message)


class State(Factory):
    def route(self, receiver, args):
        peers = args
        state_request = chat.protocol.Envelope(
            payload=peers,
            type='stateQuery',
            trace=['Peer.route_command<state>'])

        receiver.send(state_request)
