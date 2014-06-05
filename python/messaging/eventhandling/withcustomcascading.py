"""Event-handling with Custom Cascading

QWidget is overriden to (re)implement `post_event` and `event_handler`.

The native `postEvent` and `event` respectively works in a similar fashion
but doesn't allow for user-defined QEvents to be propagated past its
initial widget; unless you subclass QApplication.

Reference: http://stackoverflow.com/questions/3180506/propagate-custom-qevent-to-parent-widget-in-qt-pyqt

Notice how List is instancing Items based on input, and that it doesn't
have to manually propagate events to Window. That's because all widgets
in the path leading up to Window are our overridden PWidget which
propagates events coming from within.

QWidget.event() vs. PWidget.event_handler
    They are indeed similar in behaviour, although overriding .event()
    involves knowing exactly what is being overridden which would involve
    source-diving into the Qt C++ code of which I am not qualified.

    Managing it separately is a safe way forward, whilst keeping the door
    open for transitioning onto .event() once I know more.

"""

import os

from PyQt5 import QtWidgets
from PyQt5 import QtCore


class PWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(PWidget, self).__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)

    def event_handler(self, event):
        """Re-implementation of QtWidget.event()

        Do nothing, cascade all events to compatible PWidgets.

        """

        parent = self.parent()
        if hasattr(parent, 'post_event'):
            parent.post_event(event)

    def post_event(self, event):
        self.event_handler(event)


class Window(PWidget):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        view = List()
        view.setObjectName('List')

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(view)

    def setup(self, paths):
        view = self.findChild(QtWidgets.QWidget, 'List')
        view.setup(paths)

    def event_handler(self, event):
        if event.type() == SelectedEventType:
            print "%s was selected" % event.path

        elif event.type() == RunEventType:
            print "%s was run" % event.path

        elif event.type() == DeleteEventType:
            print "%s was deleted" % event.path

        super(Window, self).event_handler(event)


class List(PWidget):
    """Notice how List isn't aware of any events coming through.

    Events are being handled by our PWidget subclass.

    """

    def __init__(self, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)

        body = PWidget()
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


class Item(PWidget):
    """Superclass to all items

    Intercepts press/hover events for selected
    and alive events respectively.

    """

    def __init__(self, path):
        super(Item, self).__init__(None)
        self.path = path

        basename = os.path.basename(path)
        name, suffix = os.path.splitext(basename)
        label = QtWidgets.QLabel(name)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(label)

    def mousePressEvent(self, event):
        self.selected_event()
        super(Item, self).mousePressEvent(event)

    def selected_event(self):
        custom_event = SelectedEvent(self.path)
        self.post_event(custom_event)


class SpecialItem(Item):
    """Composite item with multiple buttons

    Each button performs a unique task relevant to the item.

    """

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
        self.post_event(custom_event)

    def run_event(self):
        custom_event = RunEvent(self.path + "|Special")
        self.post_event(custom_event)

    def delete_event(self):
        custom_event = DeleteEvent(self.path + "|Special")
        self.post_event(custom_event)


class SecureItem(Item):
    """Plain item subclass, appending data"""
    def selected_event(self):
        custom_event = SelectedEvent(self.path + "|Secure")
        self.post_event(custom_event)


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


SelectedEventType = 1001
RunEventType = 1002
DeleteEventType = 1003

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
