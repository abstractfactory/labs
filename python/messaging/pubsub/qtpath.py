"""Path serialisation/deseriasation for Qt Widgets.

Goal
    Mimic os.path as much as possible. The main exception being
    the presence of `root` for the majority of functions.

    os.path would need it too, unless there was already a fixed
    point in your system for access to the file-system.

Syntax
    We utilise QWidget.findChild() for widget lookup, which
    requires both name and type. Due to this, paths are formatted
    by name + type:

        - <name>.<type>
        - MyButton.QPushButton

"""


def abspath(root, widget):
    """os.abspath equivalent

    Example:
        >> abspath(window, button)
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
        name = part.objectName()
        typ = type(part).__name__

        if name:
            basename = '{}.{}'.format(name, typ)
            path.append(basename)

    path = '/' + '/'.join(path)

    return path


def relpath(root, widget):
    """os.relpath equivalent"""


def instance(root, path):
    """Get instance from path

    Recursively look for each part of path until found.
    None found returns None.

    Example:
        >> instance(window, '/Body.QWidget/Button.QPushButton')
        <QPushButton object at 0x000000000342344D32>

    """

    parts = path.split('/')
    root = root

    while parts:
        part = parts.pop(0)
        if not part:
            continue

        root = find(root, part)
        if not root:
            return None

    return root


def find(root, basename):
    """Find first occurence of `basename` in `root`

    Example
        >> find(window, 'Button.QPushButton')
        <QPushButton object at 0x000000000342344D32>

        >> find(window, 'Missing.QWidget')
        None

    """

    for child in listwidget(root):
        if basename == formatted(child):
            return child


def formatted(root):
    return '{objectname}.{type}'.format(
        objectname=root.objectName(),
        type=type(root).__name__)


def listwidget(root):
    """os.listdir equivalent

    Example
        >> for child in listwidget(window):
        ...   print child
        <QWidget object at 0x000000000342344D32>
        <QPushButton object at 0x000000000342344D32>

    """

    for child in root.children():
        # Uniquely identify instances of
        # QWidget without importing PyQt5.
        mro = [o.__name__ for o in type(child).__mro__]
        if 'QWidget' in mro:
            yield child


def walk(widget):
    """os.walk equivalent"""
