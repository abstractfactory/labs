"""Process incoming envelope and output a response envelope

Benefit of dnyamic registry:
    - Inheritance, log all processes in one go, uniformly

"""

from __future__ import absolute_import

# standard library
import sys
import time
import traceback

# local library
import chat.protocol
import chat.service
import chat.lib

__all__ = [
]


class Factory(object):
    __metaclass__ = chat.lib.DynamicRegistry

    def mediate(self, typ, receiver, envelope):
        try:
            mediator = self.registry[typ.lower()]()
            mediator.execute(receiver, envelope)
        except KeyError:
            raise ValueError("Unhandled mediate: %s" % typ.lower())

    def publish(self, receiver, envelope):
        receiver.publish(envelope)

        name = "%s.%s" % (__name__, type(self).__name__)
        log = chat.protocol.Log(
            name=name,
            author=envelope.author,
            level='info',
            string='{} was published'.format(envelope.type),
            trace=envelope.trace)

        receiver.log(log)

    def execute(self, receiver, envelope):
        envelope.trace += ['mediate.letter']


class Letter(Factory):
    """Mediate message sent from PEER
     ______
    |\    /|
    | \  / |
    |  \/  |
    |______|

    """

    def execute(self, receiver, envelope):
        super(Letter, self).execute(receiver, envelope)

        if not envelope.author in receiver.letters:
            receiver.letters[envelope.author] = {}

        # Maintain all original authors
        receiver.peers.add(envelope.author)

        author = envelope.author
        timestamp = envelope.timestamp
        receiver.letters[author][timestamp] = envelope.to_dict()

        self.publish(receiver, envelope)


class StateQuery(Factory):
    def execute(self, receiver, envelope):
        super(StateQuery, self).execute(receiver, envelope)

        query = envelope.payload

        threads = {}
        for author in query:
            state = receiver.letters.get(author, {})
            threads.update(state)

        envelope = chat.protocol.Envelope(author=envelope.author,
                                          payload=threads,
                                          recipients=[envelope.author],
                                          type='state')

        self.publish(receiver, envelope)


class PeersQuery(Factory):
    def execute(self, receiver, envelope):
        super(PeerQuery, self).execute(receiver, envelope)

        peers = list(receiver.peers)
        envelope = chat.protocol.Envelope(author=envelope.author,
                                          payload=peers,
                                          recipients=[envelope.author],
                                          type='peers')
        self.publish(receiver, envelope)


class Invitation(Factory):
    def execute(self, receiver, envelope):
        envelope.trace += ['mediate.invitation']

        invitation = envelope.payload
        envelope = chat.protocol.Envelope(author=envelope.author,
                                          payload=invitation,
                                          recipients=invitation,
                                          type='invitation',
                                          trace=envelope.trace)
        print "%s inviting %s" % (envelope.author, invitation)

        receiver.peers.update(invitation)
        receiver.peers.add(envelope.author)

        self.publish(receiver, envelope)


