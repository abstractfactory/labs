#!c:\Python27\python
"""The Command Pattern
 
An illustration of how the Command Pattern can be used
to facilitate scripting and multi-level undo/redo.
 
In this example, the user works against an in-memory
datastore, DATASTORE (see below); creates, modified and
deletes values, while the Invoker keeps track of what
happens in which order; the user may then undo previous
commands with the `undo` command.
 
Features:
    - Create, Update and Delete data
    - Undo/redo, for commands that support it (e.g. not 'cls')
    - Acyclic undo/redo, undoing a command doesn't record its inverse
    - Next/previous command using arrow keys
    - Visualise history
    - Visualise data
    - Display help
    - Per-command help

Usage:
    Run in a shell; available commands will be given to you
    upon first run.

Commands:
    create(key, value)  -- Create new entry
    delete(key)         -- Remove existing entry
    update(key, value)  -- Update existing entry
    undo                -- Undo last command
    redo                -- Redo last command
    history             -- Display available history
    data                -- Display available data
    cls                 -- Clear the console window
    verbosity(level)    -- Level or verbosity (info, warning, error)
    help(command)       -- Help on an individual command
    exit                -- Exit

Example:
    command> create age 5
    command> creage length 0.76
    command> undo

Design:
    These are some of the design decisions made in this example,
    each of which could be implemented differently:

    DES01 - Each command is encapsulated into an object, a subclass
    of AbstractCommand.

    DES02 - Undoable commands store their opposite command within
    their undo method.

    DES03 - Instances of AbstractCommand objects are stored within a
    sorted list, both for undo and redo.

    DES04 - Class- and command-names are tightly coupled; this is
    so that no command can ever be defined twice.

    DES05 - History stored a class attributes; this is so that
    commands can access/modify it on their own, without requiring
    knowlege of its invoker.

Reference:
    http://en.wikipedia.org/wiki/Command_pattern
    https://github.com/gennad/Design-Patterns-in-Python/blob/master/command.py

"""

import os
import sys
import subprocess
import logging

log = logging.getLogger("command")

