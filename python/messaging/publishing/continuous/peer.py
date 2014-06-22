import zmq
import time
import uuid

unique_id = uuid.uuid4().get_urn()


if __name__ == '__main__':

    while True:
        print "I: Publishing {}".format(unique_id)

        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        socket.connect("tcp://127.0.0.1:5555")
        socket.send_multipart(['general', unique_id])
        socket.close()
        context.destroy()

        # Wait for a random amount of time
        time.sleep(1)
