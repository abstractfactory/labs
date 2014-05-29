
from __future__ import absolute_import

import argparse

import lib
import peer


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("author")
    parser.add_argument('-p', "--peer", action='append', dest='peers',
                        default=[], help='Add peer to talk to')
    args = parser.parse_args()

    lib.clear_console()
    peer = peer.Peer(args.author, args.peers)

    while True:
        try:
            peer.init_shell()
            command = raw_input()

            if not command:
                continue

            peer.route_command(command)

        except KeyboardInterrupt:
            print "\nGood bye"
            break

        except Exception as e:
            print e
            break
