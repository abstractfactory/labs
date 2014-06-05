"""

Three layers of widgets, inner widget communicating with
outer widget.

 _______________________
|         Top           |
|   _________________   |
|  |      View       |  |
|  |   ___________   |  |
|  |  |   Item    |  |  |
|  |  |           |  |  |
|  |  |___________|  |  |
|  |_________________|  |
|_______________________|

qtpath://Top.QWidget/List1.QWidget/Item1.QWidget


Description:
    In this example, `Model` is the central datastore for items.
    Widgets are generated based on available items and imprinted
    with the UUID of their corresponding data-item.

    Upon an event, the UUID is emitted along with the type of
    event being transmitted. The UUID is then used to lookup
    the corresponding data-item.

"""

from __future__ import absolute_import

from uuid import uuid4
from PyQt5 import QtWidgets
from PyQt5 import QtCore


class DataItem(object):
    def __init__(self, name):
        self.name = name


class WidgetItem(QtWidgets.QPushButton):
    pevent = QtCore.pyqtSignal(tuple)

    def __init__(self, *args, **kwargs):
        super(WidgetItem, self).__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        super(WidgetItem, self).mousePressEvent(event)
        uid = self.property('uid')
        self.pevent.emit(('selected', uid))

    def mouseDoubleClickEvent(self, event):
        super(WidgetItem, self).mousePressEvent(event)
        uid = self.property('uid')
        self.pevent.emit(('doubleclicked', uid))


class Model(object):
    def __init__(self):
        """
        Store items with an id
        {
            '5454-3RWR344-43F34F2F-4F34': item,
            '7654-3786jh4-78838787-8639': item
        }

        """

        self._uids = dict()
        self._items = dict()

    def append_item(self, item):
        uid = uuid4()

        # Store reference both ways; so we can derive an
        # id from an item, and an item from an id.
        self._uids[uid] = item
        self._items[item] = uid

    @property
    def children(self):
        for item in self._uids:
            yield item

    def item(self, uid):
        return self._uids[uid]

    def uid(self, item):
        return self._items[item]

    def load(self, children):
        for item in children:
            item_obj = DataItem(item)
            self.append_item(item_obj)


class View(QtWidgets.QWidget):
    def __init__(self, model, parent=None):
        super(View, self).__init__(parent)
        self._children = {}

        body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(body)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)

        items = ['Item1', 'Item2', 'Item3']
        model = Model()
        model.load(items)

        self.model = model
        self.set_model(model)

    def set_model(self, model):
        layout = self.layout()
        for uid in model.children:
            item = WidgetItem()
            layout.addWidget(item)

            item.setProperty('uid', uid)
            item.pevent.connect(self.event_handler)

    def event_handler(self, event):
        typ, uid = event
        dataitem = self.model.item(uid)

        if typ == 'selected':
            print "Selected: %s" % dataitem.name

        if typ == 'doubleclicked':
            print "Double clicked: %s" % dataitem.name


class Top(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(Top, self).__init__(*args, **kwargs)
        self.setObjectName('Main')

        body = QtWidgets.QWidget()

        layout = QtWidgets.QHBoxLayout(body)

        for x in range(3):
            name = 'View%i' % x
            lis = View(name)
            lis.setObjectName(name)
            layout.addWidget(lis)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)

    def locations_event(self, path):
        print "%s was received from Top" % path

    def messages_event(self, message):
        print message


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = Top()
    win.show()
    app.exec_()
