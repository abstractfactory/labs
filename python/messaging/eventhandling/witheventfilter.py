"""
By Justin Israel: http://pastebin.com/Rn739jdA
- Converted to PyQt5

Note from Marcus:
    Here, events are posted onto a global Handler. The difference between
    this and withcustomcascading.py is that parent widgets cannot intercept
    events emitted by children, as they are directly posted onto the global
    QApplication instance. Similar to withpypubsub.py.

"""

import os

from PyQt5 import QtWidgets
from PyQt5 import QtCore


class Handler(QtCore.QObject):
    """
    An event filter class for handling all logic
    related to actions in a part of our system
    """

    def eventFilter(self, obj, event):
        if event.type() == SelectedEventType:
            print "%s was selected" % event.path

        elif event.type() == RunEventType:
            print "%s was run" % event.path

        elif event.type() == DeleteEventType:
            print "%s was deleted" % event.path

        return super(Handler, self).eventFilter(obj, event)


class Window(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        view = List()
        view.setObjectName('List')

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(view)

        # Example of installing event filter on a composed
        # child widget
        self._handler = Handler()
        view.installEventFilter(self._handler)

    def setup(self, paths):
        view = self.findChild(QtWidgets.QWidget, 'List')
        view.setup(paths)


class List(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)

        body = QtWidgets.QWidget()
        body.setObjectName('Body')

        layout = QtWidgets.QVBoxLayout(body)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(body)

    def setup(self, paths):
        """Insert `paths` into list

        Assign `Item` based on path suffix.

        """

        body = self.findChild(QtWidgets.QWidget, 'Body')
        layout = body.layout()

        for path in paths:
            basename = os.path.basename(path)
            _, suffix = os.path.splitext(basename)

            if suffix == '.special':
                item = SpecialItem(path)

            elif suffix == '.secure':
                item = SecureItem(path)

            else:
                item = Item(path)

            layout.addWidget(item)


class Item(QtWidgets.QWidget):
    def __init__(self, path):
        super(Item, self).__init__(None)
        self.path = path
        self.setAttribute(QtCore.Qt.WA_StyledBackground)

        basename = os.path.basename(path)
        name, suffix = os.path.splitext(basename)
        label = QtWidgets.QLabel(name)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(label)

        # Example of installing an event filter
        # on the actual widget instead of composed children
        self._handler = Handler()
        self.installEventFilter(self._handler)

    def mousePressEvent(self, event):
        self.selected_event()
        super(Item, self).mousePressEvent(event)

    def selected_event(self):
        custom_event = SelectedEvent(self.path)
        QtWidgets.qApp.postEvent(self, custom_event)


class SpecialItem(Item):
    def __init__(self, *args, **kwargs):
        super(SpecialItem, self).__init__(*args, **kwargs)

        button1 = QtWidgets.QPushButton('run')
        button2 = QtWidgets.QPushButton('delete')

        layout = self.layout()
        layout.addWidget(button1)
        layout.addWidget(button2)

        button1.released.connect(self.run_event)
        button2.released.connect(self.delete_event)

    def selected_event(self):
        custom_event = SelectedEvent(self.path + "|Special")
        QtWidgets.qApp.postEvent(self, custom_event)

    def run_event(self):
        custom_event = RunEvent(self.path + "|Special")
        QtWidgets.qApp.postEvent(self, custom_event)

    def delete_event(self):
        custom_event = DeleteEvent(self.path + "|Special")
        QtWidgets.qApp.postEvent(self, custom_event)


class SecureItem(Item):
    def selected_event(self):
        custom_event = SelectedEvent(self.path + "|Secure")
        QtWidgets.qApp.postEvent(self, custom_event)


class BaseEvent(QtCore.QEvent):
    def __init__(self, path):
        super(BaseEvent, self).__init__(Types[type(self)])
        self.path = path


class SelectedEvent(BaseEvent):
    pass


class RunEvent(BaseEvent):
    pass


class DeleteEvent(BaseEvent):
    pass


SelectedEventType = QtCore.QEvent.Type(1001)
RunEventType = QtCore.QEvent.Type(1002)
DeleteEventType = QtCore.QEvent.Type(1003)

Types = {
    SelectedEvent: SelectedEventType,
    RunEvent: RunEventType,
    DeleteEvent: DeleteEventType,
}

css = """

Item {background-color: yellow;}
SpecialItem {background-color: orange;}
SecureItem {background-color: lightgreen;}

"""

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)

    paths = ['/home/marcus/A.special', '/home/marcus/B.normal',
             '/home/marcus/C.secure', '/home/marcus/D.normal']

    window = Window()
    window.setup(paths)
    window.setStyleSheet(css)
    window.show()

    app.exec_()