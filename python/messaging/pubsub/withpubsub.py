"""

Three layers of widgets, inner widget communicating with
outer widget.

 _______________________
|         Top           |
|   _________________   |
|  |      List       |  |
|  |   ___________   |  |
|  |  |   Item    |  |  |
|  |  |           |  |  |
|  |  |___________|  |  |
|  |_________________|  |
|_______________________|

qtpath://Top.QWidget/List1.QWidget/Item1.QWidget


Description:
    In this example, `pubsub` acts as a broker; forwarding events
    based on their target address/topic/frequency.

    Note that List is de-coupled from any communication
    between `Item` and `Top`.

"""

from __future__ import absolute_import

from PyQt5 import QtWidgets

import qtpath
import pubsub.pub


class Item(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        self.pressed.connect(self.locations_event)

    def locations_event(self):
        root = self.window()
        path = qtpath.abspath(root, self)

        pubsub.pub.sendMessage('locations', path=path)

    def mouseDoubleClickEvent(self, event):
        message = "Hello from %s" % self.objectName()
        pubsub.pub.sendMessage('messages', message=message)


class List(QtWidgets.QWidget):
    def __init__(self, name, parent=None):
        super(List, self).__init__(parent)

        header = QtWidgets.QWidget()
        label = QtWidgets.QLabel(name)
        layout = QtWidgets.QHBoxLayout(header)
        layout.addWidget(label)

        body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(body)

        for x in range(10):
            name = 'Item%i' % x
            item = Item(name)
            item.setObjectName(name)
            layout.addWidget(item)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(header)
        layout.addWidget(body)


class Top(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(Top, self).__init__(*args, **kwargs)
        self.setObjectName('Main')

        body = QtWidgets.QWidget()

        layout = QtWidgets.QHBoxLayout(body)

        for x in range(3):
            name = 'List%i' % x
            lis = List(name)
            lis.setObjectName(name)
            layout.addWidget(lis)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)

        pubsub.pub.subscribe(self.locations_event, 'locations')
        pubsub.pub.subscribe(self.messages_event, 'messages')

    def locations_event(self, path):
        print "%s was received from Top" % path

    def messages_event(self, message):
        print message


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = Top()
    win.show()
    app.exec_()
