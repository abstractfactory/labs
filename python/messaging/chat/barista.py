"""Baristas (a worker) serve coffee"""

from __future__ import absolute_import

# standard library
import time

# local library
import lib
import peer
# import service


def is_service(func):
    func.service = True
    return func


class Barista(peer.Peer):
    """A Barista orchestrates multiple services"""

    # Baristas handle orders between each other
    orders = dict()

    def __init__(self, *args, **kwargs):
        super(Barista, self).__init__(*args, **kwargs)
        self.name = 'barista'
        self.services = [self.take_order]

    @is_service
    def take_order(self, order):
        print "Taking order"
        # order = service.order_coffee(order)

        # # Store order
        # order.id = 0
        # while order.id in self.orders:
        #     order.id += 1

        # self.orders[order.id] = order

        # lib.spawn(service.make_coffee,
        #           args=[order],
        #           name='order: %s' % order.id)

        # return order

    def serve_coffee(self, order):
        pass


if __name__ == '__main__':
    lib.clear_console()
    barista = Barista()

    print "Barista online.."

    while True:
        try:
            barista.init_shell()
            command = raw_input()

            if not command:
                continue

            barista.route_command(command)

        except KeyboardInterrupt:
            print "\nGood bye"
            break

        except Exception as e:
            print e
            break
