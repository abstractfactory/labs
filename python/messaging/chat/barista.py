"""Baristas serve coffee"""

from __future__ import absolute_import

# standard library
import time

# local library
import lib
import peer


def take_order(order):
    pass


def serve_coffee(order):
    pass


if __name__ == '__main__':
    lib.clear_console()
    barista = peer.Peer('barista')

    barista.services = [take_order, serve_coffee]

    print "Barista online.."

    while True:
        try:
            time.sleep(1)

        except KeyboardInterrupt:
            print "\nGood bye"
            break

        except Exception as e:
            print e
            break
