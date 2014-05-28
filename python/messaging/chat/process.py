"""Process incoming envelope and output a response envelope"""

from __future__ import absolute_import

# standard library
import time

# local library
import protocol
import service


def letter(self, envelope):
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
    dic = envelope.to_dict()
    self.letters[envelope.author][envelope.timestamp] = dic

    return envelope


def query_state(self, envelope):
    query = envelope.payload

    threads = {}
    for author in query:
        state = self.letters.get(author, {})
        threads.update(state)

    envelope = protocol.Envelope(author=envelope.author,
                                 payload=threads,
                                 recipients=[envelope.author],
                                 type='state')
    return envelope


def query_peers(self, envelope):
    peers = list(self.peers)
    envelope = protocol.Envelope(author=envelope.author,
                                 payload=peers,
                                 recipients=[envelope.author],
                                 type='peers')
    return envelope


def invitation(self, envelope):
    invitation = envelope.payload
    envelope = protocol.Envelope(author=envelope.author,
                                 payload=invitation,
                                 recipients=invitation)
    print "%s inviting %s" % (envelope.author, invitation)

    self.peers.update(invitation)
    self.peers.add(envelope.author)
    return envelope


def query_services(self, envelope):
    query = envelope.payload

    if not query:
        services = service.services.keys()
        message = 'Available swarm services:\n'
        message += ' '.join(["  %s\n" % serv for serv in services])
    else:
        try:
            message = getattr(service, query).__doc__
        except AttributeError:
            message = 'Sorry, service "%s" was not available' % query

    envelope = protocol.Envelope(author=envelope.author,
                                 payload=message,
                                 recipients=[envelope.author],
                                 type='services')
    return envelope
