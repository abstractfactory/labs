from __future__ import absolute_import

import zmq
import time

# local library
import lib
import protocol

context = zmq.Context()


class Swarm(object):
    letters = dict()  # Keep track of all letters sent, per peer
    peers = set()  # Keep track of all peers

    def __init__(self):
        pull = context.socket(zmq.PULL)  # Incoming messages
        pull.bind("tcp://*:5555")

        pub = context.socket(zmq.PUB)  # Distributing messages
        pub.bind("tcp://*:5556")

        self.pull = pull
        self.pub = pub

        lib.spawn(self.listen, name='listen')

    def listen(self):
        print "Listening for messages @ %s" % "tcp://*:5555"
        print "Broadcasting messages @ %s" % "tcp://*:5556"

        while True:
            message = self.pull.recv_json()
            envelope = protocol.Envelope.from_message(message)
            self.publisher(envelope)

    def publish(self, envelope):
        self.pub.send_json(envelope.dump())

    def publisher(self, envelope):
        """
             ________    ___________
            |        |  |           |   /
        --->|  Pull  |--|  Publish  |---|-o
            |________|  |___________|   \

        """

        if envelope.type == 'letter':
            letter = envelope.payload

            if not envelope.author in self.letters:
                self.letters[envelope.author] = {}

            # Maintain all original authors
            self.peers.add(envelope.author)

            gmtime = time.gmtime(envelope.timestamp)
            asctime = time.asctime(gmtime)
            print "On %s, %s said: %s" % (asctime,
                                          envelope.author,
                                          letter)
            self.letters[envelope.author][envelope.timestamp] = envelope.dump()
            self.publish(envelope)

        elif envelope.type == 'queryState':
            request = envelope.payload

            threads = {}
            for author in request:
                state = self.letters.get(author, {})
                threads.update(state)

            if threads:
                envelope = protocol.Envelope(author=envelope.author,
                                             payload=threads,
                                             recipients=[envelope.author],
                                             type='state')
                self.publish(envelope)

        elif envelope.type == 'queryPeers':
            peers = list(self.peers)
            envelope = protocol.Envelope(author=envelope.author,
                                         payload=peers,
                                         recipients=[envelope.author],
                                         type='peers')
            self.publish(envelope)

        elif envelope.type == 'invitation':
            invitation = envelope.payload
            envelope = protocol.Envelope(author=envelope.author,
                                         payload=invitation,
                                         recipients=invitation)
            print "%s inviting %s" % (envelope.author, invitation)

            self.peers.update(invitation)
            self.peers.add(envelope.author)

            self.publish(envelope)

if __name__ == '__main__':
    swarm = Swarm()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "\nGood bye"
            break
