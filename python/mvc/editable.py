"""Editable MVC example

The difference between this and multisource.py is items being editable.

Layout:
     _________________________________
    |  _____________________________  |<----- controller
    | |     |     |     |     |     | |
    | |     |     |     |     |     |<----- miller 1
    | |     |     |     |     |   <------ list
    | |_____|_____|_____|_____|_____| |
    |  _____________________________  |
    | |     |     |     |           | |
    | |     |     |     |           | |
    | |     |     |     |           |<----- miller 2
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
        DataAddedEvent event. This UUID is referred to as `index`

                        __   __
                       |       |
                       | index |
                       | index |
                       | index |
                  .--->|  ...  |<----.
                 |     |       |     |
                 |     |__   __|     |
             ____|____           ____|____
            |         |         |         |
            |  Model  |         |   View  |
            |_________|         |_________|
              |       |           |       |
              | item1 |           | item1 |
              | item2 |           | item2 |
              |  ...  |           |  ...  |
              |_______|           |_______|


        When the view instantiates a new widget, the UUID is stored together
        with it, and used in any communication with the model; such as getting
        the display-label for the widget.

    Model responsibility
        The model is the only component with access to the file-system.
        Items are dumb data-containers and data origin are distinguished
        via the "scheme" part of their URI.

    URI
        Data sources are distinguished via a URI that looks like this:
            <source>:<path>

        E.g.
            disk:/home/marcus
            memory:/my/item

        When the model are tasked with returning the children of
        disk:/home/marcus it will query the file-system. When instead
        tasked with memory:/my/item it will look directly inside the dumb
        item-container for its children, as they are merely in-memory.

    Model and Events
        Models emits signals instead of events. Signals only target
        interested recipients, whereas events propagate up through an
        hierarchy of objects. In this example, there are two unique
        views - ListView and MillerView, both observing the same model.
        When an event is emitted from the model, it is received by both
        views as they are both subscribed to its events.

        If events would be used, the inner view, ListView, would receive
        an event and them propagate it upwards. But as MillerView receives
        the same event, it would receive the event twice; once from the model
        and once from the propagated event coming up from ListView.


Features:
    1. Multiple sources
    2. Multiple views
    3. Editability

    Multiple Sources
        Items may be drawn from either disk or in-memory, based on a URI

    Multiple Views
        The same model draws two views, both editable

    Editability
        Double-clicking on an item will cause it to be editable. Edits
        are reflected in other views, as well as internally in headers
        of existing lists.

        Removing an item will cause any open list of said item to be
        deleted along with any of opened children.

Events:
    RemoveItemEvent:    Controller requests an item to be removed
    AddItemEvent:       Controller requests an item be added
    EditItemEvent:      Controller requests an item to be edited
    AcceptEditEvent:    Edit was accepted and may be inserted into model
    SelectedEvent:      An item was selected in a view

"""

from __future__ import absolute_import

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

            # In cases where `widget` has no parent,
            # notify must still return something valid.
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
class AddItemEvent(BaseEvent):
    def __init__(self, index):
        super(AddItemEvent, self).__init__()
        self.index = index
        self.view = None


@EventType.register
class RemoveItemEvent(BaseEvent):
    def __init__(self, index):
        super(RemoveItemEvent, self).__init__()
        self.index = index
        self.view = None


@EventType.register
class EditItemEvent(BaseEvent):
    def __init__(self, index):
        super(EditItemEvent, self).__init__()
        self.index = index
        self.view = None


@EventType.register
class AcceptEditEvent(BaseEvent):
    def __init__(self, data, index):
        super(AcceptEditEvent, self).__init__()
        self.data = data
        self.index = index
        self.view = None


@EventType.register
class SelectedEvent(BaseEvent):
    def __init__(self, index):
        super(SelectedEvent, self).__init__()
        self.index = index


# -------------------------------------------------------------------
#
# Model items
#
# -------------------------------------------------------------------


def create_index():
    """Helper function"""
    return unicode(uuid4())


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
        return self.data(role='display')

    def __repr__(self):
        return u"%s.%s(%r)" % (__name__,
                               type(self).__name__,
                               self.__str__())

    def __init__(self, uri, parent=None):
        assert ":" in uri
        self.uri = uri
        self.index = None
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

    def set_data(self, value, role):
        if role == 'display':
            self.uri = ":".join([self.scheme, value])

    def add_child(self, item):
        self.children.append(item)

    def remove_child(self, item):
        self.children.remove(item)


