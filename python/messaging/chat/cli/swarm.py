
import os
import sys
import time

path = __file__
for i in range(3):
    path = os.path.dirname(path)

sys.path.insert(0, path)

import chat.lib
import chat.swarm


def main():
    chat.swarm.Swarm()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "\nGood bye"
            break


if __name__ == '__main__':
    main()
