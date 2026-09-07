# B7 — conventional translation generation and stale fill discard

Segment registration epoch and normal translation invalidation are separate
domains:

| Domain | Owner | Meaning |
| --- | --- | --- |
| Segment epoch | privileged registration lifecycle | immutable descriptor-image version for a pinned inference epoch |
| ASID translation generation | normal page translation/shootdown | version of resident/in-flight L1/L2/PTW translation work |

At first request admission the controller materializes the ASID generation
(initially 1). `lookup_operation` captures it; an L2 miss copies it into its
MSHR; a completed PTW outcome carries it too. `invalidate_translation()` and
`flush_translation_asid()` advance that ASID before invalidating L1 and exact
or sub-entry L2 residency. A global flush advances every materialized ASID,
so a request admitted at the implicit initial value cannot escape a later
global shootdown.

Before a lookup proceeds, before a completed outcome is handed back, and
before `complete_translation()` fills L1/exact/sub-entry state, captured and
current generations are compared. A mismatch removes the obsolete lookup or
MSHR/PWQ state, increments a stale-discard counter, and does not call either
fill path. This binds the transaction itself rather than checking only the
current ASID or current sub-entry group at fill time.

For the active Segment ASID, a normal shootdown also initiates descriptor
revoke; it does not increment or reuse the Segment epoch. C10-B must execute
the exact and sub-entry race cases and inspect stale-fill telemetry.