class Model(QtCore.QObject):
    data_changed = QtCore.pyqtSignal(str)  # UUID
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
        self.root_item = None
        self.indexes = dict()

    def data(self, index, role):
        """Return `role` from `index`

        Supported roles:
            display

        """

        item = self.indexes[index]
        return item.data(role=role)

    def set_data(self, index, value, role):
        item = self.indexes[index]
        item.set_data(value=value, role=role)

        index = self.index(item)
        self.data_changed.emit(index)

    def children(self, index):
        """Traversing items is the responsibility of the model

        The model has access to network, file-system and any arbitrary
        data-store - whereas items are plain containers with a dedicated
        scheme, indicating from where to "pull" children.

        """

        root = self.indexes[index]

        if not root.has_children and os.path.isdir(root.path):
            scheme = root.scheme

            if scheme == 'disk':
                for child in os.listdir(root.path):
                    full_path = os.path.join(root.path, child)
                    index = create_index()
                    uri = scheme + ":" + full_path

                    item = ModelItem(uri=uri, parent=root)
                    item.index = index
                    self.indexes[index] = item

            if scheme == 'widget':
                print "Listing children of: %s" % 2

        for child in root.children:
            yield child

    def setup(self, uri):
        index = create_index()

        root_item = ModelItem(uri=uri, parent=None)
        root_item.index = index
        self.indexes[index] = root_item

        self.root_item = root_item
        self.model_reset.emit()

    def item(self, index):
        """Get item from `index`"""
        return self.indexes[index]

    def index(self, item):
        """Get index from `item`"""
        indexes = {v: k for k, v in self.indexes.items()}
        return indexes[item]

    def add_item(self, uri, parent=None):
        if not parent:
            parent = self.root_item

        index = create_index()
        item = ModelItem(uri=uri, parent=parent)
        item.index = index
        self.indexes[index] = item

        self.data_added.emit(index)

        # Return None.
        # Use the data_added signal to retrieve UID.
        return None

    def remove_item(self, index):
        self.indexes.pop(index)
        self.data_removed.emit(index)

    def reset(self):
        while self.indexes:
            self.indexes.pop()

        # Re-register root_item
        root_index = self.root_item.index
        self.indexes[root_index] = self.root_item

        self.model_reset.emit()

    def count(self):
        """Return number of items in model"""
        return len(self.indexes)


# -------------------------------------------------------------------
#
# View items
#
# -------------------------------------------------------------------


class Item(QtWidgets.QPushButton):

    def __init__(self, label, index, parent=None):
        super(Item, self).__init__(label, parent)
        self.released.connect(self.selected_event)
        self.index = index

        self.setCheckable(True)
        self.setAutoExclusive(True)

    def action_event(self, state):
        action = self.sender()
        label = action.text()

        if label == "Add":
            event = AddItemEvent(index=self.index)
            QtWidgets.QApplication.postEvent(self, event)

        elif label == "Remove":
            event = RemoveItemEvent(index=self.index)
            QtWidgets.QApplication.postEvent(self, event)

        elif label == "Edit":
            event = EditItemEvent(index=self.index)
            QtWidgets.QApplication.postEvent(self, event)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)

        for label in ("Add",
                      "Remove",
                      "Edit"):
            action = QtWidgets.QAction(label,
                                       self,
                                       triggered=self.action_event)
            menu.addAction(action)

        menu.exec_(event.globalPos())

    def mouseDoubleClickEvent(self, event):
        event = EditItemEvent(index=self.index)
        QtWidgets.QApplication.postEvent(self, event)

    def selected_event(self):
        event = SelectedEvent(index=self.index)
        QtWidgets.QApplication.postEvent(self, event)


