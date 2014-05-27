import time


class Envelope(object):
    """On-the-wire protocol"""
    def __str__(self):
        return "(%s: %s)" % (self.author, self.payload)

    def __init__(self, payload=None, author=None, recipients=None, type=None):
        self.payload = payload
        self.author = author
        self.recipients = recipients
        self.timestamp = time.time()
        self.type = type

    @classmethod
    def from_message(cls, message):
        envelope = cls(author=message['author'],
                       payload=message['payload'],
                       recipients=message['recipients'],
                       type=message['type'])
        return envelope

    def dump(self):
        return {
            'type': self.type,
            'author': self.author,
            'recipients': self.recipients,
            'payload': self.payload,
            'timestamp': self.timestamp,
            'type': self.type
        }
