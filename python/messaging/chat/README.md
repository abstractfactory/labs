# Chat

> Messaging systems work basically as instant messaging for applications. - http://aosabook.org/en/zeromq.html

> Instant messaging for Apps - http://jaxenter.com/an-introduction-to-scriptable-sockets-with-zeromq-49167.html

An illustration of a simple human-to-human messaging application, made to explore the possibility of whether or not a similar approach can be taken in the design of computer-to-computer messaging.

### Language

A PEER represents a client, server is called SWARM and a human-to-human correspondence is called LETTER.

### Requirements

* `REQ01` PEER may recieve LETTERS
* `REQ02` PEER may send LETTERS
* `REQ03` PEER may join late
* `REQ04` PEER may list remote peer's services
* `REQ05` PEER may list SWARM services
* `REQ06` PEER may list available PEERS
* `REQ07` PEER may list all PEERS
* `REQ08` PEER may signal availability (yes/no)
* `REQ09` PEER may signal inactivity (yes/no)
* `REQ10` There may be multiple PEERS
* `REQ11` One peer may send LETTERS to exactly one peer
* `REQ12` One peer may send LETTERS to multiple PEERS
* `REQ13` PEER may initiate conversation

**Send/receive**

Once a PEER is connected to a SWARM, route LETTERS to the designated PEER. This is text-book `REQ/REP`.

**Join late**

PEERS not immediately available (late joiners) will receive LETTERS once available. This goes both ways; an active PEER may send LETTERS to an inactive PEER and an inactive PEER may deliver LETTERS sent previously to an active PEER

This involves:

* SWARM keeps track of LETTERS sent to any particular peer (a queue).
* Each letter contains a `delivered` and `timestap` property.
* Messages that has been `delivered` are removed from queue.

**List PEER services**

Involves returning upon query a list of available services that a remote computer may perform.

* Send me a funny pic
* Compute n+1

**List SWARM services**

Which smilies can I send to my PEER?

**List available PEERS**

Return a list of all PEERS currently connected to the SWARM. This includes the SWARM maintaining a record of each connected PEER and also governs how PEERS communicate; whether it be centrally (router pattern) or decentrally (freelancer pattern).

**List all PEERS**

Return list of all PEERS ever connected to the SWARM. Involves SWARM maintaining a persistent record of each connected client.

**Status**

A PEER may signal that he is either active or inactive. The SWARM is responsible for determining whether a PEER is available or not (indirectly, via his response to heartbeats).