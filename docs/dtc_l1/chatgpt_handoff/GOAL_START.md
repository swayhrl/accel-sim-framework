# DTC-L1 M5 Explicit Goal Launch Contract

Status: **ACTIVE — M5 v1 CONTINUOUS COMPUTE GOAL AUTHORIZED**

This is the durable objective for Codex Goal mode. Detailed experiment definitions are in `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`; the researcher-approved interpretation/activation is in `docs/dtc_l1/m5/M5_V1_APPROVAL.md`.

## Persistent Goal

Establish a source/workload/config/metric fidelity lock, then reproduce and explain the Decoupled-Tag Cache mechanism on the ten thesis general-purpose compute workloads through Figures 4.2, 4.5, 4.7, 4.8, 4.9, and 4.10, resolving ordinary implementation/workload/platform issues inside Goal mode instead of stopping at the first failure.

Primary scientific objective:

`traditional L1 structural limits -> fewer live concurrent misses -> DTC removes structural limits -> more concurrency / better latency hiding -> performance effect`.

Exact thesis speedups are references, not pass thresholds.

Final compute state:

`M5_COMPUTE_READY_FOR_REVIEW`.

The Goal is complete only when:

1. M5.0 fidelity lock is complete and a formal behavior anchor exists;
2. all ten thesis compute algorithms have source-backed reproducible mappings and deterministic inputs;
3. `gemv/gemver`, `gesu/gesummv`, and `conv2d/2DConvolution` naming/algorithm mappings are explicitly resolved;
4. platform/config and metric definitions are source-audited and frozen;
5. Figure 4.2 Base structural-bottleneck experiment is complete;
6. Figure 4.5 Base/IO/OO compute performance is complete;
7. Figure 4.7 common live-miss per-SM cycle-average result is complete;
8. Figure 4.8 logical-cache sensitivity is complete;
9. Figure 4.9 physical-cache/reclaim/deadlock-pressure sensitivity is complete;
10. Figure 4.10 PIB sensitivity is complete;
11. every weak/negative/surprising result has a source-backed causal classification rather than only a comparison to thesis numbers;
12. M5.6 integrated causal synthesis is complete;
13. graphics G0-G2 preparation has a source-backed readiness/feasibility classification;
14. all formal result identities, parsers, counter sanity, raw-log indexes, handoffs, and review packs required by the matrix/contract exist;
15. both M5 branches are pushed/clean and `git diff --check` passes;
16. `codex_handoff/LATEST_REPORT.md` says `M5_COMPUTE_READY_FOR_REVIEW`;
17. no post-review M5.7+ supplemental/graphics-formal stage has begun.

## Active branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`

Validated parents:

- Core `cdeec769fd0c1be12b45d58536ecb81074d4b415`;
- Framework `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`.

Do not modify the validated M1-M4 branches for M5 experiments.

