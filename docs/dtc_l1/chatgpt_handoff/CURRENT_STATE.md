# DTC-L1 Current State

Last coordination update: 2026-09-03

Status: **M1-M4 VALIDATED; M5.0A PASS; M5.0B RESUME AUTHORIZED VIA DIRTY-VICTIM POLICY RESOLUTION**

## Validated anchors

M1-M4 remain frozen validated infrastructure:

- Core final: `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0` at `cdeec769fd0c1be12b45d58536ecb81074d4b415`.
- Framework final: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0` at `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`.

Active M5 branches:

- Core: `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`.
- Framework: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`.

## Approved M5 authority

Read the M5 documents in this order:

1. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`;
2. `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md` — specific active refinement for M5-T005;
3. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`;
4. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`;
5. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`;
6. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`;
7. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`;
8. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`;
9. M1-M4 final review packs/specs as regression context.

The dirty-victim resolution is researcher-approved and supersedes the previous researcher-decision stop only for this conventional-L1 policy issue.

## M5 research objective

M5 remains a **mechanism/trend reproduction**, not numerical fitting to thesis speedups.

Causal target:

`Base structural limits -> constrained live misses -> DTC removes limits -> concurrency/latency hiding changes -> performance effect`.

Weak or negative performance must be diagnosed as implementation/modeling, workload/input fidelity, downstream/platform, traffic side effect, compute-bound behavior, or genuine mechanism limitation. Do not tune inputs or architecture to thesis numbers.

## Researcher-frozen M5 v1 interpretations

### Figure 4.5

- PAPER_BASE: conventional 16 KiB L1, 128B, 4-way, PIB=8, MSHR=32.
- PAPER_IO: 16 KiB logical Tag capacity + 80 KiB physical Cacheline Array, PIB=256.
- PAPER_OO: 16 KiB logical Tag capacity + 80 KiB physical Cacheline Array, PIB=128.

### Figure 4.7

Live miss lifecycle is new-miss lower-request commit through final lower response. Primary metric is per-SM cycle average.

### Figure 4.2

Paper-facing structural categories are PIB full, true Tag+Cacheline allocation failure, MSHR capacity/merge failure, and Miss Queue/lower-capacity failure. Tag-bank arbitration remains diagnostic.

### Conventional-L1 dirty-victim policy — new approved refinement

For all paper-facing M5 formal configurations, explicitly use:

`-gpgpu_l1_cache_write_ratio 0`.

Keep the existing write-through/cache-allocation/replacement semantics otherwise unchanged. Ratio 25 is an inherited SM7 diagnostic platform policy, not the paper-facing formal policy.

## M5.0A

M5.0A anchor/reproducibility lock is closed PASS according to Codex evidence. Do not redo it except for the ratio-0 config/sentinel refresh explicitly required by the dirty-victim resolution.

## Current stage — M5.0B workload recovery

M5.0B reached M5-T005 on canonical Parboil JDS SpMV at the corrected 16 KiB geometry. LEGACY and PAPER_BASE both reproduced a source-level deadlock when all four ways of a set became MODIFIED before the inherited global dirty threshold of 25% allowed a dirty victim.

The researcher decision is now resolved by:

`docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`.

Immediate ordered work:

1. preserve ratio-25 evidence and in-flight diagnostics;
2. update the formal config family to explicit ratio 0 only, without unrelated knob changes;
3. add/execute a directed dirty-set replacement regression;
4. rerun canonical SpMV LEGACY and PAPER_BASE under corrected 16 KiB ratio-0 configs and require correctness/forward progress;
5. refresh config identities and required sentinels;
6. close M5-T005;
7. resume the remaining M5.0B workload recovery without redoing valid provenance work.

Already-running 16/32/128 KiB ratio-25 jobs need not be interrupted solely because of this decision. Their results remain diagnostic and cannot replace ratio-0 formal runs.

## Continuous progression after M5-T005 closes

Resume automatically:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`.

Terminal compute state remains:

`M5_COMPUTE_READY_FOR_REVIEW`.

Use the handoff contract at each passing substage. Do not pause for ordinary resolvable workload/build/assertion/timeout/performance issues; execute the M5 issue loop and continue.

## Parallel graphics

Graphics G0-G2 preparation remains nonblocking and may continue when resources allow. It must not contaminate the compute formal behavior/config identity. `GM-ALL-PAPER` remains forbidden until all five graphics workloads are source-backed and correctness-clean.

## Scope boundary

M5 v1 authorizes the ten-compute mechanism study through M5.6 plus graphics preparation G0-G2. It does not authorize M5.7+ supplemental studies, post-review graphics aggregation, Figure 4.6 area claims, or sector-extension paper comparisons before compute review.