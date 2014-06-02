from __future__ import absolute_import

# standard library
import time

# local library
import lib
import json
import process
import protocol

# vendor dependency
import zmq

context = zmq.Context()


class Swarm(object):
    letters = dict()  # Keep track of all letters sent, per peer
    peers = set()  # Keep track of all peers
    orders = dict()  # Keep track of all orders
    heartbeats = dict()  # Keep your ear close to the peer's chests

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
            self.router(envelope)

    def publish(self, envelope):
        """Physically publish `envelope`"""
        dic = envelope.to_dict()
        marshal = json.dumps(dic)
        self.pub.send_multipart(['default', marshal])

    def log(self, log):
        dic = log.to_dict()
        marshal = json.dumps(dic)
        self.pub.send_multipart(['log', marshal])

    def router(self, in_envelope):
        """Take incoming envelope, process it, and send one back out"""

        in_envelope.trace += ['Swarm.router']

        log = protocol.Log(
            name='Swarm.router',
            author=in_envelope.author,
            level='info',
            string='{} was received'.format(in_envelope.type),
            trace=in_envelope.trace,
            envelope=in_envelope)

        self.log(log)

        type = in_envelope.type

        processors = {
            'letter': process.letter,
            'invitation': process.invitation,
            'orderPlacement': process.order_placement,
            'stateQuery': process.state_query,
            'peersQuery': process.peers_query,
            'statsQuery': process.stats_query,
            'peerQuery': process.peer_query,
            'heartbeat': process.heartbeat,
            '__peerResults__': process.peer_results,
        }

        processor = processors.get(type)
        if processor:
            out_envelope = processor(self, in_envelope)
            out_envelope.trace += ['Swarm.router']

            if out_envelope:
                self.publish(out_envelope)

                log = protocol.Log(
                    name='Swarm.router',
                    author=out_envelope.author,
                    level='info',
                    string='{} was sent'.format(out_envelope.type),
                    trace=out_envelope.trace)

                self.log(log)
        else:
            print "Envelope not recognised: {}".format(type)


if __name__ == '__main__':
    swarm = Swarm()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "\nGood bye"
            break
