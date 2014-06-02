"""Process incoming envelope and output a response envelope"""

from __future__ import absolute_import

# standard library
import sys
import time
import traceback

# local library
import protocol
import service
import lib


def letter(self, in_envelope):
    in_envelope.trace += ['process.letter']

    # letter = in_envelope.payload

    if not in_envelope.author in self.letters:
        self.letters[in_envelope.author] = {}

    # Maintain all original authors
    self.peers.add(in_envelope.author)

    author = in_envelope.author
    timestamp = in_envelope.timestamp
    self.letters[author][timestamp] = in_envelope.to_dict()

    return in_envelope


def state_query(self, in_envelope):
    query = in_envelope.payload

    threads = {}
    for author in query:
        state = self.letters.get(author, {})
        threads.update(state)

    out_envelope = protocol.Envelope(author=in_envelope.author,
                                     payload=threads,
                                     recipients=[in_envelope.author],
                                     type='state')

    # log = protocol.Log(
    #     name='process.state_query',
    #     author=in_envelope.author,
    #     level='info',
    #     string='{} queried state'.format(in_envelope.author),
    #     trace=in_envelope.trace + ['process.state_query'],
    #     envelope=in_envelope)

    # self.log(log)

    return out_envelope


def peers_query(self, in_envelope):
    peers = list(self.peers)
    out_envelope = protocol.Envelope(author=in_envelope.author,
                                     payload=peers,
                                     recipients=[in_envelope.author],
                                     type='peers')
    return out_envelope


def invitation(self, in_envelope):
    in_envelope.trace += ['process.invitation']

    invitation = in_envelope.payload
    out_envelope = protocol.Envelope(author=in_envelope.author,
                                     payload=invitation,
                                     recipients=invitation,
                                     type='invitation',
                                     trace=in_envelope.trace)
    print "%s inviting %s" % (out_envelope.author, invitation)

    self.peers.update(invitation)
    self.peers.add(out_envelope.author)
    return out_envelope


# def services_query(self, in_envelope):
#     peer = in_envelope.payload

#     if peer:
#         try:
#             message = getattr(service, peer).__doc__
#         except AttributeError:
#             message = 'Sorry, service "%s" was not available' % peer
#     else:
#         services = service.services.keys()
#         message = 'Available swarm services:\n'
#         message += ' '.join(["  %s\n" % serv for serv in services])

#     out_envelope = protocol.Envelope(author=in_envelope.author,
#                                      payload=message,
#                                      recipients=[in_envelope.author],
#                                      type='services')
#     return out_envelope


def order_placement(self, in_envelope):
    """Place an order via SWARM

    Your options are:
        coffee
        chocolate

    """

    order = in_envelope.payload
    item, args = order[0], order[1:]

    prices = {'coffee': 2.10,
              'chocolate': 0.30}

    out_envelope = protocol.Envelope(
        author=in_envelope.author,
        payload=None,
        recipients=[in_envelope.author],
        type='error')

    if item == 'status':
        orders = args or service.orders.keys()
        statuses = {}

        for order in orders:
            try:
                order_ = service.orders[int(order)]
                statuses[order] = order_.status
            except KeyError:
                statuses[order] = 'no order found'

        out_envelope.payload = statuses
        out_envelope.type = 'orderStatus'

    elif item == 'coffee':
        parser = lib.ArgumentParser(prog='order coffee')
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

            item = protocol.Coffee(**parsed)
            order = protocol.Order(item,
                                   location='takeaway',
                                   cost=prices['coffee'])

            # Execute order

            try:
                order = service.order_coffee(order)
                result = order.to_dict()

            except Exception as e:
                sys.stderr.write(traceback.format_exc())
                out_envelope.payload = "Error: %s" % e

            else:
                out_envelope.payload = result
                out_envelope.type = 'orderReceipt'

    elif item == 'chocolate':
        parser = lib.ArgumentParser(prog='order chocolate')
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

            item = protocol.Chocolate(**parsed)
            order = protocol.Order(item,
                                   location=location,
                                   cost=price)

            # Execute order

            try:
                order = service.order_chocolate(order)
                result = order.to_dict()

            except Exception as e:
                sys.stderr.write(traceback.format_exc())
                out_envelope.payload = "Error: %s" % e

            else:
                out_envelope.payload = result
                out_envelope.type = 'receipt'

    else:
        out_envelope.payload = 'Could not order "%s"' % item

    return out_envelope


def stats_query(self, in_envelope):
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

    stats_query = in_envelope.payload
    peers = stats_query['peers']  # list
    out_envelope = protocol.Envelope(author=in_envelope.author,
                                     payload=stats_query,
                                     recipients=peers,
                                     type='__swarmQuery__')
    return out_envelope


def peer_query(self, in_envelope):
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

    in_envelope.trace += ['process.peer_query']

    peers, query = in_envelope.payload
    out_envelope = protocol.Envelope(author=in_envelope.author,
                                     payload=query,
                                     recipients=peers,
                                     type='__swarmQuery__',
                                     trace=in_envelope.trace)

    # log = protocol.Log(
    #     name='process.peer_query',
    #     author=in_envelope.author,
    #     level='info',
    #     string='{} queried {} from {}'.format(in_envelope.author,
    #                                           query, peers),
    #     trace=in_envelope.trace,
    #     envelope=in_envelope)

    # self.log(log)

    return out_envelope


def peer_results(self, in_envelope):
    """Results have been returned from peer, process it

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

    in_envelope.trace += ['process.peer_results']

    print "peer_results: %s" % in_envelope.to_dict()
    results = protocol.QueryResults.from_dict(in_envelope.payload)
    out_envelope = protocol.Envelope(author=results.peer,
                                     payload=results,
                                     recipients=[results.questioner],
                                     type='__queryResults__',
                                     trace=in_envelope.trace)
    return out_envelope


def heartbeat(self, in_envelope):
    """Update peer status"""
    self.heartbeats[in_envelope.author] = time.time()
