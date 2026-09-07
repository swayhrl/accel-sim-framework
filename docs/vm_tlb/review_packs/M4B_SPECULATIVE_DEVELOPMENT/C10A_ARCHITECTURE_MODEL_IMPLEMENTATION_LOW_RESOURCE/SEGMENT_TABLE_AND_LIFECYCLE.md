# Segment table, throughput, and lifecycle boundary

The C10-A model represents the C9 nominal local topology by copying one
immutable, capacity-capped V2 descriptor image into each existing L1/SID
translation cluster. The canonical copy is retained only to ensure that a
normal PTE completion sees the same PPN. A profile that asks for 35 clusters
therefore needs `num_sms=35`; F7/F8 charge `35 * 8 * 135 = 37,800` descriptor
bits in their manifest contract.

The model's one-accept contract is lockstep with the existing one-port local
L1 admission: a candidate request reaches a Segment attempt at that admission;
an L1-port denial produces no Segment acceptance and increments the Segment
denial counter. There is no hidden software queue in the candidate model.

Implemented immutable-epoch fields are ASID and 16-bit epoch in every V2
descriptor. They protect load-time matching, and the map is immutable for a
controller lifetime.

Not implemented: privileged install acknowledgements across replicas, revoke
acknowledgements, runtime epoch/generation advancement and wrap quiescence,
descriptor removal before remap/free, context-switch injection, and a
stale-fill discard race. Existing install telemetry reports construction-time
attempt/ack only; it is not falsely presented as a complete lifecycle model.
Those omissions block replay authorization.
