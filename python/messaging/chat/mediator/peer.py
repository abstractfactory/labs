from __future__ import absolute_import

import chat.lib
import chat.protocol


class Factory(object):
    __metaclass__ = chat.lib.DynamicRegistry

    def process(self, typ, receiver, envelope):
        try:
            processor = self.registry[typ]()
            processor.process(receiver, envelope)
        except KeyError:
            raise ValueError("Unhandled mediator: %s" % typ)


class Letter(Factory):
    def process(self, receiver, envelope):
        """Letter was sent from another PEER

        PEER A
         _             SWARM
        | |             _             PEER B
        | |            |/|             _
        | |            |/|            | |
        | |            |/|   letter   | |
        | |   letter   |/|<-----------|_|
        | |<===========|_|
        |_|

        Arguments:
            receiver (object) - object to operate upon
            envelope (chat.protocol.Envelope) - message to process

        """

        # Include this (potentially new) peer in list
        # of recipients for future letters send by `self`.
        receiver.peers.add(envelope.author)

        if envelope.author != receiver.name:
            message = receiver.formatter(envelope)
            receiver.display_remote_message(message)


class Receipt(Factory):
    def process(self, receiver, envelope):
        """A receipt was returned from SWARM order. (event)

        PEER A
         _             SWARM
        | |             _
        | |            |/|
        | |            |/|
        | |            |/|
        | |  receipt   |/|
        | |<===========|_|
        |_|

        Note: messages are received indirectly, as a result
              of an earlier/remote request.

        """

        order = chat.protocol.Order.from_dict(envelope.payload)
        dic = order.to_dict()

        message = "Your receipt:\n"
        message += chat.lib.pformat(dic, level=1)

        receiver.display_remote_message(message)
