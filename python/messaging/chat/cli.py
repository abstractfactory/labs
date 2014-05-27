
from __future__ import absolute_import

import sys
import argparse

import lib
import peer

if len(sys.argv) >= 2:
    author, peers = sys.argv[1], sys.argv[2:]

    lib.clear_console()
    peer = peer.Peer(author, peers)

    while True:
        try:
            sys.stdout.write("%s> " % peer.author)
            command = raw_input()

            if not command:
                continue

            peer.mediate(command)

        except KeyboardInterrupt:
            print "\nGood bye"
            break

        except Exception as e:
            print e
            break

else:
    print "Usage: client.py my_name peer1_name peer2_name ..."
