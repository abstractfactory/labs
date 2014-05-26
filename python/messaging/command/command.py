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

Server-side commands:
    create(key, value)  -- Create new entry
    delete(key)         -- Remove existing entry
    update(key, value)  -- Update existing entry
    data                -- Display available data
    help(command)       -- Help on an individual command

Client-side commands:
    undo                -- Undo last command
    redo                -- Redo last command
    history             -- Display available history
    cls                 -- Clear the console window
    verbosity(level)    -- Level or verbosity (info, warning, error)
    exit                -- Exit

Example:
    command> create age 5
    command> creage length 0.76
    command> undo

Design:
    These are some of the design decisions made in this example,
    each of which could be implemented differently:

    DES01 - Each command is encapsulated into an object

    DES02 - Commands know how to undo themselves

    DES03 - History is stored in a sorted list

    DES04 - Names of commands are coupled with their respective class names

    DES05 - <deprecated>

    DES06 - Client and server both have access to this module.

    DES07 - Commands know what to undo themselves with (i.e. have state)

Reference:
    http://www.oodesign.com/command-pattern.html
    http://en.wikipedia.org/wiki/Command_pattern
    http://www.insomniacgames.com/ron-pieket-a-clientserver-tools-architecture/
    https://github.com/gennad/Design-Patterns-in-Python/blob/master/command.py

"""

import os
import sys
import time
import json
import socket
import random
import logging
import urllib2
import subprocess

stdout = sys.stdout


def setup_log(root):
    log = logging.getLogger(root)

    formatter = logging.Formatter(
        "%(asctime)s "
        "%(message)s",
        '%H:%M:%S')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    return log

log = setup_log("command")

# Default verbosity, overriden via the command 'verbosity'
log.setLevel(logging.WARNING)


# Constants
KEY = 'key'
VALUE = 'value'

# Message keys
STATUS = 'status'
INFO = 'message'
COMMAND = 'command'
ARGS = 'args'
ID = 'id'  # Unique identifier for each executed command
BLOCKING = 'blocking'  # This command should be executed synchronously
UNDO = 'undo'
REDO = 'redo'

# Message values
OK = 'ok'
FAIL = 'fail'

# Cross-platform command for clearing shell
clear_cmd = "cls" if os.name == "nt" else "clear"
cls = lambda: subprocess.call(clear_cmd, shell=True)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("gmail.com", 80))
    except socket.error:
        raise Connection("Could not get local ip address, "
                         "try again later.")

    local_ip = s.getsockname()[0]
    s.close()

    return local_ip


def get_public_ip():
    reply = json.load(urllib2.urlopen('http://httpbin.org/ip'))
    public_ip = reply.get('origin')
    return public_ip


class Datastore(object):
    DATASTORE = {}

    CONGESTIONS = {
        'real': 0,  # Do not simulate
        'instant': 0.02,
        'fast': 0.91,
        'slow': 2.1462,
        'faulty': 5.01
    }

    CONGESTION = CONGESTIONS['fast']  # Default

    size = 3  # Maximum amount of entries
    length = 5
    blocking = True

    def create(self, key, value):

        # Pretend to do heavy-lifting
        self.congest(2, len(value))

        if len(self.DATASTORE) > self.size:
            raise Full("Sorry, I'm full. Use 'delete' to clear things up.")

        if len(value) > self.length:
            raise Length("Can't store data longer than %i "
                         "characters." % self.length)

        if key in self.DATASTORE:
            raise Exists("%r already exists, use 'update' instead" % key)

        self.DATASTORE[key] = value

        log.info("Creating %r" % key)

    def update(self, key, value):
        try:
            previous_value = self.DATASTORE[key]
        except KeyError:
            raise Exists("%r did not exist." % key)

        # Pretend to do heavy-lifting
        self.congest(1, len(value))

        self.DATASTORE[key] = value

        log.info("Updating %r from %r --> %r" % (key, previous_value, value))

        return previous_value

    def delete(self, key):
        try:
            value = self.DATASTORE.pop(key)
        except KeyError:
            raise Exists("%r did not exist." % key)

        # Pretend to do heavy-lifting
        self.congest(1)

        log.info("Deleting %r" % key)

        return value

    def dump(self):
        # Pretend to do heavy-lifting
        self.congest(1.3)
        return self.DATASTORE

    @property
    def congestion(self):
        return self.CONGESTION

    @congestion.setter
    def congestion(self, value):
        self.CONGESTION = value

    def congest(self, multiplier=1, weight=1):
        """Simulate network conditions"""

        # Response/throughput algorithm
        sleep = (
            random.random()
            * self.congestion
            * multiplier
            * (weight * 0.25)
            + weight * self.congestion
        )

        time.sleep(sleep)

    def help(self, cmd=None):
        obj = server_commands.get(cmd)
        if obj:
            return obj.__doc__

        # If command isn't available here, it may
        # be available on the client.
        return 'Which command do you want to know more about?'


def name(cls):
    """Parse class into name

    Convention:
        <name>Command

    Example:
        CreateCommand
        UpdateCommand

    """

    return cls.__name__.rsplit("Command")[0].lower()


def display_help(cmd=None):
    message = """
     ______________________________________________________
    |                                                      |
    | Command Pattern - Demonstration                      |
    |            __________          __________            |
    |           |          | -----> |          |           |
    |           |          | <----- |          |           |
    |           |__________|        |__________|           |
    |                                                      |
    | Author: Marcus Ottosson <marcus@abstractfactory.io>  |
    |______________________________________________________|

