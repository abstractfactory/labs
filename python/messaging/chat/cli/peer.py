
from __future__ import absolute_import

import os
import sys
import time
import random
import argparse

path = __file__
for i in range(3):
    path = os.path.dirname(path)

sys.path.insert(0, path)

import chat.lib
import chat.peer

vocabulary = ['Hi there', 'hello', 'how are you?', "I'm fine thanks",
              'and you?']


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument('-p', "--peer", action='append', dest='peers',
                        default=[], help='Add peer to talk to')
    parser.add_argument('-c', "--chatter", action='store_true', default=False)
    args = parser.parse_args(args)

    peer = chat.peer.Peer(name=args.name,
                          peers=args.peers)

    while True:
        try:
            if not args.chatter:
                peer.init_shell()
                command = raw_input()

                if not command:
                    continue

                peer.route_command(command)
            else:
                index = random.randrange(0, len(vocabulary) - 1)
                peer.route_command("say %s" % vocabulary[index])
                time.sleep(random.random() * 2)

        except KeyboardInterrupt:
            print "\nGood bye"
            break

        except Exception as e:
            print e
            break


if __name__ == '__main__':
    chat.lib.clear_console()
    main(sys.argv[1:])
