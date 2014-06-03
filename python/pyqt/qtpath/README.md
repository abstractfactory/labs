# Qt Path

Path serialisation/de-seriasation for Qt widgets.

```bash
$ /Win.Demo/Body.QWidget/Button.QPushButton
```

Compatible with PyQt4, PyQt5 and PySide.

### Type

Each part of a path consists of a name (the objectName) and type (class) to uniquely identify a widget within a hierarchy of widgets.

```bash
<objectName>.<type>
```

### Functions

- abspath

```python
>> abspath(window, button)
'/Win.Demo/Body.QWidget/Button.QPushButton'
```

- relpath
- instance

```python
>> instance(window, '/Body.QWidget/Button.QPushButton')
<QPushButton object at 0x000000000342344D32>
```

- find

```python
>> find(window, 'Button.QPushButton')
<QPushButton object at 0x000000000342344D32>

>> find(window, 'Missing.QWidget')
None
```

- listwidget

```python
>> for child in listwidget(window):
...   print child
<QWidget object at 0x000000000342344D32>
<QPushButton object at 0x000000000342344D32>
```

- walk(widget): os.walk equivalent
