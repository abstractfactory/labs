import os
import argparse
import threading
import subprocess


def spawn(func, **kwargs):
    thread = threading.Thread(target=func, **kwargs)
    thread.daemon = True
    thread.start()


clear_console = lambda: subprocess.call(
    'cls'
    if os.name == 'nt'
    else 'clear',
    shell=True)


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)

    def exit(self, status=0, message=None):
        raise SystemExit(message)


def _expand_list(obj,
                 indent=4,
                 title=False,
                 separator=': ',
                 _lines=None,
                 level=0):

    _lines = _lines or list()

    def append(value):
        value = (value.title()
                 if isinstance(value, basestring)
                 else value)

        template = '{level}{value}'
        line = template.format(level=' ' * indent * level,
                               value=value)
        _lines.append(line)

    for value in obj:
        if isinstance(value, list):
            _expand_list(obj=value,
                         indent=indent,
                         title=title,
                         separator=separator,
                         level=level + 1,
                         _lines=_lines)
            continue

        append(value)

    return _lines


def _expand_dict(obj,
                 indent=4,
                 title=False,
                 separator=': ',
                 level=0,
                 _lines=None):

    _lines = list() if _lines is None else _lines

    def append(key, value=''):
        if title:
            key = key.title()
            value = (value.title()
                     if isinstance(value, basestring)
                     else value)

        template = "{level}{key}{sep}{value}"
        line = template.format(level=' ' * indent * level,
                               sep=separator if value is not None else '',
                               key=key,
                               value=value)
        _lines.append(line)

    for key, value in sorted(obj.iteritems()):
        if isinstance(value, dict):
            append(key)
            _expand_dict(obj=value,
                         indent=indent,
                         title=title,
                         separator=separator,
                         _lines=_lines,
                         level=level + 1)
            continue

        if isinstance(value, list):
            append(key)
            _expand_list(obj=value,
                         indent=indent,
                         title=title,
                         separator=separator,
                         _lines=_lines,
                         level=level + 1)
            continue

        append(key, value)

    return _lines


def pformat(obj, indent=4, title=False, separator=': ', level=0):
    """Pretty-format a JSON-compatible collection"""
    lines = list()

    if isinstance(obj, dict):
        expanded = _expand_dict(obj,
                                indent=indent,
                                title=title,
                                separator=separator,
                                level=level)
        lines.extend(expanded)

    elif isinstance(obj, list):
        expanded = _expand_list(obj,
                                indent=indent,
                                title=title,
                                separator=separator,
                                level=level)
        lines.extend(expanded)

    else:
        # Unhandled
        lines.append(str(obj))

    output = ''
    for line in lines:
        line = line.replace("_", " ")
        output += '%s\n' % line

    return output


def pprint(obj,
           indent=4,
           title=False,
           separator=': ',
           level=0):
    """Pretty-print a JSON-compatible collection"""
    print pformat(obj,
                  indent=indent,
                  title=title,
                  separator=separator,
                  level=level)


if __name__ == '__main__':
    obj = {
        'hello': 'world',
        'this is': ['pluto', 'calling', ['another', 'list']],
        'deep': {
            'and ugly': {
                'long': 'nest',
                'another': 'dict',
                'with': ['a',
                         'big',
                         'syringe']
            }
        }
    }

    pprint(obj, title=True, separator='=', level=1)
