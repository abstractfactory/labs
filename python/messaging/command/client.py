"""
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


There are two categories of commands; divided into two additional
categories: Synchronous, Asynchronous and Client, Server.

Asynchronous/synchronous:
    Some commands are performed asynchronously on the server,
    letting clients continue to perform unimpeeded:

        > create age 5
        > create length 0.56

    Other commands make better sense when synchronous:

        > data
            age=5
            length=0.56

    Other commands remain asynchronous, yet behave synchronously:

        > create width 1.5
        > history
            0: create (...)
        > data
            width=1.5

    Here, history isn't available until the command has been
    successfully executed on the server; the same is true for data.

Client/server
    Some commands operate only on the server:

        # Update server data
        > update age 6

    Other commands operate only on the client:

        # Clear client shell
        > cls

    Other commands operate on both:

        # Display available data on server
        > data

Blocking commands:
    In the case of slow responses, there may be situations where
    the client and server go out of sync, causing unexpected
    behaviour.

        # Request data creation on server
        > create age 5

        # Before server has had a chance to complete
        # the request, have a look at history:
        > history
            No history

        # As we can see, the command hasn't finished executing yet.
        # Running undo at this point would not undo anything:
        > undo

        # Worse yet, if there was existing history prior to our command,
        # we would be undoing a different command.
        > create age 5
        > history
            0: update

        > undo
        # Undoing "update"

    To keep client and server in sync with requests, critical
    commands are blocking; i.e. synchronous.

     _      _                _      _
    |        |              |        |
    |  cmd1  | -----------> |        |
    |  wait  |              |        |
    |        | <----------- |  resp  |
    |  cmd2  | -----------> |        |
    |  wait  |              |        |
    |        | <----------- |  resp  |
    |_      _|              |_      _|

      client                  server

Multiple clients:
    There are two flavours of having multiple clients connect to an
    application.

    1. Multiple views
        Either they provide multiple views onto the same set of data,
        in which case they may both be in use by the same user which
        means that commands from both clients would add to the same
        pool of history.

    2. Multiple users
        Alternatively, multiple users operate on the same set of data
        in which case history is kept separate.

    Ultimately, undo/redo is a per-user concept; not per-client. In
    this implementation however, each client maintains its own history,
    regardless of the amount of users.

Messages:
    These are all types of messages transferred.

    --> Register - Advertise client to server
    --> Command - Delegated asynchronous action
    <-- Result - Return value of command
    <-- Confirmation - Status of request

Questions:
    1. Asynchronous create/update/delete

    Creating new data is a non-blocking operation. Once the command
    has been executed, it is stored in history and available for
    undo.

    On a slow network, it may take a substantial amount of time for
    the command to finish. If the user requests to undo, before the
    command has finished executing, what is expected to happen?

        # Create a large value, takes several seconds to finish
        > create age large_value
        # And immediately after call undo
        > undo
        # What happens here?

"""

from __future__ import absolute_import

import zmq
import json
import uuid
import time
import logging
import threading

# DES06 (see command.py)
import command

log = command.setup_log('client')
log.setLevel(logging.INFO)

# Each running client will have a unique ID
# The server uses this ID to separate between commands
# being executed and allows multiple clients to undo/redo
# their own individual commands.
UUID = str(uuid.uuid4())

context = zmq.Context()


