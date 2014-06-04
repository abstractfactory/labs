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


class Item(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        self.pressed.connect(self.locations_event)

    def locations_event(self):
        # This works, as it's posted in direct reference to
        # the receiver.
        QtWidgets.QApplication.postEvent(self.window(), QtCore.QEvent(12345))

        # This uses our QApplication subclass, and doesn't work
        # for some reason.
        QApplication.postEvent(self, QtCore.QEvent(12345))

        # This uses another method, also doesn't work, but here we
        # can see that all events are being accepted by their immediate
        # parent (for some reason), and thus not propagated further.
        manual_propagate(self, QtCore.QEvent(12345))


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

    def event(self, event):
        if event.type() == 12345:
            self.locations_event('Success')
        return True

    def locations_event(self, path):
        print "%s was received from Top" % path


def manual_propagate(target, event):
    app = QtWidgets.QApplication.instance()
    while target:
        app.sendEvent(target, event)
        if not event.isAccepted():
            if hasattr(target, 'parent'):
                target = target.parent()
        else:
            # All events land here; they're accepted
            # no matter what.
            target = None
    return event.isAccepted()


class QApplication(QtWidgets.QApplication):
    def notify(self, receiver, event):
        if event.type() > QtCore.QEvent.User:
            w = receiver
            while(w):
                # Note that this calls `event` method directly thus bypassing
                # calling qApplications and receivers event filters
                res = w.event(event)
                if res and event.isAccepted():
                    return res
                w = w.parent()

        return super(QApplication, self).notify(receiver, event)


if __name__ == '__main__':
    import sys

    # Custom QApplication
    app = QApplication(sys.argv)
    # app = QtWidgets.QApplication(sys.argv)
    win = Top()
    win.show()
    app.exec_()
