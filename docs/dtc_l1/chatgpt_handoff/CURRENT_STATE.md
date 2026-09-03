# DTC-L1 Current State

Last coordination update: 2026-09-03

Status: **M1-M4 VALIDATED; M5 v1 APPROVED; M5.0A FIDELITY LOCK AUTHORIZED**

## Validated parent anchors

M1-M4 are frozen validated infrastructure for M5.

Core parent:

- repository: `swayhrl/gpgpu-sim`;
- branch: `hrl/decoupled-l1-m1m4-v0`;
- final validated SHA: `cdeec769fd0c1be12b45d58536ecb81074d4b415`.

Framework parent:

- repository: `swayhrl/accel-sim-framework`;
- branch: `hrl/decoupled-l1-exp-m1m4-v0`;
- final validated SHA: `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`.

M0 and M1-M4 validated branches are read-only experimental anchors unless an M5-discovered implementation-fidelity bug requires a separately documented M5 repair on the M5 branch.

## Active M5 branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`.

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`.

Both were created directly from the validated M1-M4 final anchors. M5 implementation/instrumentation/experiments belong on these branches.

## Approved M5 authority

Read in this order:

1. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`;
2. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`;
3. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`;
4. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`;
5. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`;
6. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`;
7. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`;
8. M1-M4 final review packs/specs as regression/source context.

The stale `PLANNING DRAFT` banner inside the long matrix is superseded by `M5_V1_APPROVAL.md`; the matrix body is the approved v1 detailed execution plan.

## M5 research objective

M5 is a **mechanism/trend reproduction**, not a numeric-target recreation of the thesis' +22%/+30% aggregate speedups.

The causal question is:

`Base structural limits -> constrained live misses -> DTC removes limits -> concurrency/latency hiding changes -> performance effect`.

Weak or negative performance is not by itself a failure. It must be classified as implementation/modeling, workload/input fidelity, downstream/platform, traffic side effect, compute-bound behavior, or a genuine mechanism limitation. Do not tune inputs or architecture to thesis numbers.

## Researcher-frozen M5 v1 interpretations

### Figure 4.5 main configuration

Primary DTC result uses:

- 16KB logical Tag/cache capacity;
- 80KB physical Cacheline Array;
- IO PIB=256;
- OO PIB=128;
- remaining frozen M1-M4 paper-mode defaults.

PAPER_BASE remains the conventional 16KB L1 with PIB=8 and MSHR=32.

### Figure 4.7 metric

A live concurrent miss is counted from new-miss lower-request commit through final lower response completion.

Primary plot metric:

`avg_concurrent_misses_per_sm = sum(live misses across all SMs/cycles) / (num_SM * sampled_kernel_cycles)`.

GPU-total cycle average and peaks are retained as audit data.

### Figure 4.2 categories

Formal paper-facing categories are only:

1. PIB/waiting-buffer full;
2. true Tag & Cacheline allocation failure;
3. MSHR capacity/merge failure;
4. Miss Queue/lower-request-capacity failure.

Tag-bank arbitration conflicts are diagnostic and must not be folded into Tag & Cacheline allocation failure.

## Authorized continuous compute progression

`M5.0A Anchor -> M5.0B Workloads -> M5.0C Platform -> M5.0D Metrics -> M5.0E Pilot/Fidelity Lock -> M5.1 Fig4.2 -> M5.2 Fig4.5+4.7 -> M5.3 Fig4.8 -> M5.4 Fig4.9 -> M5.5 Fig4.10 -> M5.6 Causal Synthesis`.

Terminal compute state:

`M5_COMPUTE_READY_FOR_REVIEW`.

Do not pause between passing substages. Emit the required handoff/review evidence, commit/push, update `codex_handoff/LATEST_REPORT.md`, and continue.

## Current immediate stage — M5.0A

First establish the M5 formal anchor and resumable experiment infrastructure:

- prove branch ancestry;
- release build + all DTC CTests;
- LEGACY/Base/IO/OO sentinel regressions against M4;
- formal identity tuple and runtime/toolchain hashes;
- resumable result registry;
- measured safe batch concurrency;
- `handoffs/M5_0A_ANCHOR.md`.

Then continue automatically to M5.0B.

## M5.0B workload priority

Recover and source-verify all ten thesis compute algorithms. First explicitly audit:

- `gemv -> gemver?`;
- `gesu -> gesummv?`;
- `conv2d -> 2DConvolution/pb_2dconv?`.

Missing binaries/wrappers are problems to solve inside the Goal, not reasons to substitute algorithms or stop immediately.

SpMV receives special fidelity analysis because the M4 input did not exercise the Base PIB bottleneck described by the thesis.

## Parallel graphics preparation

Graphics G0-G2 may run in parallel with compute work:

- recover glmark2 scene/version/assets/provenance;
- audit direct/trace/proxy feasibility;
- prepare source-backed execution if possible.

Graphics must not block compute M5 and must not contaminate the compute formal behavior anchor. `GM-ALL-PAPER` remains forbidden until all five graphics workloads are source-backed and correctness-clean.

## Problem behavior

Follow `M5_PROBLEM_RESOLUTION_POLICY.md`.

Assertions, missing counters, missing workloads, build errors, timeouts, unexpected bottlenecks, weak speedup, and newly discovered implementation bugs are normally `RESOLVING_ISSUE` states. Diagnose, repair when source-correct, regress, invalidate stale results as needed, and continue.

Pause only at a true `RESEARCHER_DECISION_REQUIRED` boundary: required change to frozen architecture semantics, irreducible scientific ambiguity, inability to verify a required compute algorithm without changing experiment meaning, contradiction of a researcher-frozen metric definition, or final compute review state.

## Scope boundary

M5 v1 authorizes the ten-compute paper mechanism study through M5.6 plus parallel graphics preparation G0-G2.

It does **not** yet authorize post-review graphics formal aggregation, Figure 4.6 area claims, MODERN_OO_SECTOR paper comparisons, or M5.7+ supplemental studies.
