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

"""

from __future__ import absolute_import

from PyQt5 import QtWidgets
from PyQt5 import QtCore

import qtpath


class Item(QtWidgets.QPushButton):
    locations_signal = QtCore.pyqtSignal(str)
    messages_signal = QtCore.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        self.pressed.connect(self.locations_event)

    def mouseDoubleClickEvent(self, event):
        message = "Hello from %s" % self.objectName()
        self.messages_signal.emit(message)

    def locations_event(self):
        root = self.window()
        path = qtpath.abspath(root, self)

        self.locations_signal.emit(path)


class List(QtWidgets.QWidget):
    locations_signal = QtCore.pyqtSignal(object)
    messages_signal = QtCore.pyqtSignal(object)

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

            # Forward events, not the knowledge of
            # implementation detail 'locations_signal', along
            # with the additional signal 'forward_signal' and
            # modification of List for signals from Item to
            # reach Top.
            item.locations_signal.connect(self.forward_locations)
            item.messages_signal.connect(self.forward_messages)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(header)
        layout.addWidget(body)

    def forward_locations(self, *args, **kwargs):
        self.locations_signal.emit(*args, **kwargs)

    def forward_messages(self, *args, **kwargs):
        self.messages_signal.emit(*args, **kwargs)


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

            lis.locations_signal.connect(self.locations_event)
            lis.messages_signal.connect(self.messages_event)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)

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