class OrderPlacement(Factory):
    def execute(self, receiver, envelope):
        """Place an order via SWARM

        Your options are:
            coffee
            chocolate

        """

        order = envelope.payload
        item, args = order[0], order[1:]

        prices = {'coffee': 2.10,
                  'chocolate': 0.30}

        trace = envelope.trace
        trace += ["%s.%s<%s>" % (__name__,
                                 type(self).__name__,
                                 item)]

        out_envelope = chat.protocol.Envelope(
            author=envelope.author,
            payload=None,
            recipients=[envelope.author],
            type='error',
            trace=trace)

        if item == 'status':
            orders = args or chat.service.orders.keys()
            statuses = {}

            for order in orders:
                try:
                    order_ = chat.service.orders[int(order)]
                    statuses[order] = order_.status
                except KeyError:
                    statuses[order] = 'no order found'

            out_envelope.payload = statuses
            out_envelope.type = 'orderStatus'

        elif item == 'coffee':
            parser = chat.lib.ArgumentParser(prog='order coffee')
            parser.add_argument("name")
            parser.add_argument("--quantity", default=1)
            parser.add_argument("--milk", dest="milk", action="store_true")
            parser.add_argument("--size", default='regular')
            parser.add_argument("--no-milk",
                                dest="milk",
                                action="store_false")
            parser.add_argument("--takeaway",
                                dest="location",
                                action="store_false",
                                default=True)

            parsed = None

            try:
                parsed = parser.parse_args(args).__dict__

            except ValueError:
                out_envelope.payload = parser.format_help()

            except SystemExit:
                # Parser exited without error (e.g. to return help)
                pass

            if parsed:
                location = parsed.pop('location')
                price = prices['coffee'] * int(parsed['quantity'])

                item = chat.protocol.Coffee(**parsed)
                order = chat.protocol.Order(item,
                                            location='takeaway',
                                            cost=prices['coffee'])

                # Execute order

                try:
                    order = chat.service.order_coffee(order)
                    result = order.to_dict()

                except Exception as e:
                    sys.stderr.write(traceback.format_exc())
                    out_envelope.payload = "Error: %s" % e

                else:
                    out_envelope.payload = result
                    out_envelope.type = 'orderReceipt'

        elif item == 'chocolate':
            parser = chat.lib.ArgumentParser(prog='order chocolate')
            parser.add_argument("name")
            parser.add_argument("--quantity", default=1)
            parser.add_argument("--dark",
                                dest="shade",
                                action="store_const",
                                const='dark',
                                default='dark')
            parser.add_argument("--white",
                                dest="shade",
                                action="store_const",
                                const='white',
                                default='dark')
            parser.add_argument("--takeaway",
                                dest="location",
                                action="store_false",
                                default=True)

            parsed = None

            try:
                parsed = parser.parse_args(args).__dict__

            except ValueError:
                out_envelope.payload = parser.format_help()

            except SystemExit:
                # Parser exited without error (e.g. to return help)
                pass

            if parsed:
                location = parsed.pop('location')
                price = prices['chocolate'] * int(parsed['quantity'])

                item = chat.protocol.Chocolate(**parsed)
                order = chat.protocol.Order(item,
                                            location=location,
                                            cost=price)

                # Execute order

                try:
                    order = chat.service.order_chocolate(order)
                    result = order.to_dict()

                except Exception as e:
                    sys.stderr.write(traceback.format_exc())
                    out_envelope.payload = "Error: %s" % e

                else:
                    out_envelope.payload = result
                    out_envelope.type = 'receipt'

        else:
            out_envelope.payload = 'Could not order "%s"' % item

        self.publish(receiver, out_envelope)


class PeerQuery(Factory):
    def execute(self, receiver, envelope):
        """Swarm queries peer

        PEER A
         _             SWARM
        | |   query     _
        | |----------->|\|
        | |            |\|             PEER B
        | |            |\|    query     _
        | |            |\|============>| |
        | |            |\|             | |
        | |            |\|             | |
        | |            |\|             | |
        | |            |\|             | |
        | |            |\|    stats    | |
        | |            |\|<------------|_|
        | |            |\|
        | |   stats    |\|
        | |<-----------|_|
        |_|

        """

        envelope.trace += ['mediate.peer_query']

        peers, query = envelope.payload
        envelope = chat.protocol.Envelope(author=envelope.author,
                                          payload=query,
                                          recipients=peers,
                                          type='__swarmQuery__',
                                          trace=envelope.trace)

        self.publish(receiver, envelope)


class PeerResults(Factory):
    key = '__peerresults__'

    def execute(self, receiver, envelope):
        """Results have been returned from peer, mediate it

        PEER A
         _             SWARM
        | |   query     _
        | |----------->|\|
        | |            |\|             PEER B
        | |            |\|    query     _
        | |            |\|------------>| |
        | |            |\|             | |
        | |            |\|             | |
        | |            |\|             | |
        | |            |\|             | |
        | |            |\|    stats    | |
        | |            |\|<------------|_|
        | |            |\|
        | |   stats    |\|
        | |<===========|_|
        |_|

        """

        envelope.trace += ['mediate.peer_results']

        print "peer_results: %s" % envelope.to_dict()
        results = chat.protocol.QueryResults.from_dict(envelope.payload)
        envelope = chat.protocol.Envelope(author=results.peer,
                                          payload=results,
                                          recipients=[results.questioner],
                                          type='__queryResults__',
                                          trace=envelope.trace)
        self.publish(receiver, envelope)


class Heartbeat(Factory):
    def execute(self, receiver, envelope):
        """Update peer status"""
        receiver.heartbeats[envelope.author] = time.time()
