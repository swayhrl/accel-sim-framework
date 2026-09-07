# C10-A low-resource architecture-model implementation

Goal: `C10A_ARCHITECTURE_MODEL_IMPLEMENTATION_LOW_RESOURCE`
Final state: `C10A_IMPLEMENTATION_PARTIAL_WITH_NAMED_BLOCKERS`

This pack records a deliberately bounded implementation of the C9 architecture
decision. It is not a performance report and it does not authorize C10-B, C5,
any replay, KV Segmentation, 12K work, or M5.

Preserved labels: `REFERENCE_APPROX_SUBENTRY_16`,
`SPECULATIVE_CANDIDATE`.

The source delta implements a versioned V2 registered VA-to-PA descriptor
format, a non-identity-capable ordinary-PTE consistency override, logical
per-L1-cluster immutable replicas, an explicit `HIT_FIRST / MISS_JOIN` owner
path, access-intent plumbing, fair group geometry, leaf invalidation APIs, and
additional bounded telemetry. It does not yet satisfy all lifecycle and
runtime-integration conditions listed in `KNOWN_DEFERRED_C10B.md`; therefore
no C10-A full-PASS claim is made.

The C9 decisions, not Window A results, set all candidate parameters. Window A
was not accessed or changed.
