"""Distributed logging

This WORKER listens for logging messages and
displays them in the termial.

"""

from __future__ import absolute_import

# standard library
import time
import json
import logging

# dependencies
import zmq

# local library
import lib
import protocol


def get_formatter():
    formatter = logging.Formatter(
        '%(asctime)s - '
        '%(levelname)s - '
        '%(name)s - '
        '%(message)s',
        '%H:%M:%S')
    return formatter


def setup_log(root='chat'):
    log = logging.getLogger(root)

    if log.handlers:
        return log.handlers[0]

    formatter = get_formatter()
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)

    return log


logger = setup_log()
logger.setLevel(logging.DEBUG)


def main():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://localhost:5556')
    socket.setsockopt(zmq.SUBSCRIBE, 'log')

    print "Running logger.."

    while True:
        header, body = socket.recv_multipart()
        message = json.loads(body)
        log = protocol.Log.from_dict(message)

        write = getattr(logger, log.level)
        write("{}: {}".format(log.trace, log.string))


if __name__ == '__main__':
    lib.spawn(main)

    while True:
        try:
            time.sleep(1)

        except KeyboardInterrupt:
            print "\nGood bye"
            break
