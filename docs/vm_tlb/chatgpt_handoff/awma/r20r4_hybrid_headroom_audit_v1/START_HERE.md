# START HERE — AWMA R20R4 hybrid active-world headroom audit

Date: 2026-10-02

Scientific parent:
`3f4e3409ad629d5302a54e9c3a0f356bdc190456`

Parent decision:
`R20R3_ACTIVE_WORLD_NO_MATERIAL_GAIN`

Accepted parent fact:
the fixed 304-worker online active-world organization is a stable complete-solver negative on the four G1 discovery entries:
- B0 four-entry aggregate ~2.687–2.688 ms
- S1 ~4.476–4.479 ms
- ~66.6% slower

This does not prove every active-world organization is negative.

The fixed candidate source has a structural property:
when active_count > 304, each of 304 workers serially loops over multiple active world IDs. Early solver iterations have active counts near 1024, so this candidate deliberately trades baseline world-level parallelism for worker-loop serialization before substantial shrinkage.

Before any second candidate is considered, quantify whether a structurally gated late-phase organization could even have >=5% complete-solver ideal headroom.

This stage is CPU-only analysis of existing accepted profiler/raw data.

Execution branch:
`hrl/awma-r20r4-hybrid-headroom-audit-109-v1`

No CUDA execution, no new profiler, no S1, no holdout, no 174.
