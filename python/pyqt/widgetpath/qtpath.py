"""Path manipulation for Qt Widgets.

Goal:
    Mimic os.path as much as possible. The main exception being
    the presence of `root` for the majority of functions.

    os.path would need it too, unless there was already a fixed
    point in your system for access to the file-system.

"""


from PyQt5 import QtWidgets


class Demo(QtWidgets.QWidget):
    """
    Object hierarchy looks like this:
        /Win.Demo/Body.QWidget/Button.QPushButton

    """

    def __init__(self, parent=None):
        super(Demo, self).__init__(parent)

        body = QtWidgets.QWidget()

        button = QtWidgets.QPushButton('Hello World')

        layout = QtWidgets.QHBoxLayout(body)
        layout.addWidget(button)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(body)

        for name_, widget_ in {
                'Win': self,
                'Body': body,
                'Button': button
                }.iteritems():
            widget_.setObjectName(name_)


def abspath(root, widget):
    """Return path from child widget

    Example:
        >> abspath(button)
        '/Win.Demo/Body.QWidget/Button.QPushButton'

    """

    parts = [root]
    parent = widget
    while parent:
        parts.append(parent)
        parent = parent.parent()
        if parent == root:
            break

    path = []
    for part in parts:
        path.append('{}.{}'.format(part.objectName(),
                                   type(part).__name__))
    path = '/' + '/'.join(path)

    return path


def instance(root, path):
    """Return widget from path

    Example:
        >> instance('/Win.Demo/Body.QWidget/Button.QPushButton')
        QPushButton instance

    """

    parts = path.split('/')
    root = root

    while parts:
        part = parts.pop(0)
        if not part:
            continue

        for child in listwidget(root):
            basename = '{}.{}'.format(child.objectName(),
                                      type(child).__name__)

            if part == basename:
                root = child
            else:
                # Path could not be found
                return None

    return root


def listwidget(widget):
    """os.listdir equivalent"""
    for child in widget.children():
        if not isinstance(child, QtWidgets.QLayout):
            yield child


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = Demo()
    win.show()

    print ""

    but = instance(win, '/Body.QWidget/Button.QPushButton')
    print abspath(win, but)

    sys.exit(app.exec_())