* Available commands"""

    if cmd:
        cls = server_commands.get(cmd)
        if cls:
            return cls.__doc__
        else:
            return "No help found for %r" % cmd
    else:
        message_ = message
        for cmd in sorted(server_commands):
            message_ += "\n    %s" % cmd
        message_ += '\n'
        return message_


def init_shell():
    sys.stdout.write('command> ')


class InvalidSignature(Exception):
    """Raised when signature of command is invalid"""
    pass


class Exists(Exception):
    """Raised when command does not exist"""
    pass


class Length(Exception):
    """Raised when a value is too long"""
    pass


class Full(Exception):
    """Raised when the datastore is full"""
    pass


class Server(Exception):
    pass


class Connection(IOError):
    """Raised in the event of any error with connections"""
    pass


class AbstractCommand(object):
    """Abstract base class for all commands"""

    blocking = False

    def __init__(self, receiver):
        self.receiver = receiver
        self.state = {}

    def do(self, *args):
        return


class NetworkCommand(AbstractCommand):
    """Network congestion command

    Simulate the performance of the network.

    Args:
        level:
            'real': Actual network performance
            'instant': Hardly any delay
            'fast': Noticable, but quick
            'slow': Painfully slow
            'faulty': Inhuman

    Example:
        command> network slow

    """

    blocking = True

    def do(self, *args):
        if not len(args) == 1:
            value = self.receiver.congestion

        else:
            try:
                level = args[0]
                value = self.receiver.CONGESTIONS[level]
            except KeyError:
                raise InvalidSignature("network: level not recognised. "
                                       "Type 'help network' for more "
                                       "information.")
            self.receiver.congestion = value

        if value == self.receiver.CONGESTIONS['real']:
            message = 'network congestion simulation off'
        else:
            message = ('average response: %s second(s) | '
                       'average throughput: %s seconds/char'
                       % (value, value * 0.25))
        return message


class CreateCommand(AbstractCommand):
    """Create a new value in DATASTORE

    Args:
        key: Identifier for value
        value: Value for identifier

    Pre-condition:
        `key` must not already exist

    Example:
        command> create age 5

    """

    def do(self, *args):
        if not len(args) == 2:
            raise InvalidSignature("create: Expected key value")

        key, value = args[0], args[1]

        # Store state (memento pattern)
        self.state[KEY] = key
        self.state[VALUE] = value

        self.receiver.create(key, value)

    def undo(self):
        """Delete created data"""
        key = self.state[KEY]
        self.receiver.delete(key)

    def redo(self):
        key, value = (self.state[KEY],
                      self.state[VALUE])
        self.receiver.create(key, value)


class DeleteCommand(AbstractCommand):
    """Delete a value from DATASTORE

    Args:
        key: Identifier for value

    Pre-condition:
        `key` must already exist

    Example:
        command> delete age

    """

    def do(self, *args):
        super(DeleteCommand, self).do(*args)

        if not len(args) == 1:
            raise InvalidSignature("delete: Expected key")

        key = args[0]

        value = self.receiver.delete(key)

        # Save state
        self.state[KEY] = key
        self.state[VALUE] = value

    def undo(self):
        """Re-create deleted data"""
        key, value = (self.state[KEY],
                      self.state[VALUE])
        self.receiver.create(key, value)

    def redo(self):
        key = self.state[KEY]
        self.receiver.delete(key)


class UpdateCommand(AbstractCommand):
    """Update existing value in DATASTORE

    Args:
        key: Identifier for value
        value: Value for identifier

    Pre-condition:
        `key` must already exist

    Example:
        command> update age 5

    """

    def do(self, *args):
        super(UpdateCommand, self).do(*args)

        if not len(args) == 2:
            raise InvalidSignature("update: Expected key, value")

        key, value = args
        previous_value = self.receiver.update(key, value)

        self.state[KEY] = key
        self.state[VALUE] = value
        self.state['previous_value'] = previous_value

    def undo(self):
        """Restore data to previous value"""
        key, value = (self.state[KEY],
                      self.state['previous_value'])
        self.receiver.update(key, value)

    def redo(self):
        key, value = (self.state[KEY],
                      self.state[VALUE])
        self.receiver.update(key, value)


class DataCommand(AbstractCommand):
    """Visualise data in datastore

    Example:
        command> data

    Blocking:
        This command blocks until finished.

        Questions:
            1. If blocking was False, consider the following scenario:
                > create age 5
                > update age 6
                # Now, before the server has completed the
                # requests, we ask it for data:
                > data
                ?

            A) Should it say "No data", even though we just
            created data and would expect it to exist? This might
            not be what the user expects.

            B) Should we "fake" data; i.e. pretend that everything
            went well with the command on the server, even though
            the server may return later with "sorry, can't do it".

            Ba) In the case of erroring out, should we "unfake" it
            client-side; i.e. remove the "faked" value. In this case,
            for the user to know about removal of faked data, he would
            have to check again. But when? 2 seconds later? 5? When
            is the user guaranteed to be given a correct view of the
            data on the server?

    """

    blocking = True

    def do(self, *args):
        super(DataCommand, self).do(*args)

        if args:
            raise InvalidSignature("data: data does not take any arguments")

        if not self.receiver.DATASTORE:
            log.info("No data")
            return

        message = ''
        for key, value in self.receiver.dump().iteritems():
            message += '    %s=%s\n' % (key, value)
        return message


class UndoCommand(AbstractCommand):
    """Undo last command

    Args:
        id: optional UUID for command to undo

    Example:
        command> undo
        command> undo 4354524-54fsr4f4-sdf234rf-2f2f4ff

    Blocking:
        This command will block until finished.

        Questions:
            1. Which one is undone?

            If undo is asynchronous, consider the following scenario:
                > create age 5
                > creage length 1.65
                > undo

            age is written before length. If length isn't completed
            before undo is called, then from the server's perspective,
            age should be undone; not length.

            However, this might not be what the user expects.

            Blocking is there to keep client and server in sync, but does
            cause a performance bottle-neck. How can this be solved otherwise?

            2. Multiple undo

            If undo is asynchronous, consider the following scenario:
                > create age 5
                > creage length 1.65
                # Wait until they are finsihed..
                > undo
                > undo

            Here, undo is called. Before the first undo has completed,
            a second undo is called. What command is the second undo
            undoing if the first undo fails?

    """

    blocking = True

    def do(self, command_id=None):
        if not command_id:
            try:
                command_id = self.receiver.HISTORY[-1]
            except IndexError:
                log.warning("Nothing to undo.")
                return

        self.receiver.execute('_undo', command_id)


class RedoCommand(AbstractCommand):

    blocking = True

    def do(self, command_id=None):
        if not command_id:
            try:
                command_id = self.receiver.FUTURE[-1]
            except IndexError:
                log.warning("Nothing to redo.")
                return

        self.receiver.execute('_redo', command_id)


class HistoryCommand(AbstractCommand):
    """Visualise history (client)

    Example:
        command> history

    """

    def do(self):
        super(HistoryCommand, self).do()
        self.receiver.history()


class FutureCommand(AbstractCommand):
    """Visualise future (client)

    Example:
        command> future

    """

    def do(self):
        super(FutureCommand, self).do()
        self.receiver.future()


class ClsCommand(AbstractCommand):
    """Clear shell (client)

    Example:
        command> cls

    """

    def do(self):
        self.receiver.cls()


class ExitCommand(AbstractCommand):
    """Exit shell (client)

    Example:
        command> exit

    """

    def do(self):
        self.receiver.exit()


class CommandsCommand(AbstractCommand):
    def do(self):
        self.receiver.display_commands()


class HelpCommand(AbstractCommand):
    """Display help (client)

    Example:
        command> help
        command> help create
        command> help update

    Blocking:
        > help create

        This action is assumed to be synchronous; a user looking
        for help on an action usually means he won't perform it
        prior to getting it.

    """

    blocking = True

    def do(self, cmd=None):
        super(HelpCommand, self).do(cmd)
        return self.receiver.help(cmd)


class BlockingCommand(AbstractCommand):
    """Override blocking

    Debugging command to disable blocking on all commands.

    """

    blocking = True

    def do(self, state=None):
        super(BlockingCommand, self).do(state)
        if state:
            self.receiver.blocking = True if state == 'True' else False
        else:
            return self.receiver.blocking


server_commands = {}
for cmd in (CreateCommand,
            DeleteCommand,
            UpdateCommand,
            NetworkCommand,
            DataCommand,
            BlockingCommand,
            HelpCommand):
    server_commands[name(cmd)] = cmd


if __name__ == '__main__':
    receiver = Datastore()
    cmd = CreateCommand(receiver)
    cmd.do('test', 5)
    print receiver.DATASTORE
