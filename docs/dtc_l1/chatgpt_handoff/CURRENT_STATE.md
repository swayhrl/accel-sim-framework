# DTC-L1 Current State

Last coordination update: 2026-09-03

Status: **M1-M4 PASS; M5 EXPERIMENT MATRIX DRAFTED; M5 EXECUTION NOT YET AUTHORIZED**

## Validated parent anchors

M1-M4 final Core:

- branch: `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`
- SHA: `cdeec769fd0c1be12b45d58536ecb81074d4b415`

M1-M4 final Framework:

- branch: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`
- SHA: `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`

M4 review pack:

`docs/dtc_l1/review_packs/M4_COMPUTE_BRINGUP/`

Codex final M4 report:

`docs/dtc_l1/codex_handoff/LATEST_REPORT.md`

M0 and M1-M4 branches are now historical validated anchors. Do not perform M5 experiments or exploratory implementation on them.

## M5 planning branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`
- created from Core M1-M4 final SHA `cdeec769...`.

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`
- created from Framework M1-M4 final SHA `56369da3...`.

These branches currently contain M5 planning/coordination only. Formal M5 execution is not authorized until the user approves the experiment matrix.

## Research objective for M5

M5 is not a numerical-target replication exercise. The goal is to show, in the simulator, the performance benefit and causal mechanism of the already-implemented Decoupled-Tag Cache RTL idea.

Primary scientific objective:

`traditional L1 structural constraints -> lower memory-level concurrency -> DTC removes constraints -> higher live concurrent miss requests / latency hiding -> performance effect`.

If performance is weak or negative, M5 must determine whether the cause is:

- implementation/modeling fidelity;
- workload/input fidelity;
- downstream simulator/platform bottleneck;
- traffic side effect;
- compute-bound behavior;
- or a genuine mechanism limitation.

Do not tune the design or input to hit the thesis' +22%/+30% results.

## User-frozen M5 decisions

1. Reproduction target: **mechanism/trend fidelity**, not exact numeric speedup.
2. Recover all ten thesis general-purpose compute workloads first.
3. Prepare graphics in parallel so it can attach immediately after compute closeout.
4. First workload-provenance audit must test `gemv -> gemver`, `gesu -> gesummv`, and `conv2d -> 2DConvolution/pb_2dconv` hypotheses from thesis descriptions/source.
5. Figure 4.2 is part of formal M5.
6. Figure 4.7 concurrent miss metric is frozen as a common lifecycle: **L1/DTC new miss committed into lower-request ownership -> final lower response completes that request**, cycle-averaged.
7. Ordinary problems must be solved inside Goal mode rather than treated as automatic stop conditions.

## M5 planning documents

Read:

1. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
2. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
3. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
4. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`

The matrix currently covers:

- M5.0 Fidelity Lock;
- M5.1 Figure 4.2 baseline motivation;
- M5.2 Figures 4.5 + 4.7 main result;
- M5.3 Figure 4.8 logical-cache sweep;
- M5.4 Figure 4.9 physical-cache/release sweep;
- M5.5 Figure 4.10 PIB sweep;
- M5.6 integrated causal analysis;
- M5.G nonblocking graphics preparation;
- M5.7+ optional extensions after paper-mode compute closeout.

## Paper compute workload set

The thesis Table 4.1 compute set to recover is:

Cache-efficient:

- bicg
- atax
- gemv (alias audit required)
- mvt
- syrk
- gesu (alias audit required)
- syr2k

Cache-inefficient:

- spmv
- 2mm

Compute-intensive:

- conv2d (source-equivalence audit required)

Compute-only geometric mean must be labeled `GM-GP`. Do not call it thesis `GM-ALL`, which includes graphics.

## Current execution boundary

`CODEX_NEXT_STAGE.md` and `GOAL_START.md` remain in **PLANNING HOLD** state on the M5 branch until user approval.

Do not start formal M5 runs yet.

After approval, ChatGPT will flip the M5 Goal contract to ACTIVE and Codex may execute continuously through M5.0 -> M5.6, resolving ordinary issues in-goal according to `M5_PROBLEM_RESOLUTION_POLICY.md` and stopping at `M5_COMPUTE_READY_FOR_REVIEW` or a true researcher-decision boundary.