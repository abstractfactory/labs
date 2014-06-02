from __future__ import absolute_import

# local library
import os
import sys
import time
import json
from functools import partial

# dependencies
import zmq
import PyQt5

from PyQt5 import QtCore
from PyQt5 import QtWidgets

# local library
import chat.lib
import chat.protocol


class Entry(QtWidgets.QWidget):
    def __init__(self, log, parent=None):
        super(Entry, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)

        def setup_header():
            header = QtWidgets.QWidget()

            author = QtWidgets.QLabel(log.author)
            name = QtWidgets.QLabel(log.name)
            gmtime = time.gmtime(log.timestamp)
            asctime = time.asctime(gmtime)
            timestamp = QtWidgets.QLabel(str(log.timestamp))
            level = QtWidgets.QLabel(log.level)
            string = QtWidgets.QLabel(log.string)

            for tag in (author, name, timestamp, level):
                tag.setProperty('tag', True)

            level.setProperty('level', log.level)  # For CSS coloring
            timestamp.setToolTip(asctime)

            layout = QtWidgets.QHBoxLayout(header)
            layout.addWidget(author, 0)
            layout.addWidget(name, 0)
            layout.addWidget(timestamp, 0)
            layout.addWidget(level, 0)
            layout.addWidget(string, 1)
            layout.setContentsMargins(0, 0, 0, 0)

            for _name, _widget in {'Entry': self,
                                   'Author': author,
                                   'Name': name,
                                   'Time': timestamp,
                                   'Level': level,
                                   'String': string}.iteritems():
                _widget.setObjectName(_name)

            return header

        def setup_body():
            body = QtWidgets.QWidget()

            layout = QtWidgets.QHBoxLayout(body)
            layout.setAlignment(QtCore.Qt.AlignLeft)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            return body

        header = setup_header()
        body = setup_body()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(header)
        layout.addWidget(body)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.header = header
        self.body = body
        self.log = log

        self.expand()

    def mousePressEvent(self, event):
        super(Entry, self).mousePressEvent(event)
        if self.body.isVisible():
            self.contract()
        else:
            self.expand()

    def contract(self):
        self.body.hide()

        def kill(body):
            layout = body.layout()
            item = layout.takeAt(0)

            while item:
                widget = item.widget()
                widget.deleteLater()
                item = layout.takeAt(0)

        kill(self.body)

    def expand(self):
        layout = self.body.layout()
        self.body.show()

        count = len(self.log.trace)
        for i in xrange(count):
            mediator = self.log.trace[i]
            label = QtWidgets.QLabel(mediator)

            box = QtWidgets.QWidget()
            box.setObjectName('Box')

            layout_ = QtWidgets.QHBoxLayout(box)
            layout_.addWidget(label)
            layout_.setContentsMargins(0, 0, 0, 0)

            layout.addWidget(box)

            if i != count - 1:
                line = QtWidgets.QWidget()
                line.setObjectName('Line')
                layout.addWidget(line)

            debug_info = chat.lib.pformat(self.log.to_dict())
            box.setToolTip(debug_info)


class Application(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Application, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setWindowTitle('Logger')
        self.setObjectName('Logger')

        container = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(container)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(0)

        scrollarea = QtWidgets.QScrollArea(self)
        scrollarea.setWidget(container)
        scrollarea.setWidgetResizable(True)

        scrollbar = scrollarea.verticalScrollBar()
        scrollbar.rangeChanged.connect(self.scroll)

        self.container = container
        self.scrollarea = scrollarea
        self.previous_entry = None

        chat.lib.spawn(self.listen)

    def listen(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect('tcp://localhost:5556')
        socket.setsockopt(zmq.SUBSCRIBE, 'log')

        print "Running logger.."

        while True:
            header, body = socket.recv_multipart()
            message = json.loads(body)
            log = chat.protocol.Log.from_dict(message)
            QtCore.QTimer.singleShot(0, partial(self.log, log))

    def resizeEvent(self, event):
        super(Application, self).resizeEvent(event)
        self.scrollarea.resize(event.size())

    def log(self, log):
        if self.previous_entry:
            self.previous_entry.contract()

        entry = Entry(log)

        layout = self.container.layout()
        layout.addWidget(entry)

        self.previous_entry = entry

    def scroll(self):
        scrollbar = self.scrollarea.verticalScrollBar()
        if scrollbar.value() >= scrollbar.maximum() - 200:
            scrollbar.setValue(scrollbar.maximum())


def main():
    plugin_path = os.path.join(os.path.dirname(PyQt5.__file__), 'plugins')
    QtWidgets.QApplication.addLibraryPath(plugin_path)

    app = QtWidgets.QApplication(sys.argv)

    css = os.path.join(os.path.dirname(__file__), 'gui.css')
    with open(css, 'r') as css:
        app.setStyleSheet(css.read())

    appplication = Application()
    appplication.resize(600, 500)
    appplication.show()

    sys.exit(app.exec_())
