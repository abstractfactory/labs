### Pure-python MVC implementation, based on Qt's MVC framework.

In here are four different implementations, each more feature-rich/complex than the last. In order of complexity:

1. minimal.py
2. hierarchical.py
3. multisource.py
4. editable.py

The docstring of each module explains its purpose and difference; here is an overview.

## Layout

The graphical layout looks like this.

```python
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

```

## Architecture

And the standard MVC architecture looks like this; where Views monitor changes in Model, the User interacts with the Controller which modifies the Model.

```python
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

```python

## Description

In the final example, editable.py, two views monitor changes from Model. The user sees the view, and interacts with the Controller, which creates and removes items from the model. Once modified, the model notifies the views and the views update accordingly.

### UUID

The relationship between an item in the model and an item in a view is maintained via a common UUID. Upon instantiation a new item into the model, a UUID is associated and emitted along with the DataAddedEvent event. This UUID is referred to as `index`

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


    When the view instantiates a new widget, the UUID is stored together with
    it, and used in any communication with the model; such as getting the
    display-label for the widget.

### Model responsibility

The model is the only component with access to the file-system. Items are dumb data-containers and data origin are distinguished  via the "scheme" part of their URI.

### URI

Data sources are distinguished via a URI that looks like this:

```bash
<source>:<path>

# E.g.
disk:/home/marcus
memory:/my/item
```


When the model are tasked with returning the children of disk:/home/marcus it will query the file-system. When instead tasked with memory:/my/item it will look directly inside the dumb item-container for its children, as they are merely in-memory.

### Model and Events

Models emits signals instead of events. Signals only target interested recipients, whereas events propagate up through an hierarchy of objects. In this example, there are two unique views - ListView and MillerView, both observing the same model. When an event is emitted from the model, it is received by both views as they are both subscribed to its events.

If events would be used, the inner view, ListView, would receive an event and them propagate it upwards. But as MillerView receives the same event, it would receive the event twice; once from the model and once from the propagated event coming up from ListView.


### Features

1. Multiple sources
2. Multiple views
3. Editability

#### Multiple Sources

Items may be drawn from either disk or in-memory, based on a URI

#### Multiple Views

The same model draws two views, both editable

#### Editability
Double-clicking on an item will cause it to be editable. Edits are reflected in other views, as well as internally in headers of existing lists.

Removing an item will cause any open list of said item to be deleted along with any of opened children.

#### Events

These are all of the events present in the examples.

- RemoveItemEvent:    Controller requests an item to be removed
- AddItemEvent:       Controller requests an item be added
- EditItemEvent:      Controller requests an item to be edited
- AcceptEditEvent:    Edit was accepted and may be inserted into model
- SelectedEvent:      An item was selected in a view