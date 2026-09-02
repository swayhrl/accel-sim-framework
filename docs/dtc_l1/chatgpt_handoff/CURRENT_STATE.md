# DTC-L1 Current State

Last coordination update: 2026-09-02

Status: **M0 SPEC FROZEN; M1-M4 CONTINUOUS GOAL AUTHORIZED**

## Source anchors

Frozen M0 framework anchor:

- official: `accel-sim/accel-sim-framework:dev`
- official base SHA: `d930ad6d02c09bb56867132583735aba0389cff4`
- project M0 branch: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-v0`
- M0 documentation SHA: `4ce6da7f000aa3cd68cc011cbc004d4774383e66`

Active framework goal branch:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`
- created directly from the M0 branch; M0 remains read-only.

Frozen M0 core anchor:

- official: `accel-sim/gpgpu-sim_distribution:dev`
- official base SHA: `91880c53383d5a6a6742bfb1be2c5f34e39c7871`
- project M0 branch: `swayhrl/gpgpu-sim:hrl/decoupled-l1-v0`
- M0 documentation SHA: `5e35de9914f1ad28647ef3a416d054b86f3e44a5`

Active core goal branch:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`
- created directly from the M0 branch; M0 remains read-only.

## Authoritative design specification

Core repository:

`docs/dtc_l1/DTC_L1_SPEC.md`

Frozen paper-mode defaults include:

- warp width 32;
- simulator coalescer default 32 threads/cycle, with 16-thread original-RTL sensitivity;
- logical Tag capacity 16KB;
- 128B line;
- 32 sets x 4 ways, LRU;
- 4 Tag banks, 8 sets x 4 ways per bank;
- `tag_bank = logical_set_index % 4`;
- 1 Tag request/bank/cycle;
- fixed 80KB physical array = 640 x 128B lines;
- no Tag-bank-to-Data-location binding;
- RR physical allocation, max 4 lines/cycle;
- partial allocation retained on stall; no rollback;
- every depicted pipeline stage = 1 cycle;
- bounded queues/buffers backpressure upstream;
- Baseline PIB 8, Baseline MSHR 32;
- IO PIB 256, OO PIB 128;
- IO/OO retire width 1 instruction/cycle;
- same-cycle physical-line release visibility;
- paper default 8 SM;
- each SM L1 lower issue width 1 request/cycle;
- global lower outstanding limit 256;
- OO Ref Count = per coalesced 128B cacheline reference;
- 13-bit default Ref Count width;
- paper reproduction first uses whole-line 128B DTC;
- modern sector extension keeps 128B Tag->Physical mapping and line-level Ref Count, while readiness/merge/wait dependencies are 4 x 32B sector granular.

## Active goal

The single authorized Goal-mode task is to execute M1 through M4 continuously, with HARD gates between major stages:

- M1 — Foundation + paper Baseline + observability;
- M2 — IO-DTC read path;
- M3 — OO-DTC read path + Ref Count/Merge + sector extension;
- M4 — Store/Atomic/Fence/architectural-bypass integration + compute workload bring-up.

Codex may advance automatically only when every HARD gate for the current stage passes. On any hard failure or source-semantic ambiguity requiring a guess, STOP and report.

Detailed executable specifications:

- `docs/dtc_l1/goal/M1_M4_GOAL_PLAN.md`
- `docs/dtc_l1/goal/COUNTER_INVARIANT_SPEC.md`
- `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`
- `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`

## Current implementation state

Not yet implemented at goal authorization time:

- explicit thesis-style Baseline PIB;
- shared paper-mode Tag-bank timing layer;
- DTC instruction lifecycle/context;
- IO-DTC;
- OO-DTC;
- DTC counter/parser infrastructure;
- sector-DTC extension;
- Store/Atomic/Fence DTC lifecycle;
- DTC workload presets and diagnostic result pipeline.

## Scientific boundary of this goal

M1-M4 establishes a trustworthy implementation and brings real compute workloads to completion under Base/IO/OO.

It does NOT authorize:

- fitting speedups to thesis numbers;
- claiming reproduction of +22%/+30%;
- final Chapter 4 figure generation;
- equal-area conclusions;
- graphics proxy/calibration;
- final modern-sector performance claims;
- DTC policy-driven bypass.

Those belong to M5+ after implementation review.
