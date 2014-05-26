# Chat

An illustration of a simple human-to-human messaging application, made to explore the possibility of whether or not a similar approach can be taken in the design of computer-to-computer messaging.

### Terminology

A `peer` represents a client and the server is called `swarm`.

### Requirements

* `REQ01` Peer may recieve messages
* `REQ02` Peer may send messages
* `REQ03` Peer may join late
* `REQ04` Peer may list remote peer's services
* `REQ05` Peer may list server services
* `REQ06` Peer may list available peers
* `REQ07` Peer may list all peers
* `REQ08` Peer may signal availability (yes/no)
* `REQ09` Peer may signal inactivity (yes/no)

**Send/receive**

Once a `peer` is connected to a `swarm`, route messages to the designated `peer`. This is text-book `REQ/REP`.

**Join late**

Peers not immediately available (late joiners) will receive messages once available. This goes both ways; an active `peer` may send messages to an inactive `peer` and an inactive `peer` may deliver messages sent previously to an active `peer`

**List `peer` services**

This is more (only) relevant to computer-to-computer messaging, but involves returning upon query a list of available services that a remote computer may perform.

* Compute 1+1
* Block and Sleep

**List server services**

Which smilies can I send to my `peer`?

**List available peers**

Return a list of all peers currently connected to the `swarm`. This includes the `swarm` maintaining a record of each connected `peer` and also governs how peers communicate; whether it be centrally (router pattern) or decentrally (freelancer pattern).

**List all peers**

Return list of all peers ever connected to the `swarm`. Involves `swarm` maintaining a persistent record of each connected client.

**Status**

A `peer` may signal that he is either active or inactive. The `swarm` is responsible for determining whether a `peer` is available or not (indirectly, via his response to heartbeats).