# Modification Sequence and Checkpoints

| stage | ordered modification scope | checkpoint / rollback boundary |
|---|---|---|
| M0 | add OFF-by-default fields to `l2cache.h/.cc`; read existing preview and B0 sample state; extend parser/schema documentation | build + directed collector field test; OFF exact equivalence on selected representative smoke; revert one telemetry-only commit |
| M1 | refactor `ep_l2_payload_store` in `gpu-cache.h`; change `l2_cache::access/fill` and fill-request accessor; add static policy plus all-OFF orthogonal feature-vector parsing/validation in `gpu-sim.cc`/config; update directed payload tests | compile + old mode test + static payload store tests + stale fill/rollback/replacement/bank tests + natural smoke exact equivalence; omitted feature fields must remain OFF; revert isolated substrate commit |
| M2 | add explicit pending/bypass consumer/owner contract, sidecar binding and shared-reserve policy; gate it with `unified_payload` feature bit and fail-closed combination validation; add M2 fields and tests | directed exhaust/reserve/forward-progress suite, FEATURE OFF static-mode replay, FEATURE ON correctness suite, then a small M0-selected workload smoke; independently disable shared policy to return to M1 |
| M3 | only after RO eligibility evidence; add a distinct pending object or MSHR abstraction with all state mapped in M3 source map | read/write/atomic/sector/response ordered tests and ablation bit; rollback to M2 |
| M4 | only after TVD opportunity evidence; extend WAD record and transfer a budgeted payload handle | dirty eviction/WAD full/hazard/late completion/storage accounting tests and ablation bit; rollback to M2/M3 composition |

Before formal runs, add deterministic runner overlays, effective-config hashes, collision-free result roots, and manifest feature vectors as specified in `EXPERIMENT_MODE_SWITCH_DESIGN.md`. No stage advances a baseline decision, changes fixed capacities, or executes a mechanism performance campaign. Each functional stage needs its own handoff/acceptance/review pack.
