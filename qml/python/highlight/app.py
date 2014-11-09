"""Python start-up script for QML application

The application registers a Filesystem type into QML
which is then used to display the contents of a directory,
also chosen via QML.

"""

import os
import sys

from PyQt5 import QtWidgets, QtCore, QtQml


# This is the type that will be registered with QML.
# It must be a sub-class of QObject.
class Filesystem(QtCore.QObject):
    def __init__(self, parent=None):
        super(Filesystem, self).__init__(parent)

    @QtCore.pyqtSlot(str, result="QStringList")
    def listdir(self, path=None):
        """Exposed function to QML

        Note input parameter specified in decorator, along with output format

        """

        return os.listdir(path or os.getcwd())


app = QtWidgets.QApplication(sys.argv)

QtQml.qmlRegisterType(Filesystem, 'Os', 1, 0, 'Filesystem')

engine = QtQml.QQmlApplicationEngine()


def finish_load(obj, url):
    if obj is not None:
        obj.show()
        app.exec_()
    else:
        sys.exit()


engine.objectCreated.connect(finish_load)
engine.load(QtCore.QUrl.fromLocalFile("app.qml"))
