import time


# def from_message(message):
#     """Deserialise message into object"""
#     return protocols[message['type']].from_message(message)


class Envelope(object):
    """On-the-wire protocol, encapsulating message-protocols below"""
    def __str__(self):
        return "(%s: %s)" % (self.author, self.body)

    def __init__(self, author=None, recipients=None, body=None):
        assert isinstance(body, AbstractMessage) if body else True
        self.author = author
        self.recipients = recipients
        self.timestamp = time.time()
        self.type = None

        self.body = body

    @classmethod
    def from_message(cls, message):
        assert message.get('type') == 'envelope'
        body = message['body']
        body = protocols[body['type']](data=body['data'])

        envelope = cls(author=message['author'],
                       body=body,
                       recipients=message['recipients'])
        return envelope

    def dump(self):
        assert isinstance(self.body, AbstractMessage)
        return {
            'type': self.type,
            'author': self.author,
            'recipients': self.recipients,
            'body': self.body.dump() if self.body else None,
            'timestamp': self.timestamp,
            'type': 'envelope'
        }


class AbstractMessage(object):
    """Abstract message-protocol"""
    @property
    def type(self):
        return type(self).__name__.lower()

    def __init__(self, data):
        self.data = data

    def dump(self):
        return {'data': self.data,
                'type': self.type}


class Letter(AbstractMessage):
    pass


class AllServices(AbstractMessage):
    pass


class Invitation(AbstractMessage):
    pass


class StateRequest(AbstractMessage):
    pass


class StateReply(AbstractMessage):
    pass


protocols = {}
for protocol in (Letter,
                 AllServices,
                 Invitation,
                 StateRequest,
                 StateReply):
    protocols[protocol.__name__.lower()] = protocol


if __name__ == '__main__':
    letter = Letter(body="Hello World!")
    envelope = Envelope('marcus', ['nikki'], letter)
