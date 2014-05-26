import zmq

context = zmq.Context()


class Letter(object):
    def __init__(self, data, author, timestamp):
        self.data = data
        self.author = author
        self.timestamp = timestamp
        self.delivered = False

    @classmethod
    def from_message(cls, message):
        letter = cls(data=message['data'],
                     author=message['author'],
                     timestamp=message['time'])
        return letter

# Keep track of messages sent
letters = {}


if __name__ == '__main__':
    consumer = context.socket(zmq.PULL)
    consumer.bind("tcp://*:5555")

    producer = context.socket(zmq.PUB)
    producer.bind("tcp://*:5556")

    try:
        while True:
            message = consumer.recv_json()
            letter = Letter.from_message(message)

            action = message['action']
            author = message['author']
            time = message['time']
            data = message['data']

            if action == 'says':
                producer.send_multipart([str(author), str(data)])

            if action == 'listen':
                print "%s is also listening on %s" % (author, data)

    except KeyboardInterrupt:
        print "\nGood bye"
