"""Hierarchical MVC example

The difference between this and minimal.py is that the `items`
data structure is hierarchical/nested as opposed to one-dimensional.


Layout:
     _________________________________
    |  _____________________________  |<----- controller
    | |     |     |     |     |     | |
    | |     |     |     |     |     | |
    | |     |     |     |     |     |<----- view 1
    | |_____|_____|_____|_____|_____| |
    |  _____________________________  |
    | |     |     |     |           | |
    | |     |     |     |           | |
    | |     |     |     |           |<----- view 2
    | |_____|_____|_____|___________| |
    |_________________________________|


Architecture:
     _________        ______________
    |         |      |              |           ______
    |  Model  |----->|    View 1    |          /      \
    |         |      |______________|--------->|      |
    |         |       ______________           |      |
    |         |      |              |          |      |
    |         |----->|    View 2    |--------->|      |
    |         |      |______________|          | User |
    |         |       ______________           |      |
    |         |      |              |<---------|      |
    |         |<-----|  Controller  |          \______/
    |_________|      |______________|


Description:
    Two views monitor changes from Model. The user sees the view, and
    interacts with the Controller, which creates and removes items from
    the model. Once modified, the model notifies the views and the views
    update accordingly.

    UUID
        The relationship between an item in the model and an item in a view
        is maintained via a common UUID. Upon instantiation a new item into
        the model, a UUID is associated and emitted along with the
        DataAddedEvent event.

        When the view instantiates a new widget, the UUID is stored together
        with it, and used in any communication with the model; such as getting
        the display-label for the widget.

Features:
    1. Multiple sources
    2. Multiple views

    # Multiple Sources
        Items may be drawn from either disk or in-memory, based on a URI

    # Multiple Views
        The same model draws two views, both editable

Events:
    ModelResetEvent:    Model was reset
    DataChangedEvent:   An item has changed in the model
    DataAddedEvent:     An item has been added to the model
    DataRemovedEvent:   An item has been removed from the model
    RemoveItemEvent:    Controller requests an item to be removed
    AddItemEvent:       Controller requests an item be added
    SelectedEvent:      An item was selected in a view

"""


# standard library
import os
from uuid import uuid4

# vendor library
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


class _Type(object):
    """Event type accessor

    Usage:
        >> if event.type() == EventType.SelectedEvent
        >> if event.type() == EventType.PopupEvent

    """

    registry = dict()

    def __getattr__(self, attr):
        return self.registry[attr]

    def __getitem__(self, item):
        return self.registry[item]

    @classmethod
    def register(self, cls):
        """Register, either use as-is or as decorator

        Example:
            >>> @EventType.register
            ... class MyEvent(..):
            ...

        """

        typ = QtCore.QEvent.registerEventType()
        name = cls.__name__
        self.registry[name] = typ
        return cls


EventType = _Type()


class BaseEvent(QtCore.QEvent):
    def __init__(self):
        name = type(self).__name__
        super(BaseEvent, self).__init__(EventType[name])
        self.setAccepted(False)


@EventType.register
class ModelEvent(BaseEvent):
    """
    These events are triggered from Controller upon
    changes within a model

    """

    def __init__(self, uid):
        super(ModelEvent, self).__init__()
        self.uid = uid


@EventType.register
class DataChangedEvent(ModelEvent):
    pass


@EventType.register
class DataAddedEvent(ModelEvent):
    pass


@EventType.register
class DataRemovedEvent(ModelEvent):
    pass


@EventType.register
class ModelResetEvent(BaseEvent):
    pass


@EventType.register
class AddItemEvent(BaseEvent):
    def __init__(self, uid):
        super(AddItemEvent, self).__init__()
        self.uid = uid
        self.view = None


@EventType.register
class RemoveItemEvent(BaseEvent):
    def __init__(self, uid):
        super(RemoveItemEvent, self).__init__()
        self.uid = uid
        self.view = None


@EventType.register
class SelectedEvent(BaseEvent):
    def __init__(self, uid):
        super(SelectedEvent, self).__init__()
        self.uid = uid


# -------------------------------------------------------------------
#
# Model items
#
# -------------------------------------------------------------------


def create_uid():
    """Helper function"""
    return unicode(uuid4())


# def ModelItem(uri, uid, parent=None):
#     """Helper function"""
#     scheme, path = uri.split(":", 1)

#     Item = None

#     if scheme == 'memory':
#         Item = MemoryModelItem

#     elif scheme == 'disk':
#         Item = FileSystemModelItem

#     else:
#         raise ValueError("URI not recognised: %s" % uri)

#     return Item(path, uid, parent)


class ModelItem(object):

    @property
    def scheme(self):
        return self.uri.split(":", 1)[0]

    @property
    def path(self):
        return self.uri.split(":", 1)[1]

    @property
    def has_children(self):
        return True if self.children else False

    def __str__(self):
        return self.data('display')

    def __repr__(self):
        return u"%s.%s(%r)" % (__name__,
                               type(self).__name__,
                               self.__str__())

    def __init__(self, uri, uid, parent=None):
        assert ":" in uri
        self.uri = uri
        self.uid = uid
        self.children = list()
        self.parent = parent

        if parent:
            parent.add_child(self)

    def data(self, role):
        if role == 'display':
            basename = os.path.basename(self.path)
            name, _ = os.path.splitext(basename)
            return name

        return None

    def add_child(self, item):
        self.children.append(item)

    def remove_child(self, item):
        self.children.remove(item)


