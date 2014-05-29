# Chat

> Messaging systems work basically as instant messaging for applications. - http://aosabook.org/en/zeromq.html

> Instant messaging for Apps - http://jaxenter.com/an-introduction-to-scriptable-sockets-with-zeromq-49167.html

An illustration of a simple human-to-human messaging application, made to explore the possibility of whether or not a similar approach can be taken in the design of computer-to-computer messaging in developing Service-oriented architectures.

# Architecture

A `PEER` represents a client, and `SWARM` is the central server. A human-to-human correspondence is called `LETTER` and `SERVICE` is an atomic unit of work provided by either `SWARM` or `PEER`, it may be encapsulated into `TASK`. A `PEER` under the sole control of a computer is referred to as a `WORKER`. The `LOGGER` is a `WORKER` designated for keeping persistent record of all activity on `SWARM`.

`PEERS` communicate using messages via `SWARM`. Each `PEER` is capable of communicating with `SWARM` and other `PEERS`, even `WORKERS`.

* `PEER` - A human/computer connected to `SWARM`
* `SWARM` - Communication bus for all `PEERS`
* `WORKER` - A computer `PEER`
* `SERVICE` - Atomic unit of work
* `TASK` - A `SERVICE` in progress
* `LOGGER` - A record-keeping WORKER

PEER send messages as "fire-and-forget". For any query, results are returned via the same channel as LETTERS.

SWARM receives messages via a pull-mechanism and publishes messages to their respective recipient(s).

A message sent across the wire is called an `ENVELOPE` and has the following layout:

```json
{
    'type': MESSAGE_TYPE,
    'author': AUTHOR,
    'recipients': TARGET_ADDRESSES,
    'payload': RAW_DATA,
    'timestamp': TIME_OF_TRANSMISSION
}
```

Each message transports exactly one (1) `PAYLOAD` which is the main reason for a message to exist; the other being to signal an event.

Possible Payloads are:

- Instant message (str)
- Peers (list)
- Order (list)
- State Query (dict)


### Requirements

* ~~`REQ01`~~ `PEER` may recieve `LETTERS`
* ~~`REQ02`~~ `PEER` may send `LETTERS`
* ~~`REQ03`~~ `PEER` may join late
* ~~`REQ04`~~ `PEER` may list remote peer's `SERVICES`
* ~~REQ05~~ `PEER` may list `SWARM` `SERVICES`
* ~~REQ06~~ `PEER` may list available `PEERS`
* ~~REQ07~~ `PEER` may list all `PEERS`
* `REQ08` `PEER` may signal availability (yes/no)
* `REQ09` `PEER` may signal inactivity (yes/no)
* ~~REQ10~~ There may be multiple `PEERS`
* `REQ11` One peer may send `LETTERS` to exactly one peer
* ~~REQ12~~ One peer may send `LETTERS` to multiple `PEERS`
* ~~REQ13~~ `PEER` may initiate conversation
* ~~REQ14~~ `PEER` may request status of running `SERVICE`
* `REQ15` There may be multiple `PEERS` with similar `SERVICES`
* `REQ16` A `TASK` may be distributed across multiple available `PEERS`
* `REQ17` A `PEER` may list running `TASKS`
* `REQ18` `PEER` may cancel a running `TASK`
* `REQ19` `WORKER` may run multiple `TASKS`
* `REQ20` `WORKER` may limit the amount of concurrent `TASKS`
* `REQ21` `WORKER` may signal statistics
* `REQ22` `LOGGER` maintains a record of all activitiy

### Send/receive

Once a `PEER` is connected to a `SWARM`, route `LETTERS` to the designated `PEER`.

### Join late

`PEERS` not immediately available (late joiners) will receive `LETTERS` once available. This goes both ways; an active `PEER` may send `LETTERS` to an inactive `PEER` and an inactive `PEER` may deliver `LETTERS` sent previously to an active `PEER`

This involves:

* `SWARM` keeps track of `LETTERS` sent to any particular peer (a queue).
* Each letter contains a `delivered` and `timestap` property.
* Messages that has been `delivered` are removed from queue.

### List `PEER` `SERVICES`

Involves returning upon query a list of available `SERVICES` that a remote computer may perform.

* Order coffee
* Publish file
* Compute algorithm

### List `SWARM` `SERVICES`

Which smilies can I send to my `PEER`?

### List available `PEERS`

Return a list of all `PEERS` currently connected to the `SWARM`. This includes the `SWARM` maintaining a record of each connected `PEER` and also governs how `PEERS` communicate; whether it be centrally (router pattern) or decentrally (freelancer pattern).

### List all `PEERS`

Return list of all `PEERS` ever connected to the `SWARM`. Involves `SWARM` maintaining a persistent record of each connected client.

### Status

A `PEER` may signal that he is either active or inactive. The `SWARM` is responsible for determining whether a `PEER` is available or not (indirectly, via his response to heartbeats).

### Multiple `PEERS`

Multiple `PEERS` may exist providing similar services, such as taking orders, publishing files or converting images.

When a `PEER` requests services from one of many `PEERS`, each request will get distributes across all available `PEERS`.

### Signalling availability

A `PEER` may request `SWARM` to provide a list of currently available `WORKERS`. Each `WORKER` then MUST provide the ability to respond to availability-queries.

This is how things may go down:
	1. `PEER` requests a `TASK` to be performed.
	2. `SWARM` receives request.
	3. `SWARM` requests one available `WORKER`
	4. `WORKER` is assigned the `TASK`

The requesting of available workers may go down like this:
	Scenario: 4 `WORKERS` are connected to `SWARM`, 2 of which are busy.
	1. Send availability-query to first `WORKER`
	2. If available; stop
	3. Else send to next `WORKER`, and so forth until found
	4. If none found, queue request and retry later.

In this scenario, the `SWARM` handles queuing of requests until a `WORKER` is available to accept.

### Advanced signalling of availability

In cases where the request is more involved, a query may involve additional parameters:
	- `CORES` required
	- `MEMORY` required
	- `SOFTWARE` required
	- `PRIORITY` of request

To which availability may be returned with additional data:
	- Tasks remaining
	- Estimated time until available

In the case of multiple tasks already being present in `WORKER`, `PRIORITY` will determine in which position the new `TASK` will be placed.

- 1 will put it in front to be executed as soon as the current `TASK` is completed.
- 2 will position it in the center of the queue.
- 3 will append it to the end of the queue.

### Statistics

A `WORKER` may return available CPU and `MEMORY`.