from __future__ import absolute_import

# standard library
import os
import sys
import time
import threading

path = __file__
for i in range(3):
    path = os.path.dirname(path)

sys.path.insert(0, path)

# local library
import peer


def chatter(name):
    peer.main([name, '--chatter'])


if __name__ == '__main__':
    for name in ('markus', 'nikki', 'lukas', 'rocky', 'frank'):
        print "Running chatter %r" % name
        thread = threading.Thread(target=chatter, args=[name])
        thread.deamon = True
        thread.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "\nGood bye"
            break