class Model(QtCore.QObject):
    data_changed = QtCore.pyqtSignal(str)  # uuid
    data_added = QtCore.pyqtSignal(str)
    data_removed = QtCore.pyqtSignal(str)
    model_reset = QtCore.pyqtSignal()

    def __str__(self):
        return self.name

    def __repr__(self):
        return u"%s.%s(%r)" % (__name__,
                               type(self).__name__,
                               self.__str__())

    def __init__(self, parent=None):
        super(Model, self).__init__(parent)
        self.uids = dict()
        self.root_item = None

    def data(self, role, uid):
        """Return `role` from `uid`"""
        item = self.uids[uid]
        return item.data(role)

    def children(self, uid):
        """Traversing items is the responsibility of the model

        The model has access to network, file-system and any arbitrary
        data-store - whereas items are plain containers with a dedicated
        scheme, indicating from where to "pull" children.

        """

        root = self.uids[uid]

        if not root.has_children and os.path.isdir(root.path):
            scheme = root.scheme
            if scheme == 'disk':
                for child in os.listdir(root.path):
                    child_uid = create_uid()
                    full_path = os.path.join(root.path, child)
                    child_item = ModelItem(uri=scheme + ":" + full_path,
                                           uid=child_uid,
                                           parent=root)
                    self.uids[child_uid] = child_item

        for child in root.children:
            yield child

    def setup(self, uri):
        uid = create_uid()

        root_item = ModelItem(uri=uri, uid=uid, parent=None)
        self.uids[uid] = root_item

        self.root_item = root_item
        self.model_reset.emit()

    def item(self, uid):
        """Get item from `uid`"""
        return self.uids[uid]

    def uid(self, item):
        """Get uid from `item`"""
        uids = {v: k for k, v in self.uids.items()}
        return uids[item]

    def add_item(self, uri, parent=None):
        if not parent:
            parent = self.root_item

        uid = create_uid()
        item = ModelItem(uri=uri + str(len(self.uids)),
                         uid=uid,
                         parent=parent)
        self.uids[uid] = item

        self.data_added.emit(uid)

        # Return None.
        # Use the data_added signal to retrieve UID.
        return None

    def remove_item(self, uid):
        item = self.uids.pop(uid)

        # Physically remove item
        item.remove()

        self.data_removed.emit(uid)

    def modify_item(self, uid, modification):
        uid = self.uids[uid]
        # modify item here
        self.data_removed.emit(uid)

    def reset(self):
        while self.uids:
            self._items.pop()
        self.model_reset.emit()


# -------------------------------------------------------------------
#
# View items
#
# -------------------------------------------------------------------


class Item(QtWidgets.QPushButton):

    def __init__(self, label, uid=None, parent=None):
        super(Item, self).__init__(label, parent)
        self.released.connect(self.selected_event)
        self.uid = uid

        self.setCheckable(True)
        self.setAutoExclusive(True)

    def action_event(self, state):
        action = self.sender()
        label = action.text()

        if label == "Add item":
            event = AddItemEvent(uid=self.uid)
            QtWidgets.QApplication.postEvent(self, event)

        elif label == "Remove":
            event = RemoveItemEvent(uid=self.uid)
            QtWidgets.QApplication.postEvent(self, event)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)

        for label in ("Add item",
                      "Remove"):
            action = QtWidgets.QAction(label,
                                       self,
                                       triggered=self.action_event)
            menu.addAction(action)

        menu.exec_(event.globalPos())

    def selected_event(self):
        event = SelectedEvent(uid=self.uid)
        QtWidgets.QApplication.postEvent(self, event)


class EditorItem(QtWidgets.QWidget):
    pass


class NewItem(QtWidgets.QPushButton):
    def __init__(self, uid, parent=None):
        super(NewItem, self).__init__(parent)
        self.uid = uid
        self.setText('+')
        self.released.connect(self.new_event)

    def new_event(self):
        event = AddItemEvent(uid=self.uid)
        QtWidgets.QApplication.postEvent(self, event)


class HeaderItem(QtWidgets.QPushButton):
    pass


