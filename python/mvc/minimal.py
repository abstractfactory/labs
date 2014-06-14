"""Minimal example of MVC in Python

An as small-as-possible demonstration of MVC using Python and PyQt.
When the model changes, its entire content is transmitted along with
the DataChangedEvent. The View then figures out what was different
from its previous state, and reacts accordingly.

This is innefficient for large sets of data, as there are continuous
computations of deltas between the sets upon each change.

A more efficient method is to, instead of transmitting the entire
dataset, to only transmit changes.

UUID
    The relationship between an item in the model and an item in a view
    is maintained via a common UUID. Upon instantiation of a new item into
    the model, a UUID is associated and emitted along with the
    DataAddedEvent event.

    When the view instantiates a new widget, the UUID is stored together
    with it, and used in any communication with the model; such as getting
    the display-label for the widget.

References:
    http://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller
    http://wiki.wxpython.org/ModelViewController
    http://tkinter.unpythonic.net/wiki/ToyMVC

"""

import os

from PyQt5 import QtCore
from PyQt5 import QtWidgets


# -------------------------------------------------------------------
#
# Implement proper propagation of custom events.
# Reference: http://stackoverflow.com/questions/3180506/propagate-custom-qevent-to-parent-widget-in-qt-pyqt/3184510#3184510
#
# -------------------------------------------------------------------


class QApplication(QtWidgets.QApplication):
    def notify(self, receiver, event):
        if event.type() >= QtCore.QEvent.User:
            widget = receiver

            while widget:
                result = widget.event(event)

                if result and event.isAccepted():
                    return result

                widget = widget.parent()

            return False

        return super(QApplication, self).notify(receiver, event)


# -------------------------------------------------------------------
#
# Custom events
#
# -------------------------------------------------------------------


DataChangedEventType = 1001
SelectedEventType = 1002


class DataChangedEvent(QtCore.QEvent):
    """This event is sent whenever there is a change in the model

    The Controller is subscribed to *signals* from the model and posts
    this *event* to the View which then handles the event.

    Events and Signals are similar.

    The general rule is; events propagate and signals do not. Meaning
    signals only reach particular widgets - the subscribers - whereas
    an event is posted and then propagates upwards through the widget
    hierarchy so that other widgets may handle the event as well.

    """

    def __init__(self):
        super(DataChangedEvent, self).__init__(DataChangedEventType)

        # QEvent has its "accepted" flag set per default. For an
        # event to be accepted means that it will not propagate
        # to the next parent. This is a way for widgets to grab
        # onto an event, and tell it to be handled solely by a
        # particular widget, and that it should not be passed along.
        #
        # As we make our custom events specifically to be propagated,
        # we make sure to toggle this default behaviour off.
        self.setAccepted(False)


class SelectedEvent(QtCore.QEvent):
    def __init__(self, name):
        super(SelectedEvent, self).__init__(SelectedEventType)
        self.setAccepted(False)
        self.name = name


# -------------------------------------------------------------------
#
# MVC
#
# -------------------------------------------------------------------


class Item(QtWidgets.QPushButton):

    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        self.released.connect(self.selected_event)

    def selected_event(self):
        """Item is a QPushButton, which has a released signal by default

        When the release signal is emitted, it sends along it's state.
        We aren't interested in its state however; we're interested in
        its content, so we make our own event and append the content
        of this button.

        We also make it into an event, rather than a signal, so that it
        can post the event onto itself, which will make QApplication
        forward the event to its parent and parents parent and so on,
        until it reaches our Controller which is the one interested in
        this event.

        If we instead used signals, we would have to connect each widget
        inbetween Item and Controller manually, which would not only mean
        more work, but would also make our widget hierarchy fixed and thus
        strongly coupled.

        Events help keep the hierarchy arbitrary and independent of content.

        """

        event = SelectedEvent(name=self.text())
        QtWidgets.QApplication.postEvent(self, event)


class View(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        self.old_data = list()

        css = """
        View {
            min-width: 500px;
            min-height: 300px;
        }

        """

        self.setStyleSheet(css)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

    def event(self, event):
        if event.type() == DataChangedEventType:
            """
            The event doesn't send any data along with it and so for
            our view to update, we must first figure out what is
            different from last time we were updated.

            Every time the view updates, it stores a local copy of all
            of the data in the model and then uses that copy for comparison
            upon the next update.

            Not very efficient, of course.

            """

            data = self.model.data
            old_data = self.old_data

            added = list(set(data) - set(old_data))
            removed = list(set(old_data) - set(data))

            for item in added:
                button = Item(item)
                self.add_item(button)

            for item in removed:
                for existing in self.children():
                    if not isinstance(existing, QtWidgets.QWidget):
                        continue

                    if existing.text() == item:
                        existing.deleteLater()

            self.old_data = list(data)
            event.accept()

        return super(View, self).event(event)

    def selected_event(self, name):
        print name

    def set_model(self, model):
        self.model = model

    def add_item(self, item):
        self.layout().addWidget(item)


class Controller(QtWidgets.QWidget):
    def __init__(self, path, parent=None):
        super(Controller, self).__init__(parent)

        model = FileSystemModel()

        # In this module, the controller listens for events from
        # the model. This means that for a controller to make use
        # of a model and a view, it must know the details of both.
        # This isn't necessarily a bad thing, the controller is
        # allowed to have this kind of knowledge, but as you can
        # see below, the event isn't interesting to the controller
        # and is instead posted directly onto the view.
        #
        # The issue with this is two-fold.
        #
        # 1. We're using events to reflect updates from the model.
        # The event will be received by the model, and then bubble
        # back up to here, of which we care very little.
        #
        # 2. If we had more than one view (as is the case in the next
        # example) then the event would be posted to both and then
        # the inner view would post the event back up to its parent;
        # resulting in double events for the upper view.
        #
        # We could solve this by simply accepting the event directly
        # upon receving it; but then this would defeat the purpose
        # of using event for this purpose to begin with.
        #
        # That is why in the following examples, signals are sent
        # directly to views and to not bubble up.
        model.data_changed.connect(self.data_changed_event)

        view = View()
        view.set_model(model)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(view)

        self.view = view
        self.model = model

        model.setup(path)

    def event(self, event):
        if event.type() == SelectedEventType:
            self.model.remove_item(event.name)

        return super(Controller, self).event(event)

    def data_changed_event(self):
        event = DataChangedEvent()
        QtWidgets.QApplication.postEvent(self.view, event)


class FileSystemModel(QtCore.QObject):
    """This model will populate itself with content from a file-system

    Notes:
    data_changed -- The model uses signals as opposed to events because
                    events in a model makes little sense when propagated.
                    These events are meant for very specific subscribers.

    self.data    -- As opposed to hierarchical.py, this model is
                    1-dimensional and can only cope with very simple
                    objects - strings. Each string take the form of a
                    file-system path which is de-composed into the name
                    of each button within the QPushButton subclass.

    """

    data_changed = QtCore.pyqtSignal()

    def __init__(self):
        super(FileSystemModel, self).__init__()

        self.data = list()

    def setup(self, path):
        count = 0
        for item in os.listdir(path):

            # Content filtering
            if item.startswith('.'):
                continue

            self.add_item(item)

            # Content limit
            count += 1
            if count > 10:
                break

    def add_item(self, item):
        self.data.append(item)
        self.data_changed.emit()

    def remove_item(self, item):
        self.data.remove(item)
        self.data_changed.emit()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    c = Controller(r'c:\users\marcus')
    c.show()

    app.exec_()
