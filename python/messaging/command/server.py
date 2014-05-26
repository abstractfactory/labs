"""

Architecture:

          client                             server
        __________                         __________
    1. |          | --- run command ----> |          |
       |          | <------- ok --------- |          |
       |__________|                       |__________|

    Client sends a request for execution of `command`.
    The server immediately (synchronously) responds with
    confirmation that the request has been recieved.

    2. Control is returned to client and server awaits
    further instructions.
        __________                         __________
    3. |          | <----- results ------ |          |
       |          | ------ thanks  -----> |          |
       |__________|                       |__________|

    Once the command has finished processing, its results
    (if any) are returned to the client, to which the client
    responds "thank you very much!".

Undo/redo:
    Each executed command is stored and processed on the server.
    The client passes along his ID and passed back a unique ID
    per command. The client then stores this ID in his local history
    and sends it back to the server whenever an undo operation is
    requested. The command object is then retreived on the server
    and is undone/redone.

Linear Command Execution:
    Each command given to a server is executed in the order that it
    was given. This is to prevent errors such as creating data and
    then modifying it directly afterwards. If the create operation
    should take longer than the update, there will be conflict.

Memory-leak:
    Because each command is stored on the server, this means that
    the more commands executed by a client, the more memory a server
    will consume.

    An alternative to this design might be to implement a "heartbeat".
    The server can either send or listen for signals at regular intervals
    and when a client stops sending/responding, the associated commands
    could be erased.

"""

from __future__ import absolute_import


import sys
import zmq
import json
import time
import uuid
import Queue as queue
import logging
import traceback
import threading

import command

stdout = sys.stdout

log = command.setup_log('server')

# Default verbosity, overriden via the command 'verbosity'
log.setLevel(logging.INFO)

context = zmq.Context()

# The server will listen on port 5555 for incoming requests
# from clients. It will execute them in a separate thread
# and move onto listening for further commands.
requests = context.socket(zmq.REP)
requests.bind("tcp://*:5555")

# While a command is being processed, the incoming socket
# can continue taking on requests. Once a command is finished,
# a message is sent to the client who initially made the request.
# Each client is stored here, along with each communication channel.
clients = {}

# Object actually performing the commands (the "chef").
datastore = command.Datastore()

# Store executed commands on a per-client basis
# {
#   'client1': {
#       'command1': cmd_obj
#       'command2': cmd_obj
#   },
#   'client2': {
#       'command2': cmd_obj
#   }
# }
#
# Note, this particular implementation doesn't bother with
# multiple clients, which makes this dict uneccessarily complex.
# However, a client connecting multiple times will introduce
# additional containers for commands. A heartbeat could then
# be used to erase commands stored within client containers.
executed_commands = dict()

# Server constants
RESULTS = 'results'  # Result channel
TIME = 'time'  # Command time-stamp  (not used)
OBJ = 'obj'    # Command object


def do(cmd_obj, args, func, blocking, client_id):
    """Asynchronously run `cmd`

    Args:
        cmd_obj (object): Command object to do
        args (list): Arguments passed to command
        func (str): to `do` or `undo`
        client_id (str): Unique identifier for client, for undo/redo

    """

    cmd_name = command.name(cmd_obj.__class__)
    log.info("    executing %r.." % cmd_name)

    # Assume failure of command, until proven otherwise.
    output = {
        command.STATUS: command.FAIL,
        command.INFO: None
    }

    # Interpret command
    #  ___________
    # |           |
    # |    ???    |
    # |___________|

    try:
        if func == 'undo':
            # Signal that this command has now been undone.
            # The client will receive this message and remove
            # it from its local history.
            undo_id = args.pop()
            output[command.UNDO] = undo_id

        if func == 'redo':
            # Signal that this command has now been redone.
            # The client will receive this message and remove
            # it from its local trash.
            redo_id = args.pop()
            output[command.REDO] = redo_id

        # Execute command
        #  ___________
        # |           |
        # |    ...    |
        # |___________|

        retval = getattr(cmd_obj, func)(*args)
        command_id = str(uuid.uuid4())

        output[command.STATUS] = command.OK
        output[command.INFO] = retval
        output[command.COMMAND] = cmd_name
        output[command.BLOCKING] = blocking

        # Only track commands that support undo.
        if hasattr(cmd_obj, 'undo'):
            output[command.ID] = command_id

        # Store and associate client with command, for undo/redo
        if not client_id in executed_commands:
            executed_commands[client_id] = {}

        command_msg = {
            'obj': cmd_obj,
            'time': time.time()
        }

        executed_commands[client_id][command_id] = command_msg

    except (command.Exists,
            command.InvalidSignature,
            command.Full,
            command.Length) as e:
        output[command.INFO] = str(e)

    except Exception as e:
        # In the event of an unexpected exception,
        # notify the user and include traceback server-side.
        output[command.INFO] = str(e)
        print "\n%s" % traceback.format_exc()

    # Transmit results
    #  ___________        ___________
    # |           | ---> |           |
    # |           |      |           |
    # |___________|      |___________|

    try:
        results_channel = clients[client_id][RESULTS]
    except KeyError:
        # The client sending requests isn't connected to this
        # instance of the server. What probably happened was
        # that the client connected, then the server restarted
        # and thus lost track of clients.
        log.error("ERR The client sending requests is "
                  "not registered and must be reconnected.")
        return

    log.info("--> command executed: sending..")

    # Message-type: Result
    results_channel.send_json(output)

    # Await confirmation
    #  ___________        ___________
    # |           | <--- |           |
    # |           |      |           |
    # |___________|      |___________|

    log.info("<-- command executed: receiving confirmation..")
    msg = results_channel.recv()
    log.info("    command executed: confirmation ok")
    log.info("    ready")

    unpacked_msg = json.loads(msg)
    if not unpacked_msg[command.STATUS] == command.OK:
        print unpacked_msg[command.INFO]


