# C10-A final report

## Final status

`C10A_IMPLEMENTATION_PARTIAL_WITH_NAMED_BLOCKERS`

Core began its sole functional delta at frozen
`c21137bcb86010215c008292f272aacefac175d3` and is now pushed at
`c27bf0e2fc5e24c54966426840bd56748ef92028` through two coherent checkpoints:
`5191bb5b` and `c27bf0e2`.

Framework began at authoritative
`0df947d4b35f7e916e7396540295bef73bb20c81`. Its C10-A closeout commit records
the final Framework SHA after this pack is committed.

## Delivered implementation boundary

- V2 ASID/epoch-tagged, real PA extent arithmetic replaces formal candidate
  identity PPN mapping; normal PTE completion uses the same registered PPN.
- Eligibility is registration-based rather than `OBJECT_WEIGHT`-based.
- Logical per-cluster N=8 descriptor replicas, lockstep admission and
  bounded port/fallback/order telemetry were added.
- C10 `HIT_FIRST / MISS_JOIN` replaces wait-both source behavior, preserving
  lower-path suppression and no repeated Segment launch on PTW delivery.
- Fair `G=96` and charged `G=32` sub-entry geometry, leaf invalidation and
  static F0--F9/H0 accounting guard were added.

## Why this is not a full pass

Swap-free capacity was only 76 kB. The final code has not been compiled or
run, mandatory lifecycle/atomic-registration semantics remain incomplete, and
F5 is intentionally blocked. All blockers, impacts and C10-B actions are in
`KNOWN_DEFERRED_C10B.md`.

## Boundary compliance

No full build, simulator, C5 replay, workload trace operation, C10-B,
KV Segmentation, 12K, M5, or Window A/B operation occurred. No performance
claim is made. Stop after this commit and push.
