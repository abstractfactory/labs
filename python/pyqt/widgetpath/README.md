# Widget Path

Construct a path of widgets within a given hierarchy of widgets, similar to Unix file-system paths.

```bash
$ /app.QWidget/body.QWidget/button.QPushButton
```

### Type

Each part of a path consists of a name (the objectName) and type (class) to uniquely identify a widget within a hierarchy of widgets.

```bash
<name>.<type>
```