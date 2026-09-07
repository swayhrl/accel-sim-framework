# C10-A2 final report

## Final status

`C10A2_STATIC_BLOCKERS_CLOSED_COMPILE_AND_RUNTIME_DEFERRED`

This is the sole C10-A2 status. It means B2--B7 have a coherent source and
static-validation closure, not that they have compiled, linked, executed or
produced a performance result.

## Delivered

- V2 Segment semantic rejection is transactional, machine-readable and
  conventional-fallback-safe; valid descriptor PA arithmetic remains
  non-identity capable.
- Local Segment state has explicit per-replica install/revoke acknowledgements,
  active ASID/epoch, one-ASID v1 behavior and wrap/quiesce rule.
- The only production translation call derives explicit access class from the
  authoritative instruction; Segment remains read-only and object-map labels
  remain telemetry-only.
- The official fair-arm runtime selector realizes F0--F4/F6--F9, exposes
  geometry/charged state, rejects F5 and permanently rejects H0.
- Conventional ASID generation binds lookups/MSHR/fills and discards stale
  work before exact or sub-entry state can be resurrected.

## Evidence boundary

Framework was admitted at `d112714291ff789194ab335940f76243920b4404`; Core at
`c27bf0e2fc5e24c54966426840bd56748ef92028`; the Core output checkpoint is
`12267bb7ed1dc0257d1d903f6baf7cbdc6ca550e`. The only executed validation was
the no-build Python static validator and whitespace checks recorded in
`STATIC_VALIDATION.md`. There was no build, link, simulator, C5 replay,
trace generation/scan, synthesis/PPA, or Window A/B operation.

## Deferred and stop point

`REMAINING_C10B_BLOCKERS.md` retains B1, B8/F5, B9 and all runtime validation.
No C10-B, C5, KV segmentation, 12K or M5 action is started here. The retained
candidate labels are `REFERENCE_APPROX_SUBENTRY_16` and
`SPECULATIVE_CANDIDATE`.
