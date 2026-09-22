# READY ownership liveness repair

First candidate T0 10/80 failed with RC 134 and deadlock after the last writeback at cycle 5,439.

Root cause: the prelaunch call used the normal `translate()` API and consumed a READY lookup while discarding its PA/outcome. The later accessq head therefore could not consume that completion.

Repair: add default-preserving `consume_ready=true` to `translate()`. Candidate prelaunch passes `false`; READY is observed but retained. The existing accessq-head path is still the sole completion consumer.

Frozen contracts preserved: per-access translation before admission, L1 latency/port semantics, downstream order, MSHR/PWQ/walker/PWC/PTE semantics, completion probing, store/atomic exactly-once, Segment dormancy and legacy behavior.

Patch SHA256: `0a31011fbb955f2751019c577dd6ff37071755c080c47cfc231bbbdc7b3f5563`.