class EditorItem(QtWidgets.QWidget):
    def __init__(self, label, index, parent=None):
        super(EditorItem, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.index = index

        editor = QtWidgets.QLineEdit()
        editor.setText(label)
        editor.returnPressed.connect(self.accept_event)
        editor.installEventFilter(self)

        l = QtWidgets.QHBoxLayout(self)
        l.addWidget(editor)
        l.setContentsMargins(0, 0, 0, 0)

        self.editor = editor

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.FocusOut:
            self.close()

        return super(EditorItem, self).eventFilter(obj, event)

    def show(self):
        super(EditorItem, self).show()
        self.editor.setFocus(True)
        self.raise_()

    def set_text(self, text):
        self.editor.setText(text)

    def accept_event(self):
        event = AcceptEditEvent(data=self.editor.text(), index=self.index)
        QtWidgets.QApplication.postEvent(self, event)

        self.close()


class NewItem(QtWidgets.QPushButton):
    def __init__(self, index, parent=None):
        super(NewItem, self).__init__(parent)
        self.index = index
        self.setText('+')
        self.released.connect(self.new_event)

    def new_event(self):
        event = AddItemEvent(index=self.index)
        QtWidgets.QApplication.postEvent(self, event)


class HeaderItem(QtWidgets.QPushButton):
    pass


class Listview(QtWidgets.QWidget):
    def __init__(self, index, parent=None):
        super(Listview, self).__init__(parent)

        # Without this, the window would cause items to clip
        # labels of contained items.
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                           QtWidgets.QSizePolicy.MinimumExpanding)

        self.index = index
        self.indexes = dict()
        self.items = list()
        self.model = None
        self.__signals = list()

        l = QtWidgets.QVBoxLayout(self)
        l.setAlignment(QtCore.Qt.AlignTop)
        l.setSpacing(0)
        l.setContentsMargins(0, 0, 0, 0)

    def event(self, event):
        if event.type() in (EventType.AddItemEvent,
                            EventType.RemoveItemEvent,
                            EventType.EditItemEvent):
            # Enrich event
            if event.index in self.indexes:
                event.view = self

        return super(Listview, self).event(event)

    def set_model(self, model):
        self.model = model

        signals = {
            model.data_changed: self.data_changed_event,
            model.data_added: self.data_added_event,
            model.data_removed: self.data_removed_event,
            model.model_reset: self.model_reset_event
        }

        for slot, sub in signals.iteritems():
            slot.connect(sub)

        self.clear()

        label = model.data(index=self.index, role='display')
        header = HeaderItem(label)
        header.setObjectName('Header')
        newitem = NewItem(self.index)
        newitem.setObjectName('New')

        self.layout().insertWidget(0, header)
        self.layout().addWidget(newitem)

        # Add items
        for model_item in model.children(index=self.index):
            index = model_item.index
            label = model.data(index=index, role='display')
            self.add_item(label, index)

        # Store reference for .release()
        self.__signals.extend(signals.items())

    def clear(self):
        while self.items:
            item = self.items.pop()
            item.deleteLater()

    def add_item(self, label, index):
        item = Item(label, index=index, parent=self)

        l = self.layout()
        l.insertWidget(l.count() - 1, item)

        self.items.append(item)
        self.indexes[index] = item

    def remove_item(self, index):
        item = self.indexes.pop(index)
        item.deleteLater()

    def data_changed_event(self, index):
        if index in self.indexes:
            data = self.model.data(index=index, role='display')
            widget = self.indexes[index]
            widget.setText(data)

    def data_added_event(self, index):
        model_item = self.model.item(index)
        model_parent_item = model_item.parent

        # Only update list if change was related to it.
        if model_parent_item.index == self.index:
            label = self.model.data(index=index, role='display')
            self.add_item(label, index=index)

    def data_removed_event(self, index):
        if index in self.indexes:
            self.remove_item(index)

    def model_reset_event(self):
        pass

    def release(self):
        """Clean up self

        Without explicitly disconnecting the signals, old subscribed
        lists will linger and cause this warning message to appear:

            QCoreApplication::postEvent: Unexpected null receiver

        """

        for slot, sub in self.__signals:
            slot.disconnect(sub)
        self.deleteLater()