class Invoker(object):
    """Invoker ("waiter")

    Transmit command to server for execution and await results.

    - Transmission is blocking
    - Awaiting results is non-blocking

    Another way of saying it is:
        Requests are synchronous, execution is asynchronous.

    Client vs. server history:
        The server keeps a record of each command executed on the client.
        The client then keeps a record of the ID for each command. The
        ID is sent back to the server when requesting a undo operation.

        The alternative is to store history and a delta on the client,
        which would expose internals of the server to the client and
        thus breach encapsulation.

        This way, the server is the only one aware of `how` things are
        done, the client merely stores `what` were done, so as to be
        able to signal an undo/redo operation back to the server.

    Client vs. server queue:
        In this implementation, the client sends one message at a time.

        An alternative to this design is for the server to execute only
        one command at a time.

        In the latter design, the server must be informed of the requesting
        client prior to executing said command, so as to know where to return
        the results. This means a tighter coupling of server to client and
        more complexity in terms of code.

        The benefit/disadvantage of the former design is that if a client
        disconnects during a series of pending commands, pending commands
        are not sent and may thus be considered canceled.

        Whether this is good or bad depends on your requirements.

    Difference:
        In the Command Pattern definition (*) the invoker instantiates
        concrete command objects, however this implementation does not.

        Doing so would mean giving clients access to implementation details
        of the receiver - involving the dependencies of both the concrete
        command and also the receiver.

            # From within client
            >>> invoker.create('age', '5')

        Client instantiates CreateCommand, with arguments,
        marshalls it and send it across; discarding the concrete
        object.

        From here, the receiver then re-instantiates CreateCommand,
        using the same arguments, and run it. Resulting in instantiation
        in two places, as opposed to one.

        The immediate benefit is that clients aren't given the
        additional dependency of which concrete commands are
        available. Meaning it can send strings over to the server
        and the server would determine whether or not the command
        exists and if it does instantiate it.

        The disadvantage is that clients aren't able to perform
        any operations on the objects themselves; but I have yet
        to find any need for this, as commands are simplistic in
        nature; only offering `do`, `undo` and `redo` methods.

        * http://www.oodesign.com/command-pattern.html
    """

    HISTORY = list()
    FUTURE = list()

    def __init__(self, ip='localhost', port='5555'):
        self.client_commands = {}
        for cmd in (command.UndoCommand,
                    command.RedoCommand,
                    command.HistoryCommand,
                    command.FutureCommand,
                    command.CommandsCommand,
                    command.ClsCommand,
                    command.ExitCommand):
            self.client_commands[command.name(cmd)] = cmd

        # Outgoing channel
        self.requests = context.socket(zmq.REQ)
        self.requests_ip = ip
        self.requests_port = port

        # Incoming channel
        self.results = context.socket(zmq.REP)
        self.results_port = None

        # Commands run upon launch
        self.init_commands = []

        self.connect()
        self.listen()
        self.init_shell()

    def connect(self):
        """Connect to server

        This method is responsible for keeping the server unaware
        of where a client is at, until a client attempts to connect.

        It works by first establishing a connection to a fixed point;
        the server. It then emits a message, containing a unique id
        for this particular client, along with a unique port under which
        the client will be listening for responses.

        The server will then only send messages to clients that were
        originally responsible for making the request.

        Example:
            # Client 1
            > create age 5
            > history
                0: (client1_specific_id)

            # Client 2
            > create color 5
            > history
                0: (client2_specific_id)

        """

        # Connect to stable server port
        endpoint = "tcp://{ip}:{port}".format(
            ip=self.requests_ip,
            port=self.requests_port)

        log.info("Connecting to %s.." % endpoint)
        self.requests.connect(endpoint)

        # Bind random incoming port
        try:
            results_port = self.results.bind_to_random_port("tcp://*")
        except zmq.error.ZMQError:
            raise command.Connection("Could not connect to "
                                     "random port, try again later.")

        if self.requests_ip == 'localhost':
            # The server is running locally, this means the
            # client must be running locally too.
            results_ip = 'localhost'

        elif self.requests_ip.startswith('192'):
            # The server is running somewhere within the local network.
            # Local connections don't need portmapping. The following
            # snippet will retrieve the local ip address.
            # For example: 192.168.1.3
            results_ip = command.get_local_ip()

            # Assume user is interested in actual network performance
            # and not a simulated environment.
            self.init_commands.append(['network', 'real'])

        else:
            # If the server is running across the internets,
            # advertise the public IP of the client so that the
            # server can send messages back across the internets.
            # The following snippet will retrieve the public ip address.
            # For example: 10.3.64.102
            #
            # Keep in mind that for a remote client to receive messages
            # from a server, the client must first forward the port
            # at which the server will broadcast messages.
            # E.g. I am in Sweden, and you are in America. My IP is
            # s.wed.e.n and your's is a.mer.ic.a. I am listening at port
            # 1000 and you are sending messages to 1000. But for 1000 to
            # reach me when coming in from the internet, my router must
            # first forward any requests for port 1000 to my computer on
            # local network; e.g. 192.168.1.3:1000
            results_ip = command.get_public_ip()

            # See above
            self.init_commands.append(['network', 'real'])

        # Advertise existence of client to server.
        msg = {
            command.COMMAND: '_connect',
            command.ARGS: (UUID,
                           results_ip,
                           results_port),
            command.ID: UUID
        }

        self.requests.send_json(msg)
        reply = self.requests.recv_json()
        log.info("Connected")

        if reply[command.STATUS] != command.OK:
            print reply[command.INFO]

        self.results_port = results_port

    def init_shell(self):
        header = """
     ______________________________________________________
    |                                                      |
    | Command Pattern - Client                             |
    |            __________         . . . . . . .          |
    |           |          | -----> .           .          |
    |           |          | <----- .           .          |
    |           |__________|        . . . . . . .          |
    |                                                      |
    | Author: Marcus Ottosson <marcus@abstractfactory.io>  |
    |______________________________________________________|

* Available commands"""

        msg = {
            command.COMMAND: '_available_commands',
            command.ARGS: [],
            command.ID: UUID,
        }

        packed_msg = json.dumps(msg)
        self.requests.send(packed_msg)

        raw_msg = self.requests.recv()
        msg = json.loads(raw_msg)

        available_commands = msg[command.INFO]

        all_commands = available_commands + self.client_commands.keys()

        message = header
        for cmd in sorted(all_commands):
            message += "\n    %s" % cmd
        message += '\n'
        print message

        for cmd in self.init_commands:
            self.execute(*cmd)

    def listen(self):
        """
        Once a command has been executed, this is
        where its return values are recieved.

        """

        def result_from_commands():
            while True:
                msg = self.results.recv_json()

                # -- Block here

                status = msg[command.STATUS]

                # Status: OK
                #  __________
                # |          |
                # |    OK    |
                # |__________|

                if status == command.OK:
                    self.post_command(msg)

                # Status: FAIL
                #  __________
                # |          |
                # |   FAIL   |
                # |__________|

                elif status == command.FAIL:
                    time.sleep(0.1)
                    print "\nE: %s" % msg[command.INFO]
                    command.init_shell()

                # Status: ERROR
                #  ___________
                # |           |
                # |   ERROR   |
                # |___________|

                else:
                    print "This should not happen"

                # Prepare output message
                msg = {
                    command.STATUS: command.OK,
                    command.INFO: None
                }

                self.results.send_json(msg)

        thread = threading.Thread(target=result_from_commands)
        thread.daemon = True
        thread.start()

    def execute(self, cmd, *args):
        if cmd in self.client_commands:
            # Client-side command
            #  _________________
            # |                 |
            # |   CLIENT-SIDE   |
            # |_________________|

            cmd_obj = self.client_commands[cmd](self)
            return cmd_obj.do(*args)

        else:
            # Server-side command
            #  _________________
            # |                 |
            # |   SERVER-SIDE   |
            # |_________________|

            msg = {
                command.COMMAND: cmd,
                command.ARGS: args,
                command.ID: UUID,  # Distinguish client
            }

            self.requests.send_json(msg)

            # Synchronous, await confirmation that
            # command has been recieved.
            msg = self.requests.recv_json()

            message = msg.get(command.INFO)
            if message is not None:
                print message

            return msg

    def post_command(self, message):
        """The command has been transmitted and executed successfully

        Note:
            Undo and redo commands aren't processed on the client until
            the server has confirmed their successful execution.

            This is the main reason why Undo is blocking by default.

        """

        # A command was undone, remove from history.
        #  __________
        # |          |
        # |   Undo   |
        # |__________|

        if command.UNDO in message:
            undo_id = message[command.UNDO]

            try:
                self.HISTORY.remove(undo_id)
            except ValueError:
                print ("This isn't supposed to happen "
                       "(undo_id=%s)" % undo_id)
                command.init_shell()

            self.FUTURE.append(undo_id)

        # A command was redone, remove from future.
        #  __________
        # |          |
        # |   Redo   |
        # |__________|

        elif command.REDO in message:
            redo_id = message[command.REDO]

            try:
                self.FUTURE.remove(redo_id)
            except ValueError:
                print ("This isn't supposed to happen "
                       "(undo_id=%s)" % undo_id)
                command.init_shell()

            self.HISTORY.append(redo_id)

        # A command was executed, store it in history.
        #  ___________
        # |           |
        # |   Store   |
        # |___________|

        elif command.ID in message:
            command_id = message[command.ID]

            # Clear redo queue
            while self.FUTURE:
                self.FUTURE.pop()

            self.HISTORY.append(command_id)

        if command.INFO in message:
            reply = message[command.INFO]
            if reply is not None:
                if message.get(command.BLOCKING):
                    print reply
                else:
                    # If messages are returned asynchronously,
                    # make sure to notify user that there is
                    # a message coming in.
                    print "- incoming message -"
                    print reply
                    command.init_shell()

    def history(self):
        if not self.HISTORY:
            print "No history available"
        else:
            for i in xrange(len(self.HISTORY)):
                command_id = self.HISTORY[i]
                print "    %i: (%s)" % (i, command_id)

    def future(self):
        if not self.FUTURE:
            print "No future available"
        else:
            for i in xrange(len(self.FUTURE)):
                command_id = self.FUTURE[i]
                print "    %i: (%s)" % (i, command_id)

    def cls(self):
        command.cls()

    def exit(self):
        raise KeyboardInterrupt


if __name__ == '__main__':
    """Client ('customer')"""
    import sys
    command.cls()

    try:
        invoker = Invoker(*sys.argv[1:])

    except command.Connection as e:
        print e

    else:
        try:
            while True:
                command.init_shell()
                input_ = raw_input()

                parts = input_.split()
                cmd, args = parts[0], parts[1:]

                invoker.execute(cmd, *args)

        except KeyboardInterrupt:
            print "\nGood bye"
