# Chat

> Messaging systems work basically as instant messaging for applications. - http://aosabook.org/en/zeromq.html

> Instant messaging for Apps - http://jaxenter.com/an-introduction-to-scriptable-sockets-with-zeromq-49167.html

An illustration of a simple human-to-human messaging application, made to explore the possibility of whether or not a similar approach can be taken in the design of computer-to-computer messaging.

### Terminology

A `peer` represents a client, server is called `swarm` and a human-to-human correspondence is called `letter`.

### Requirements

* `REQ01` Peer may recieve letters
* `REQ02` Peer may send letters
* `REQ03` Peer may join late
* `REQ04` Peer may list remote peer's services
* `REQ05` Peer may list swarm services
* `REQ06` Peer may list available peers
* `REQ07` Peer may list all peers
* `REQ08` Peer may signal availability (yes/no)
* `REQ09` Peer may signal inactivity (yes/no)
* `REQ10` There may be multiple peers
* `REQ11` One peer may send letters to exactly one peer
* `REQ12` One peer may send letters to multiple peers
* `REQ13` Peer may initiate conversation

**Send/receive**

Once a `peer` is connected to a `swarm`, route letters to the designated `peer`. This is text-book `REQ/REP`.

**Join late**

Peers not immediately available (late joiners) will receive letters once available. This goes both ways; an active `peer` may send letters to an inactive `peer` and an inactive `peer` may deliver letters sent previously to an active `peer`

This involves:

* Swarm keeps track of letters sent to any particular peer (a queue).
* Each letter contains a `delivered` and `timestap` property.
* Messages that has been `delivered` are removed from queue.

**List `peer` services**

Involves returning upon query a list of available services that a remote computer may perform.

* Send me a funny pic
* Compute n+1

**List swarm services**

Which smilies can I send to my `peer`?

**List available peers**

Return a list of all peers currently connected to the `swarm`. This includes the `swarm` maintaining a record of each connected `peer` and also governs how peers communicate; whether it be centrally (router pattern) or decentrally (freelancer pattern).

**List all peers**

Return list of all peers ever connected to the `swarm`. Involves `swarm` maintaining a persistent record of each connected client.

**Status**

A `peer` may signal that he is either active or inactive. The `swarm` is responsible for determining whether a `peer` is available or not (indirectly, via his response to heartbeats).