class MillerView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MillerView, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)

        self.lists = list()
        self.indexes = dict()
        self.model = None
        self.__signals = list()

        # This is where we'll store all ListViews
        l = QtWidgets.QHBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        l.setAlignment(QtCore.Qt.AlignLeft)
        l.setSpacing(0)

    def set_model(self, model):
        signals = {
            model.data_changed: self.data_changed_event,
            model.data_added: self.data_added_event,
            model.data_removed: self.data_removed_event,
            model.model_reset: self.model_reset_event
        }

        for slot, sub in signals.iteritems():
            slot.connect(sub)

        self.model = model
        self.__signals.extend(signals.items())

    def clear(self):
        while self.lists:
            lis = self.lists.pop()
            lis.release()

    def add_list(self, index):
        """Add new list-view

         ________________
        |lis |child |    |
        |    |++++++|    |
        |    |++++++|    |
        |    |++++++|    |
        |    |++++++|    |
        |____|++++++|____|

        """

        model_item = self.model.item(index)

        # If `index` has parents already visible in the view
        # make sure to remove these before adding a new one.
        model_parent = model_item.parent
        if model_parent:
            lis = self.indexes.get(model_parent.index, None)
            if lis:
                idx = self.lists.index(lis)
                while len(self.lists) > idx + 1:
                    lis = self.lists.pop()
                    lis.release()
                    self.indexes.pop(lis.index)

        # Add list to the left
        lis = Listview(index=index)
        lis.set_model(self.model)  # Re-use model

        self.lists.append(lis)
        self.layout().addWidget(lis)

        # The UID is the link between model and view
        self.indexes[index] = lis

        return lis

    def remove_list(self, index):
        """Remove list associated with `index`

        Also remove all lists to the left of that list.

        """

        lis = self.indexes.get(index, None)

        idx = self.lists.index(lis)
        while len(self.lists) > idx:
            lis = self.lists.pop()
            lis.release()
            self.indexes.pop(lis.index)

    def event(self, event):
        if event.type() == EventType.SelectedEvent:
            model_item = self.model.item(event.index)
            self.add_list(index=model_item.index)

        return super(MillerView, self).event(event)

    def data_added_event(self, index):
        if index in self.indexes:
            assert False, "No addition to the model can have any affect here"

    def data_changed_event(self, index):
        if index in self.indexes:
            # Only act if index is present
            data = self.model.data(index=index, role='display')
            listview = self.indexes[index]
            header = listview.findChild(HeaderItem, 'Header')
            header.setText(data)

    def data_removed_event(self, index):
        if index in self.indexes:
            self.remove_list(index)

    def model_reset_event(self):
        self.clear()

        item = self.model.root_item
        self.add_list(index=item.index)

    def release(self):
        """Clean up self"""
        for slot, sub in self.__signals:
            slot.disconnect(sub)
        self.deleteLater()


class Controller(QtWidgets.QWidget):
    def __init__(self, uri, parent=None):
        super(Controller, self).__init__(parent)

        model = Model()

        label1 = QtWidgets.QLabel('View 1')
        label2 = QtWidgets.QLabel('View 2')

        label1.setAlignment(QtCore.Qt.AlignCenter)
        label2.setAlignment(QtCore.Qt.AlignCenter)

        miller1 = MillerView()
        miller2 = MillerView()

        miller1.set_model(model)
        miller2.set_model(model)

        l = QtWidgets.QVBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        l.setAlignment(QtCore.Qt.AlignTop)
        l.addWidget(label1)
        l.addWidget(miller1)
        l.addWidget(label2)
        l.addWidget(miller2)

        self.miller1 = miller1
        self.miller2 = miller2
        self.model = model

        self.model.setup(uri)

        # Append debug items
        # model.add_item('memory:test1')
        # model.add_item('memory:test2')
        # model.add_item('memory:test3')
        model.add_item('disk:c:\studio')
        model.add_item('tcp://127.0.0.1:5555/c/studio')
        # model.add_item('widget:/Controller')

    def event(self, event):
        """Handle events coming in from items

        Events
            AddItemEvent    -- Add an item to model
            RemoveItemEvent -- Remove an item from model
            EditItemEvent   -- Pop up an editor
            AcceptEditEvent -- Edit item in model

        """

        if event.type() == EventType.AddItemEvent:
            item = self.model.item(event.index)
            self.model.add_item(uri='memory:test%i' % self.model.count(),
                                parent=item)

        elif event.type() == EventType.RemoveItemEvent:
            self.model.remove_item(event.index)

        elif event.type() == EventType.EditItemEvent:
            label = self.model.data(index=event.index, role='display')

            edited = event.view.indexes[event.index]
            parent = edited.parent()

            editor = EditorItem(label, index=event.index, parent=parent)

            # Overlap edited
            editor.resize(edited.size())
            editor.move(edited.pos())

            editor.show()

        elif event.type() == EventType.AcceptEditEvent:
            item = self.model.item(event.index)
            data = event.data

            self.model.set_data(index=event.index,
                                value=data,
                                role='display')

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
