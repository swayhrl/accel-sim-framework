# DTC-L1 M5 Explicit Goal Launch Contract

Status: **DRAFT ONLY — NOT YET AUTHORIZED**

This file is the short durable objective that will be activated after the user approves the M5 experiment matrix.

## Proposed persistent Goal

Establish a source/workload/config/metric fidelity lock, then reproduce and explain the Decoupled-Tag Cache mechanism on the ten thesis general-purpose compute workloads through Figures 4.2, 4.5, 4.7, 4.8, 4.9, and 4.10, resolving ordinary implementation/workload/platform issues inside Goal mode instead of stopping at the first failure.

Final compute state:

`M5_COMPUTE_READY_FOR_REVIEW`

The Goal is complete only when:

1. all ten thesis compute algorithms have source-backed reproducible mappings and deterministic inputs;
2. platform/config and metric definitions are locked and source-audited;
3. Figure 4.2 Base structural bottleneck experiment is complete;
4. Base/IO/OO main performance and common average-concurrent-miss results are complete;
5. logical-cache, physical-cache, and PIB sensitivity sweeps are complete;
6. every surprising performance result has a mechanism root-cause classification rather than a numerical-target workaround;
7. integrated causal analysis explains performance through stall, concurrency, HOL, reclaim, traffic, and downstream evidence;
8. graphics provenance/feasibility preparation has progressed independently and its status is recorded;
9. all FORMAL results have complete provenance and strict counter/accounting checks;
10. both M5 branches are pushed/clean;
11. no unresolved correctness/fidelity issue remains in compute scope.

## Branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`
- parent `cdeec769fd0c1be12b45d58536ecb81074d4b415`.

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`
- parent `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`.

Do not write M5 work back onto the M1-M4 branches.

## Mandatory future read order

1. Framework `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
4. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
5. this file
6. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
7. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
8. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
9. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`
10. M4 final review pack and implementation evidence as historical validated context
11. Core `AGENTS.md`
12. Core `docs/dtc_l1/DTC_L1_SPEC.md`

## Proposed progression

`M5.0A anchor -> M5.0B workloads -> M5.0C platform -> M5.0D metrics -> M5.0E pilots -> M5.1 Fig4.2 -> M5.2 Fig4.5+4.7 -> M5.3 Fig4.8 -> M5.4 Fig4.9 -> M5.5 Fig4.10 -> M5.6 causal -> M5_COMPUTE_READY_FOR_REVIEW`.

Graphics G0-G2 preparation proceeds as a nonblocking side track.

## Proposed continuation policy

Ordinary failures are not terminal. Follow `M5_PROBLEM_RESOLUTION_POLICY.md` for workload recovery, build/PTX problems, assertions, counter gaps, performance anomalies, timeouts, configuration mismatches, and implementation bugs. Diagnose -> minimally repair/reconstruct -> regress -> invalidate stale data when needed -> resume the same substage.

Do not tune design knobs or inputs to reproduce thesis speedup numbers.

A future active Goal may pause only when a real scientific/researcher decision cannot be resolved from thesis/source/canonical-workload evidence or when final compute review is reached.

## Current boundary

This file is a draft. Do not start M5 merely because this file exists. Wait for explicit user approval and the status flip to ACTIVE.