class List(QtWidgets.QWidget):
    def __init__(self, uid, parent=None):
        super(List, self).__init__(parent)

        self.uid = uid
        self.items = list()
        self.model = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

    def set_model(self, model):
        self.clear()

        uid = model.root_item.uid
        label = model.data(role='display', uid=uid)
        header = HeaderItem(label)
        newitem = NewItem(self.uid)

        self.layout().insertWidget(0, header)
        self.layout().addWidget(newitem)

        # Add items
        for model_item in model.children(uid=self.uid):
            label = model_item.data('display')
            uid = model_item.uid
            self.add_item(label, uid)

        self.model = model

    def clear(self):
        while self.items:
            item = self.items.pop()
            item.deleteLater()

    def add_item(self, label, uid):
        item = Item(label, uid=uid, parent=self)

        layout = self.layout()
        layout.insertWidget(layout.count() - 1, item)

        self.items.append(item)

    def remove_item(self, uid):
        item = self.uids.pop(uid)
        item.deleteLater()

    def event(self, event):
        if event.type() == EventType.DataAddedEvent:
            uid = event.uid
            label = self.model.data('display', uid)
            self.add_item(label, uid=uid)

            # Do not propagate
            event.accept()

        return super(List, self).event(event)


class View(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)

        self.lists = list()
        self.uids = dict()
        self.model = None

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.setSpacing(0)

    def set_model(self, model):
        self.clear()

        item = model.root_item
        self.add_list(uid=item.uid)

        model.data_changed.connect(self.data_changed_event)
        model.data_added.connect(self.data_added_event)
        model.data_removed.connect(self.data_removed_event)
        model.model_reset.connect(self.model_reset_event)

        self.model = model

    def clear(self):
        while self.lists:
            item = self.lists.pop()
            item.deleteLater()

    def add_list(self, uid):
        # print "Adding list"
        model_item = self.model.item(uid)

        model_parent = model_item.parent
        if model_parent:
            parent_list = self.uids.get(model_parent.uid, None)

            # Remove all lists to the left of parent_list
            if parent_list:
                index = self.lists.index(parent_list)
                while len(self.lists) > index + 1:
                    lis = self.lists.pop()
                    lis.deleteLater()

                    removed_uid = lis.uid
                    self.uids.pop(removed_uid)

        # Add list to the left
        lis = List(uid=uid)
        lis.set_model(self.model)  # Re-use model

        self.lists.append(lis)
        self.layout().addWidget(lis)

        # The UID is the link between model and view
        self.uids[uid] = lis

        return lis

    def remove_list(self, uid):
        item = self.uids[uid]
        self.lists.remove(item)
        self.uids.remove(uid)
        item.deleteLater()

    def event(self, event):
        if event.type() == EventType.SelectedEvent:
            model_item = self.model.item(event.uid)
            self.add_list(uid=model_item.uid)
            print "Adding list: %s" % model_item.path

        if event.type() == EventType.ModelResetEvent:
            self.clear()

            item = self.model.root_item
            self.add_list(uid=item.uid)

        elif event.type() == EventType.DataAddedEvent:
            item = self.model.item(event.uid)
            parent = item.parent

            try:
                lis = self.uids[parent.uid]
            except KeyError:
                # list isn't visible in this view
                pass
            else:
                lis_event = DataAddedEvent(uid=event.uid)
                QtWidgets.QApplication.postEvent(lis, lis_event)

        elif event.type() == EventType.DataRemovedEvent:
            uid = event.uid
            self.remove_list(uid)
            self.sort()

        elif event.type() in (EventType.AddItemEvent,
                              EventType.RemoveItemEvent):
            # Enrich event
            event.view = self

        return super(View, self).event(event)

    def data_changed_event(self, uid):
        event = DataChangedEvent(uid)
        QtWidgets.QApplication.postEvent(self, event)

    def data_added_event(self, uid):
        event = DataAddedEvent(uid)
        QtWidgets.QApplication.postEvent(self, event)

    def data_removed_event(self, uid):
        event = DataRemovedEvent(uid)
        QtWidgets.QApplication.postEvent(self, event)

    def model_reset_event(self):
        event = ModelResetEvent()
        QtWidgets.QApplication.postEvent(self, event)


class Controller(QtWidgets.QWidget):
    def __init__(self, uri, parent=None):
        super(Controller, self).__init__(parent)

        model = Model()

        label1 = QtWidgets.QLabel('View 1')
        label2 = QtWidgets.QLabel('View 2')

        label1.setAlignment(QtCore.Qt.AlignCenter)
        label2.setAlignment(QtCore.Qt.AlignCenter)

        view1 = View()
        view2 = View()

        view1.set_model(model)
        view2.set_model(model)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addWidget(label1)
        layout.addWidget(view1)
        layout.addWidget(label2)
        layout.addWidget(view2)

        self.view1 = view1
        self.view2 = view2
        self.model = model

        self.model.setup(uri)

        # model.add_item('memory:test')
        # model.add_item('memory:test')
        # model.add_item('memory:test')

    def event(self, event):
        if event.type() == EventType.AddItemEvent:
            item = self.model.item(event.uid)
            self.model.add_item(uri='memory:test', parent=item)

        return super(Controller, self).event(event)


if __name__ == '__main__':
    import sys

    with open('style.css', 'r') as f:
        style = f.read()

    path = os.path.expanduser('~/om')
    # path = os.path.expanduser('~')
    uri = 'disk:' + path

    app = QApplication(sys.argv)
    app.setStyleSheet(style)

    c = Controller(uri)
    c.show()
    c.resize(600, 300)

    app.exec_()
