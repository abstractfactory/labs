from __future__ import absolute_import

# standard library
import time

# local library
import chat.lib
import chat.protocol

__all__ = [
    'Letter',
    'OrderReceipt',
    'OrderStatus',
    'Invitation',
    'State',
    'Peers',
    'Error',
    'SwarmQuery',
    'QueryResults'
]


class Factory(object):
    __metaclass__ = chat.lib.DynamicRegistry

    def mediate(self, typ, receiver, envelope):
        try:
            mediator = self.registry[typ.lower()]()
            mediator.execute(receiver, envelope)
        except KeyError:
            raise ValueError("Unhandled mediator: %s" % typ.lower())

    def execute(self, receiver, envelope):
        pass

    def send(self, receiver, envelope):
        receiver.send(envelope)


class Letter(Factory):
    def execute(self, receiver, envelope):
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

        Arguments:
            receiver (object) - object to operate upon
            envelope (chat.protocol.Envelope) - message to mediate

        """

        super(Letter, self).execute(receiver, envelope)

        # Include this (potentially new) peer in list
        # of recipients for future letters send by `self`.
        receiver.peers.add(envelope.author)

        if envelope.author != receiver.name:
            message = receiver.formatter(envelope)
            receiver.display_remote_message(message)


class OrderReceipt(Factory):
    def execute(self, receiver, envelope):
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

        receiver.display_remote_message(message)


class OrderStatus(Factory):
    def execute(self, receiver, envelope):
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
        receiver.display_remote_message(message)


class Invitation(Factory):
    def execute(self, receiver, envelope):
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
        receiver.peers.add(invitation)
        receiver.display_remote_message("%s invited you" % invitation)


class State(Factory):
    def execute(self, receiver, envelope):
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

            if receiver.name in envelope.recipients:
                message = receiver.formatter(envelope)
                receiver.display_remote_message(message)
                time.sleep(0.01)


class Peers(Factory):
    def execute(self, receiver, envelope):
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

        receiver.display_remote_message(message)


class Error(Factory):
    def execute(self, receiver, envelope):
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
        receiver.display_remote_message(str(error))


class SwarmQuery(Factory):
    key = '__swarmquery__'

    def execute(self, receiver, envelope):
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

        trace = envelope.trace
        trace.append('Peer.mediator<{}>'.format(query.name))

        receiver.display_remote_message("- %s is asking about you"
                                        % query.questioner)

        if query.name == 'stats':
            """Swarm queries statistics"""
            statistics = chat.lib.local_stats()
            results = query.reply(peer=receiver.name,
                                  payload=statistics)
            envelope = chat.protocol.Envelope(payload=results,
                                              type='__peerResults__',
                                              trace=trace)
            self.send(receiver, envelope)

        elif query.name == 'mood':
            """Swarm queries mood"""
            results = query.reply(peer=receiver.name,
                                  payload='happy')
            envelope = chat.protocol.Envelope(payload=results,
                                              type='__peerResults__',
                                              trace=trace)
            self.send(receiver, envelope)

        elif query.name == 'service':
            """Perform service"""
            results = query.reply(peer=receiver.name,
                                  payload='Performed service')
            envelope = chat.protocol.Envelope(payload=results,
                                              type='__peerResults__',
                                              trace=trace)
            self.send(receiver, envelope)

        elif query.name == 'services':
            results = query.reply(peer=receiver.name,
                                  payload=receiver.services.keys())
            envelope = chat.protocol.Envelope(payload=results,
                                              type='__peerResults__',
                                              trace=trace)
            self.send(receiver, envelope)

        elif query.name == 'status':
            # liveliness = receiver.heartbeats.get(self.name)
            results = query.reply(peer=self.name,
                                  payload='dead')
            envelope = chat.protocol.Envelope(payload=results,
                                              type='__peerResults__',
                                              trace=trace)
            self.send(receiver, envelope)

        else:
            """Swarm queries something unknown"""
            results = query.reply(peer=receiver.name,
                                  payload=query.name)
            results.name = 'invalid'
            envelope = chat.protocol.Envelope(payload=results,
                                              type='__peerResults__',
                                              trace=trace)
            self.send(receiver, envelope)


class QueryResults(Factory):
    key = '__queryresults__'

    def execute(self, receiver, envelope):
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
            receiver.display_remote_message(message)

        elif results.name == 'mood':
            """
                _     _
               |_|   |_|
              \_________/

            """

            receiver.display_remote_message(results.payload)

        elif results.name == 'service':
            receiver.display_remote_message(results.payload)

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

            receiver.display_remote_message(message)

        elif results.name == 'invalid':
            receiver.display_remote_message(
                "%s didn't know how to answer '%s'"
                % (results.peer.title(), results.payload))

        else:
            receiver.display_remote_message(
                "Got results for {query} from {peer}, but don't know "
                "what for.".format(query=results.name,
                                   peer=results.peer))
