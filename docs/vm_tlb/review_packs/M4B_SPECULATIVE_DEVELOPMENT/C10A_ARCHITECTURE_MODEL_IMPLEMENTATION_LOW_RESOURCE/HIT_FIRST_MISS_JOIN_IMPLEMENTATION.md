# `HIT_FIRST / MISS_JOIN` implementation

Each accepted candidate request stores independent L1 and Segment completion
state in one `lookup_operation`. Both service intervals begin at the same
accepted L1 admission cycle.

| Observation | Owner/action |
| --- | --- |
| Segment hit first | Segment becomes terminal owner immediately; lower L2/MSHR/PWQ/walker/PWC/PTE and conventional TLB fills are suppressed. |
| L1 hit first | L1 becomes terminal owner immediately; the not-yet-completed Segment result is logically discarded. |
| Segment miss, L1 pending | retain join state; do not launch L2. |
| L1 miss, Segment pending | retain join state; do not launch L2. |
| both miss | account both-miss/join interval, then make exactly one L2 launch. |
| both provide a mapping before ownership | assert PPN equality; mismatch increments fault telemetry before assertion. |

An existing PTW-delivery retry is marked by `completed_outcome` and does not
launch Segment again. The invariant checker was amended so that this legal
delivery lookup is not falsely interpreted as a missing Segment launch.

Focused source cases cover Segment-first and L1-first paths, a store fallback,
and the pre-existing C3 directed test was updated from its obsolete wait-both
expectation. Execution of those post-delta cases is deferred; see the test
matrix and resource log.
