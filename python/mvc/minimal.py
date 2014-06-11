"""Minimal example of MVC in Python

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
    def __init__(self):
        super(DataChangedEvent, self).__init__(DataChangedEventType)
        self.setAccepted(False)  # Not accepted per default


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