def worker():
    """This function is in charge of execution ordering.

    It makes sure that commands are executed in the order that
    they are received; regardless of them being either synchronous
    or asynchronous.

    """

    while True:
        item = command_queue.get(block=True)
        do(*item)
        command_queue.task_done()

command_queue = queue.Queue()
worker_thread = threading.Thread(target=worker)
worker_thread.daemon = True
worker_thread.start()


def server():

    while True:
        request = requests.recv_json()

        # Confirm requests. This is simply so that the caller can
        # rest assured that the server is alive, nothing more.
        output = {
            command.STATUS: command.FAIL,
            command.INFO: None,
        }

        # Request protocol
        #
        # This pattern is known on both ends, prior to any
        # communication taking place.
        cmd_name, args, client_id = (
            request[command.COMMAND],  # Command to be executed
            request[command.ARGS],     # Arguments passed to command
            request[command.ID]        # Unique id per-client.
        )

        log.info("<-- request received: %s" % (cmd_name))

        # Server commands
        #  _____________________
        # |                     |
        # |   Server commands   |
        # |_____________________|
        #
        # These commands are intercepted and NOT sent to the
        # datastore; as they provide information only retrievable
        # from the server. This is to avoid storing any data in
        # the client; the client is "dumb".
        if cmd_name == '_available_commands':
            # Return list of available commands (private)
            available_commands = command.server_commands.keys()
            output[command.INFO] = available_commands
            output[command.STATUS] = command.OK

        elif cmd_name == '_connect':
            # Connect to server (private)
            try:
                client_id, client_ip, client_port = (args[0],
                                                     args[1],
                                                     args[2])
            except ValueError:
                output[command.INFO] = 'not for use in shell'

            if not client_id in clients:
                clients[client_id] = {}

            if not RESULTS in clients[client_id]:
                client_endpoint = "tcp://{ip}:{port}".format(
                    ip=client_ip,
                    port=client_port)

                results_channel = context.socket(zmq.REQ)
                results_channel.connect(client_endpoint)

                clients[client_id][RESULTS] = results_channel
                output[command.STATUS] = command.OK
                log.info("<-- Client connected: %s.." % client_endpoint)
            else:
                # This isn't supposed to ever happen
                output[command.INFO] = 'Client already registered'

        elif cmd_name == 'clients':
            # Return a list of currently connected clients
            output[command.STATUS] = command.OK
            output[command.INFO] = clients.keys()

        # Receiver commands
        #  ____________________
        # |                    |
        # |  Client commands   |
        # |____________________|

        else:
            cmd_obj = None

            if cmd_name == '_undo':
                #  __________
                # |          |
                # |   Undo   |
                # |__________|

                command_id = args[0]
                history = executed_commands[client_id][command_id]
                cmd_obj = history[OBJ]

                # The command object being redone is not UndoCommand
                # and will therefore not adhere to the blocking-state
                # of it. We need to forward this request onto whatever
                # object it is we are undoing.
                #
                # Also note that we are altering the blocking-state
                # on an instance, and not on the class; as only
                # instance are stored in the executed_commands map.
                cmd_obj.blocking = command.UndoCommand.blocking

                func = 'undo'

            elif cmd_name == '_redo':
                #  __________
                # |          |
                # |   Redo   |
                # |__________|

                command_id = args[0]
                history = executed_commands[client_id][command_id]
                cmd_obj = history[OBJ]

                # See above.
                cmd_obj.blocking = command.RedoCommand.blocking

                func = 'redo'

            else:
                try:
                    cmd_obj = command.server_commands[cmd_name](datastore)
                except KeyError:
                    output[command.INFO] = ('Command %r was not found'
                                               % cmd_name)
                func = 'do'

            if cmd_obj:
                # Asynchronously run command. The thread will signal
                # completion via a separate socket; a socket designated to
                # completion transmission.
                blocking = cmd_obj.blocking and datastore.blocking
                command_queue.put([cmd_obj, args, func, blocking, client_id])
                output[command.STATUS] = command.OK

                # Some commands may request to block until finished.
                # See client.py for more information.
                if blocking:
                    log.info("||| blocking..")
                    command_queue.join()
                    log.info("--- unblocking")

        log.info("--> request received: confirming..")
        
        # Message-type: Confirmation
        requests.send_json(output)

        log.info("    request received: confirmation ok")
        log.info("    ready")


def main():
    header = """
     ______________________________________________________
    |                                                      |
    | Command Pattern - Server                             |
    |          . . . . . . .         __________            |
    |          .           . -----> |          |           |
    |          .           . <----- |          |           |
    |          . . . . . . .        |__________|           |
    |                                                      |
    | Author: Marcus Ottosson <marcus@abstractfactory.io>  |
    |______________________________________________________|

Running @ local:  {local}:5555""".format(local=command.get_local_ip())

    command.cls()
    print header

    thread = threading.Thread(target=server)
    thread.daemon = True
    thread.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
