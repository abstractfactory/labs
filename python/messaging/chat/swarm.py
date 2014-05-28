from __future__ import absolute_import

# standard library
import sys
import time

# local library
import lib
import service
import protocol
import process
import traceback

# vendor dependency
import zmq

context = zmq.Context()


class Swarm(object):
    letters = dict()  # Keep track of all letters sent, per peer
    peers = set()  # Keep track of all peers
    orders = dict()  # Keep track of all orders

    def __init__(self):
        pull = context.socket(zmq.PULL)  # Incoming messages
        pull.bind("tcp://*:5555")

        pub = context.socket(zmq.PUB)  # Distributing messages
        pub.bind("tcp://*:5556")

        self.pull = pull
        self.pub = pub

        lib.spawn(self.listen, name='listen')

    def listen(self):
        """
             ________    ___________
            |        |  |           |   /
        --->|  Pull  |--|  Publish  |---|-o
            |________|  |___________|   \

        """

        print "Listening for messages @ %s" % "tcp://*:5555"
        print "Broadcasting messages @ %s" % "tcp://*:5556"

        while True:
            message = self.pull.recv_json()
            envelope = protocol.Envelope.from_dict(message)
            self.publisher(envelope)

    def publish(self, envelope):
        """Physically publish `envelope`"""
        self.pub.send_json(envelope.to_dict())

    def publisher(self, in_envelope):
        """Take incoming envelope, process it, and send one back out"""

        type = in_envelope.type

        if type == 'letter':
            out_envelope = process.letter(self, in_envelope)
            self.publish(out_envelope)

        elif type == 'queryState':
            out_envelope = process.query_state(self, in_envelope)
            self.publish(out_envelope)

        elif type == 'queryPeers':
            out_envelope = process.query_peers(self, in_envelope)
            self.publish(out_envelope)

        elif type == 'invitation':
            out_envelope = process.invitation(self, in_envelope)
            self.publish(out_envelope)

        elif type == 'queryServices':
            out_envelope = process.query_services(self, in_envelope)
            self.publish(out_envelope)

        elif type == 'order':
            order = in_envelope.payload
            item, args = order[0], order[1:]

            out_envelope = protocol.Envelope(
                author=in_envelope.author,
                payload=None,
                recipients=[in_envelope.author],
                type='error')

            if item == 'status':
                orders = args or service.orders.keys()
                statuses = {}

                for order in orders:
                    order_ = service.orders[int(order)]
                    statuses[order] = order_.status

                out_envelope.payload = statuses
                out_envelope.type = 'status'

            elif item == 'coffee':
                parser = lib.ArgumentParser(prog='order coffee')
                parser.add_argument("name")
                parser.add_argument("--quantity", default=1)
                parser.add_argument("--milk", dest="milk", action="store_true")
                parser.add_argument("--size", default='regular')
                parser.add_argument("--no-milk",
                                    dest="milk",
                                    action="store_false")

                parsed = None

                try:
                    parsed = parser.parse_args(args)

                except ValueError:
                    out_envelope.payload = parser.format_help()

                except SystemExit:
                    # Parser exited without error (e.g. to return help)
                    pass

                if parsed:
                    item = protocol.Coffee(**parsed.__dict__)
                    order = protocol.Order(item,
                                           location='takeaway',
                                           cost=2.10)

                    # Execute order

                    try:
                        order = service.order_coffee(order)
                        result = order.to_dict()

                    except Exception as e:
                        sys.stderr.write(traceback.format_exc())
                        out_envelope.payload = "Error: %s" % e

                    else:
                        out_envelope.payload = result
                        out_envelope.type = 'receipt'

            else:
                out_envelope.payload = 'Could not order "%s"' % item

            self.publish(out_envelope)

        else:
            print "Unrecognised envelope acquired: %s" % in_envelope.type


if __name__ == '__main__':
    swarm = Swarm()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "\nGood bye"
            break
