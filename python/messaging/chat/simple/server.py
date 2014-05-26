import zmq

context = zmq.Context()


if __name__ == '__main__':
    pull = context.socket(zmq.PULL)
    pull.bind("tcp://*:5555")

    pub = context.socket(zmq.PUB)
    pub.bind("tcp://*:5556")

    try:
        while True:
            message = pull.recv_json()
            if message['action'] == 'says':

                says = "{data}".format(data=message['data'])

                print "Sending %s" % says
                pub.send_string("%s: %s" % (message['who'], says))

    except KeyboardInterrupt:
        print "\nGood bye"
