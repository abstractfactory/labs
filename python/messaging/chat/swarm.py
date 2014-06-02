from __future__ import absolute_import

# standard library
import time
import json

# local library
import chat.lib
import chat.protocol
import chat.mediator.swarm

# vendor dependency
import zmq

context = zmq.Context()


class Swarm(object):
    letters = dict()  # Keep track of all letters sent, per peer
    peers = set()  # Keep track of all peers
    orders = dict()  # Keep track of all orders
    heartbeats = dict()  # Keep your ear close to the peer's chests

    KEEP_ALIVE = 4  # seconds before peers are considered dead

    def __init__(self):
        pull = context.socket(zmq.PULL)  # Incoming messages
        pull.bind("tcp://*:5555")

        pub = context.socket(zmq.PUB)  # Distributing messages
        pub.bind("tcp://*:5556")

        self.pull = pull
        self.pub = pub

        chat.lib.spawn(self.listen, name='listen')
        chat.lib.spawn(self.keepalive, name='keepalive')

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
            envelope = chat.protocol.Envelope.from_dict(message)
            self.router(envelope)

    def keepalive(self):
        """Scan `self.heartbeats` for dead connections"""
        while True:
            time.sleep(self.KEEP_ALIVE)

            dead = []
            for client, last_seen in self.heartbeats.iteritems():

                # If peer is unresponsive for over self.KEEP_ALIVE
                # seconds, consider him disconnected and clear
                # out his locker.
                if last_seen < (time.time() - self.KEEP_ALIVE):
                    dead.append(client)

            for d in dead:
                print "%s was disconnected" % d
                self.heartbeats.pop(d, None)
                self.letters.pop(d, None)

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
        """Take incoming envelope, chat.process it, and send one back out"""

        in_envelope.trace += ['Swarm.router']

        log = chat.protocol.Log(
            name='Swarm.router',
            author=in_envelope.author,
            level='info',
            string='{} was received'.format(in_envelope.type),
            trace=in_envelope.trace,
            envelope=in_envelope)

        self.log(log)

        type = in_envelope.type

        factory = chat.mediator.swarm.Factory()

        try:
            factory.mediate(type, self, in_envelope)
        except ValueError as e:
            print e