# Log as follows:
#   command> create age 5
#   INFO - created 'age'
formatter = logging.Formatter("%(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
log.addHandler(stream_handler)

# Default verbosity, overriden via the command 'verbosity'
log.setLevel(logging.WARNING)


# In-memory datastore. This is where we'll be reading from
# and writing to in this example.
DATASTORE = {}

# Constants
KEY = "key"
VALUE = "value"

# Cross-platform command for clearing the screen.
clear_cmd = "cls" if os.name == "nt" else "clear"
cls = lambda: subprocess.call(clear_cmd, shell=True)


def name(cls):
    """Return name from subclasses of AbstractCommand"""
    return cls.__name__.rsplit("Command")[0].lower()


def display_help(cmd=None):
    message = """
     {LINE}
    |                                                      |
    | Command Pattern - Demonstration                      |
    | Author: Marcus Ottosson <marcus@abstractfactory.io>  |
    |{LINE}|

* Available commands""".format(LINE='_'*54)

    if cmd:
        cls = Invoker.COMMANDS.get(cmd)
        if cls:
            print cls.__doc__
        else:
            print "No help found for %r" % cmd
    else:
        print message
        for cmd in sorted(Invoker.COMMANDS):
            print "    " + cmd
        print ""


class InvalidCommand(Exception):
    pass


class InvalidSignature(Exception):
    pass


class Exists(Exception):
    pass


class AbstractCommand(object):
    """Abstract base class for all commands

    Dynamically append available commands
    as they are subclassed.

    """

    def __init__(self, track=True):
        self.track = track
        self.data = {}

    def do(self, *args):
        return True


class CreateCommand(AbstractCommand):
    """Create a new value in DATASTORE

    Args:
        key: Identifier for value
        value: Value for identifier

    Precondition:
        `key` must not already exist

    Example:
        command> create age 5

    """

    def do(self, *args):
        if not super(CreateCommand, self).do(*args):
            return

        if not len(args) == 2:
            raise InvalidSignature("create: Expected key, value")

        key, value = args

        # Store state, for performing an undo of this command
        self.data[KEY] = key
        self.data[VALUE] = value

        if key in DATASTORE:
            raise Exists("%r already exists, use 'update' instead" % key)

        log.info("Creating %r" % key)

        DATASTORE[key] = value

    def undo(self, *args):
        """Perform the opposite of 'create' - 'delete'"""
        key = self.data[KEY]

        command = DeleteCommand(track=False)
        command.do(key)


class DeleteCommand(AbstractCommand):
    """Delete a value from DATASTORE

    Args:
        key: Identifier for value

    Precondition:
        `key` must already exist

    Example:
        command> delete age

    """

    def do(self, *args):
        if not len(args) == 1:
            raise InvalidSignature("delete: Expected key")

        key = args[0]

        try:
            value = DATASTORE.pop(key)
        except KeyError:
            raise Exists("%r did not exist." % key)

        self.data[KEY] = key
        self.data[VALUE] = value

        log.info("Deleting %r" % key)

    def undo(self, *args):
        """Perform the opposite of 'create' - 'delete'"""
        key = self.data[KEY]
        value = self.data[VALUE]

        command = CreateCommand(track=False)
        command.do(key, value)


class UpdateCommand(AbstractCommand):
    """Update existing value in DATASTORE

    Args:
        key: Identifier for value
        value: Value for identifier

    Precondition:
        `key` must already exist

    Example:
        command> update age 5

    """

    def do(self, *args):
        if not len(args) == 2:
            raise InvalidSignature("update: Expected key, value")

        key, value = args

        try:
            previous_value = DATASTORE[key]
        except KeyError:
            raise Exists("%r did not exist." % key)

        DATASTORE[key] = value

        # Store state
        self.data[KEY] = key
        self.data[VALUE] = previous_value  # Previous value

        log.info("Updating %r from %r --> %r" % (key, previous_value, value))

    def undo(self, *args):
        key = self.data[KEY]
        value = self.data[VALUE]

        command = UpdateCommand(track=False)
        command.do(key, value)


class DataCommand(AbstractCommand):
    """Visualise data in datastore

    Example:
        command> data

    """

    def do(self, *args):
        if args:
            raise InvalidSignature("data: data does not take any arguments")

        if not DATASTORE:
            log.info("No data")
            return

        for key, value in DATASTORE.iteritems():
            print "    %s=%s" % (key, value)


class ClsCommand(AbstractCommand):
    """Clear the current shell buffer

    Example:
        command> cls

    """

    def do(self, *args):
        cls()


class VerbosityCommand(AbstractCommand):
    """Update existing value in DATASTORE

    Args:
        level: available levels are 'info', 'warning' and 'error'

    Example:
        command> verbosity info

    """

    def do(self, *args):
        if not len(args) == 1:
            raise InvalidSignature("verbosity: Expected level")

        level = args[0]

        if level == 'info':
            level = logging.INFO

        elif level == 'warning':
            level = logging.WARNING

        elif level == 'error':
            level = logging.ERROR

        else:
            raise InvalidSignature("Value must be either "
                                   "'info', 'warning' or 'error'")

        log.setLevel(level)


class HelpCommand(AbstractCommand):
    """Display help

    Example:
        command> help
        command> help create
        command> help update

    """

    def do(self, *args):
        display_help(*args)


class UndoCommand(AbstractCommand):
    """Undo last command

    Example:
        command> undo

    """

    def do(self, *args):
        try:
            cmd = Invoker.HISTORY.pop()
            Invoker.TRASH.append(cmd)
            log.info("Undoing %r" % name(type(cmd)))
            cmd.undo()

        except IndexError:
            log.warning("Nothing to undo.")


class RedoCommand(AbstractCommand):
    """Undo last command

    Example:
        command> redo

    """

    def do(self, *args):
        try:
            cmd = Invoker.TRASH.pop()
            Invoker.HISTORY.append(cmd)
            log.info("Redoing %r" % name(type(cmd)))

            key, value = cmd.data[KEY], cmd.data[VALUE]
            cmd.do(key, value)

        except IndexError:
            log.warning("Nothing to redo.")


class HistoryCommand(AbstractCommand):
    """Visualise history

    Example:
        command> history

    """

    def do(self, *args):
        for i in xrange(len(Invoker.HISTORY)):
            cmd = Invoker.HISTORY[i]
            print "    %s: %s (%s=%s)" % (i, name(type(cmd)),
                                          cmd.data[KEY], cmd.data[VALUE])


class ExitCommand(AbstractCommand):
    """Exit

    Example:
        command> exit

    """

    def do(self, *args):
        raise KeyboardInterrupt()


class Invoker(object):
    """Invoker

    Translate string into command object,
    run and store in history.

    """

    COMMANDS = {}
    for cmd in (CreateCommand,
                DeleteCommand,
                UpdateCommand,
                UndoCommand,
                RedoCommand,
                HistoryCommand,
                VerbosityCommand,
                DataCommand,
                ClsCommand,
                HelpCommand,
                ExitCommand):
        COMMANDS[name(cmd)] = cmd

    HISTORY = list()
    TRASH = list()

    @classmethod
    def execute(cls, cmd, *args):
        try:
            command = cls.COMMANDS[cmd]()
        except KeyError:
            raise InvalidCommand("Command %r not found" % cmd)

        command.do(*args)

        # Store in history
        if hasattr(command, "undo") and command.track:

            # Clear redo queue
            while cls.TRASH:
                cls.TRASH.pop()

            cls.HISTORY.append(command)


if __name__ == "__main__":
    cls()
    display_help()

    invoker = Invoker()

    try:
        while True:
            sys.stdout.write("command> ")
            input_ = raw_input()

            parts = input_.split()
            cmd, args = parts[0], parts[1:]

            try:
                invoker.execute(cmd, *args)

            except Exists as e:
                log.error(e)

            except InvalidCommand as e:
                log.error(e)

            except InvalidSignature as e:
                log.error(e)

    except KeyboardInterrupt:
        print("Good bye")
