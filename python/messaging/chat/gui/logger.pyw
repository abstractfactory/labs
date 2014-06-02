import os
import sys

path = __file__
for i in range(3):
    path = os.path.dirname(path)

sys.path.insert(0, path)


if __name__ == '__main__':
    import chat.logger.gui
    chat.logger.gui.main()
