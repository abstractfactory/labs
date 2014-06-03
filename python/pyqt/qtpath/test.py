from __future__ import absolute_import

# PyQt5 library
from PyQt5 import QtWidgets

# local library
import qtpath


class Demo(QtWidgets.QWidget):
    """
    Object hierarchy looks like this:
        Win (Demo)
        |-- Body (QWidget)
            |-- Button (QPushButton)

    Which translates into:
        /Win.Demo/Body.QWidget/Button.QPushButton

    """

    def __init__(self, parent=None):
        super(Demo, self).__init__(parent)

        body = QtWidgets.QWidget()

        demo_button = QtWidgets.QPushButton('Hello Demo')
        body_button = QtWidgets.QPushButton('Hello Body')

        layout = QtWidgets.QHBoxLayout(body)
        layout.addWidget(body_button)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(demo_button)
        layout.addWidget(body)

        for widget_, name_ in {
                self: 'Win',
                body: 'Body',
                demo_button: 'Button',
                body_button: 'Button',
                }.iteritems():
            widget_.setObjectName(name_)


if __name__ == '__main__':
    import sys

    # Set-up PyQt application
    app = QtWidgets.QApplication(sys.argv)
    win = Demo()

    # How we would normally find `Button` within `Demo`
    find_button = win.findChild(QtWidgets.QPushButton, 'Button')

    # Get an instance from `Demo` by serialised path
    button = qtpath.instance(win, '/Body.QWidget/Button.QPushButton')
    button = qtpath.instance(win, '/Button.QPushButton')
    assert find_button == button

    # Get back the serialised path from instance.
    assert qtpath.abspath(win, button) == '/Win.Demo/Button.QPushButton'

    # A path may return nothing
    missing = qtpath.instance(win, '/Body.QWidget/Checkbox.QWidget')
    assert missing is None

    # findPath searches a hierarchy, regardless of proximity to root
    # The following will return `Button` closest to `Win`, there is no
    # way to directly reference the nested `Button`.
    button = win.findChild(QtWidgets.QPushButton, 'Button')
    assert button.parent() == win

    button = qtpath.instance(win, '/Body.QWidget/Button.QPushButton')
    assert button is not find_button
