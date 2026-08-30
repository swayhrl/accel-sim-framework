# EP-L2 Mechanism Implementation Preparation r1

Status: **MECHANISM_IMPLEMENTATION_PREP_REVIEW_READY**
Lane: F — source audit/design only; no functional simulator source was changed and no mechanism experiment was run.

## Review scope and source anchors

| family | framework SHA | core SHA | disposition |
|---|---|---|---|
| Formal C7e | `f08d2ce857972fad73c4e1ab7162ba94c6336507` | `ece1a3a77c5628763e0a4605bfd1c639ee6a1495` | primary audited source |
| D512 candidate | `aae62b66685f15437cecf0193934f628e6fac6ae` | `878f80869ce212e779df20b6421e4dc7f987825d` | comparison only; not a baseline decision |

Inspection worktrees are `/workspace/worktrees/accel-sim-ep-l2-mechanism-prep` on `hrl/ep-l2-mechanism-prep-v0` and `/workspace/worktrees/gpgpu-sim-ep-l2-mechanism-prep` at C7e. The D512 core diff changes only descriptor-histogram cardinality handling in `src/gpgpu-sim/l2cache.cc`; it is observation-only, not a payload/lifecycle semantic change.

## Executive finding

The C7e payload store has 1,024 resident slots plus 128 bypass slots, but its production L2 path allocates and fills **resident** slots only. `reserve_bypass`, `complete_bypass`, and `release_bypass` have no production caller (only directed tests). Thus existing `bypass_*` occupancy is a dormant-model observation, not evidence of an active bypass payload lifetime. M0 must first measure a semantically defined candidate bypass demand; it must not infer role complementarity from 128 permanently-free synthetic slots.

M1 can safely make payload IDs role-independent while preserving the exact static mapping. M2 requires a tag-index-to-payload-ID sidecar and a real bypass/pending consumer contract before it can make a shared-pool performance claim. A fully shared allocator is unsafe as v1 because an unbounded resident role could exhaust slots required by a live bypass/pending transaction. The recommended v1 policy is a shared pool with a **pending-demand-aware protected reserve**, initially fixed to the existing 128 only as a compatibility/safety ceiling; M0 must measure live bypass demand before reducing it. This is a safety default, not performance tuning.

## Pack index

- [SOURCE_MAP.md](SOURCE_MAP.md) — exact implementation map and C7e/D512 comparison.
- [PAYLOAD_LIFECYCLE.md](PAYLOAD_LIFECYCLE.md) — resident, bypass-model, failure and writeback lifecycles.
- [M0_TELEMETRY_DELTA.md](M0_TELEMETRY_DELTA.md) — observation-only producer points and counter contracts.
- [M1_ELASTIC_SUBSTRATE_DESIGN.md](M1_ELASTIC_SUBSTRATE_DESIGN.md) — static-equivalent refactor.
- [M2_UNIFIED_PAYLOAD_V1_DESIGN.md](M2_UNIFIED_PAYLOAD_V1_DESIGN.md) — bounded shared-pool design.
- [M3_RO_PENDING_SOURCE_MAP.md](M3_RO_PENDING_SOURCE_MAP.md) and [M4_TVD_WAD_SOURCE_MAP.md](M4_TVD_WAD_SOURCE_MAP.md) — later dependencies only.
- [MODIFICATION_SEQUENCE.md](MODIFICATION_SEQUENCE.md), [RISK_AND_INVARIANT_MATRIX.md](RISK_AND_INVARIANT_MATRIX.md), and [CHANGED_FILES_EXPECTED.md](CHANGED_FILES_EXPECTED.md) — implementation gates.

## Decision boundary

This pack authorizes neither M0 implementation nor a baseline choice. In particular, D256/D512 are not selected here. The next action is ChatGPT review and baseline-decision integration.
