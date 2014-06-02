import os
import sys

path = __file__
for i in range(2):
    path = os.path.dirname(path)

sys.path.insert(0, path)