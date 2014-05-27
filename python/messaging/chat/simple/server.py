"""
Server receives:


"""

import zmq
import time
import threading

context = zmq.Context()


def spawn(func):
    thread = threading.Thread(target=func)
    thread.daemon = True
    thread.start()


class Letter(object):
    """Letter

    Responsibilities:
        - Carry message
        - Carry author
        - Carry recipient(s)
        - Carry time

    """

    def __init__(self, body, author, recipients, timestamp):
        self.body = body
        self.author = author
        self.recipients = recipients
        self.timestamp = timestamp

    @classmethod
    def from_message(cls, message):
        letter = cls(body=message['body'],
                     author=message['author'],
                     recipients=message['recipients'],
                     timestamp=message['time'])
        return letter

    def dump(self):
        return {
            'from': self.author,
            'to': self.recipients,
            'message': self.body
        }


# Keep track of messages sent
letters = {}


if __name__ == '__main__':
    pull = context.socket(zmq.PULL)  # Incoming messages
    pull.bind("tcp://*:5555")

    pub = context.socket(zmq.PUB)  # Distributing messages
    pub.bind("tcp://*:5556")

    rep = context.socket(zmq.REP)  # Responding to queries
    rep.bind("tcp://*:5557")

    def commando():
        while True:
            request = rep.recv_json()
            action = request['action']
            author = request['author']

            if action == 'state':
                print "Getting state for %s" % author
                state = letters.get(author, {})
                rep.send_json(state)

    def publisher():
        while True:
            message = pull.recv_json()
            letter = Letter.from_message(message)

            action = message['action']
            author = letter.author
            time = letter.timestamp

            if action == 'says':
                if not author in letters:
                    letters[author] = {}
                print "Storing %s @ %s" % (letter.body, time)
                letters[author][time] = letter.dump()

                pub.send_json(letter.dump())

    spawn(commando)
    spawn(publisher)

    print "Listening for requests on @ %s" % "tcp://*:5557"
    print "Listning for messages @ %s" % "tcp://*:5555"

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "\nGood bye"
            break