## Mandatory read order

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
4. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
5. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
6. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
7. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`
8. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
9. this file
10. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
11. final M4 review pack / completion-accounting recovery evidence as regression context

Core:

12. `AGENTS.md`
13. `docs/dtc_l1/DTC_L1_SPEC.md`

The stale planning banner in `M5_EXPERIMENT_MATRIX.md` is superseded by `M5_V1_APPROVAL.md`; the matrix body is approved v1.

## Researcher-frozen interpretations

### Figure 4.5

Primary DTC configuration uses **16KB logical Tag/cache capacity + 80KB physical Cacheline Array**. IO PIB=256; OO PIB=128. Base remains conventional 16KB L1, PIB=8, MSHR=32.

### Figure 4.7

A live miss begins when a new L1/DTC miss is committed into lower-request ownership and ends on final lower-response completion. Pending-hit merge adds no live request; a real duplicate lower request after Tag eviction does.

Primary metric:

`avg_concurrent_misses_per_sm = sum(live misses across all SMs/cycles) / (num_SM * sampled_kernel_cycles)`.

### Figure 4.2

Formal paper-facing categories only:

1. PIB/waiting-buffer full;
2. true Tag & Cacheline allocation failure;
3. MSHR capacity/merge failure;
4. Miss Queue/lower-request-capacity failure.

Tag-bank arbitration conflicts remain a separate diagnostic channel.

## Authorized continuous sequence

Execute and transition automatically:

`M5.0A -> M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`.

Each successful substage must:

1. satisfy its acceptance criteria;
2. produce the handoff required by `M5_HANDOFF_CONTRACT.md`;
3. run strict parser/counter sanity;
4. commit compact evidence with explicit path staging;
5. push affected branches;
6. update `codex_handoff/LATEST_REPORT.md`;
7. immediately begin the next authorized substage.

Do not stop to ask for confirmation between passing substages.

## Immediate start point — M5.0A

Start with branch/anchor/reproducibility lock:

- verify ancestry from validated M4 finals;
- release build and all DTC CTests;
- LEGACY/Base/IO/OO sentinel regressions;
- formal source/config/workload/parser identity format;
- runtime/toolchain/library hashes;
- resumable result registry;
- safe measured simulation concurrency;
- `m5/handoffs/M5_0A_ANCHOR.md`.

Then continue to workload recovery M5.0B.

## Workload recovery behavior

All ten thesis compute algorithms must be recovered/source-verified. Missing binaries or wrappers are not ordinary stop conditions.

Use canonical suite source where necessary, build source-equivalent wrappers, validate output, and lock source/PTX/input provenance. Never substitute a different algorithm because it is easy to run.

Input sizes are selected from canonical/standard datasets and Base-only full-load/work-amount evidence. Never choose a dataset because it maximizes DTC speedup.

SpMV receives special fidelity investigation if Base still does not exhibit the paper-discussed PIB pressure.

## Problem-resolution behavior

Follow `M5_PROBLEM_RESOLUTION_POLICY.md`.

The following are normally in-goal problems to diagnose and resolve rather than Goal-stop boundaries:

- missing workload/input/wrapper;
- build/PTX extraction failure;
- missing parser/counter;
- assertion discovered under a new workload;
- operation-count mismatch;
- timeouts;
- weak/negative performance;
- absent expected Base structural pressure;
- unexpected Tag-bank/downstream bottleneck;
- source-backed simulator bug;
- stale formal results after a repair.

Use the issue lifecycle in `implementation/M5_ISSUE_LOG.md`, regress after repairs, invalidate stale results, and resume.

## Pause conditions

Pause with `RESEARCHER_DECISION_REQUIRED` only if:

- the needed change would alter frozen M0/M1-M4 architecture semantics rather than correct implementation fidelity;
- multiple scientifically different source-supported interpretations remain and the thesis does not resolve them;
- a required compute algorithm cannot be source-verified/reconstructed without changing experiment meaning;
- a finding invalidates one of the researcher-frozen M5 definitions above;
- compute M5 reaches terminal `M5_COMPUTE_READY_FOR_REVIEW`.

Graphics infeasibility alone is not a compute pause condition.

## Parallel graphics preparation

Progress G0-G2 in parallel when resources permit. It may recover provenance, audit simulator/trace feasibility, and prepare a source-backed execution manifest.

Do not let graphics work alter the compute formal behavior anchor without normal invalidation/regression. Do not emit `GM-ALL-PAPER` until all five graphics workloads are source-backed and correctness-clean.

## Forbidden before compute review

Do not:

- tune architecture, workload size, or downstream parameters to thesis speedups;
- hide valid negative results;
- silently replace algorithms;
- fold Tag-bank conflict into Figure 4.2 Tag+Cacheline allocation failure;
- use heterogeneous occupancy proxies for Figure 4.7;
- include MODERN_OO_SECTOR in paper Figures 4.2-4.10;
- claim simulator C++ storage as Figure 4.6 synthesis area;
- present a graphics memory proxy as direct graphics reproduction;
- start M5.7+ supplemental studies before compute review.
