# R20R5 authorization

Date: 2026-10-02

Parent R20R4 authority:
- execution branch: `hrl/awma-r20r4-hybrid-headroom-audit-109-v1`
- commit: `769ea5f3592976b2035beb76947b0d934d6efabf`
- tree: `ac38c4c91cb0dfd65ef7c27803b44bc85d4ad14f`
- decision: `R20R4_HYBRID_CANDIDATE_JUSTIFIED_FOR_REVIEW`

Accepted headroom:
- active_count<=304 late region = 412.097 us / 1024.802 us selected-stage time = 40.21%
- O1 ideal complete-solver headroom = 15.33%
- O2 targeted H+blocked-Cholesky ideal complete-solver headroom = 11.77%
- all four entries have positive O2
- O2 numerator not dominated by one entry
- O3 remains unknown
- previous always-worklist 304-worker S1 remains ~66.6% slower and is not reinterpreted

Authorized final R20 active-world runtime candidate:
- handoff branch: `hrl/awma-r20r5-hybrid-native-handoff-v1`
- handoff HEAD: `e523466fc897f17f3309bff4ad02017d09ccb618`
- execution branch: `hrl/awma-r20r5-hybrid-native-109-v1`
- Goal:
  `docs/vm_tlb/chatgpt_handoff/awma/r20r5_hybrid_native_v1/LANE_F_R20R5_HYBRID_ACTIVE_WORLD_NATIVE_109_GOAL.md`

The hybrid is fixed:
- current nsolving >304 -> original baseline selected-stage organization, no active-list build
- current nsolving <=304 -> build ascending active IDs and use the already-accepted fixed 304-worker H/blocked-Cholesky mapping
- threshold exactly 304
- no threshold/worker/stage/queue sweep

A nested device-side conditional canary is required before the scientific candidate.

If the hybrid is not cleanly implementable, numerically invalid, <5% material at discovery, mixed, or nonreproduced at holdout, the R20 active-world line closes. No rescue candidate follows.

If discovery and sealed holdout both reproduce >=5% complete-solver response, stop for review as `R20R5_HYBRID_SOLVER_RESPONSE_REPRODUCED`.

No hardware/node174/Accel-Sim is automatically authorized.
