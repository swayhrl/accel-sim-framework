# DTC-L1 Current State

Last coordination update: 2026-09-02

Status: **M0 SPEC FROZEN; IMPLEMENTATION HOLD**

## Source anchors

Framework:

- official: `accel-sim/accel-sim-framework:dev`
- base SHA: `d930ad6d02c09bb56867132583735aba0389cff4`
- project: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-v0`

Core:

- official: `accel-sim/gpgpu-sim_distribution:dev`
- base SHA: `91880c53383d5a6a6742bfb1be2c5f34e39c7871`
- project: `swayhrl/gpgpu-sim:hrl/decoupled-l1-v0`

## Frozen architecture / design decisions

The authoritative detailed specification is in the core repository's `docs/dtc_l1/DTC_L1_SPEC.md`.

High-level frozen defaults:

- paper-mode warp width: 32 threads;
- simulator default coalescer width: 32 threads/cycle; 16 threads/cycle retained as a configurable original-RTL sensitivity;
- logical Tag capacity: 16KB;
- line size: 128B;
- logical geometry: 32 sets × 4 ways;
- replacement: LRU;
- Tag Array: 4 banks/partitions, each 8 sets × 4 ways;
- Tag-bank mapping: `logical_set_index % 4`;
- Tag-bank throughput: 1 request/bank/cycle;
- physical Cacheline Array: fixed 80KB = 640 × 128B lines, entirely L1-owned;
- physical allocation: round-robin, aggregate width 4 lines/cycle;
- partial allocation allowed; allocated lines are retained when later allocation stalls; no rollback;
- default Data-bank conflict modeling disabled in the first mechanism model;
- every depicted pipeline stage is modeled as 1 cycle;
- bounded queues/buffers apply upstream backpressure when full;
- Baseline PIB: 8;
- Baseline MSHR: 32;
- IO PIB: 256;
- OO PIB: 128;
- IO retire width: 1 instruction/cycle;
- OO retire width: 1 instruction/cycle;
- physical release is visible to allocation in the same cycle;
- 8-SM paper-mode default;
- each SM L1 may issue 1 lower-memory request/cycle;
- global lower-memory outstanding limit: 256;
- OO Ref Count granularity: per coalesced 128B cacheline reference/request;
- Ref Count default width: 13 bits (conservative 128×32 upper bound);
- primary thesis reproduction uses whole-line 128B DTC;
- modern sector extension keeps 128B Tag→Physical renaming and line-level Ref Count, but uses 4×32B INVALID/PENDING/VALID state, per-sector OO merge state, and per-sector `wait_cnt` dependencies.

## Important mechanism interpretation

The 80KB physical array and 16KB logical Tag space are deliberately decoupled. A Tag bank does not constrain which physical line may be allocated.

The original RTL has area-driven 16-thread processing and 4-bank allocation resources. The simulator preserves the important throughput/resource constraints while allowing a 32-thread/cycle coalescer default for Base/IO/OO symmetry.

IO-DTC physical-space deadlock is not to be prevented by an all-or-nothing allocator. It should emerge naturally when a partially allocated instruction holds physical lines, cannot allocate its remaining lines, and FIFO progress cannot release enough older lines.

## Completed stages

- M0 research/design discussion: COMPLETE.
- official upstream branch anchoring: COMPLETE.
- M0 architecture spec committed: COMPLETE.

## Not yet implemented

- explicit thesis-style Baseline PIB model;
- IO-DTC read path;
- OO-DTC read path;
- DTC statistics/assertions;
- Store/Atomic/Fence integration;
- DTC policy bypass;
- formal paper workload experiments;
- modern sector-DTC formal experiments;
- graphics-memory proxy/calibration.

## Deferred semantics

For the first read-path implementation, Store/Atomic/Fence full DTC lifecycle semantics are deferred. Existing architectural L1 bypass semantics must still remain correct. Thesis DTC policy bypass is a later extension.

Temporary Store/Atomic routing used only to bring up workloads must not be treated as formal IO-vs-OO evidence.

## Current open implementation questions

These are source-integration questions, not permission to change the frozen architecture:

1. exact insertion point for explicit Baseline/DTC PIB admission and backpressure;
2. exact physical-allocation identity carried by lower-memory fills/returns;
3. clean reuse/wrapping strategy for current sector-cache classes;
4. authoritative relationship between standalone core and framework `gpu-simulator` source trees;
5. Store/Atomic/Fence lifecycle attachment points for the later compute-complete stage;
6. stats/config/run-script plumbing.

## Current research direction

First reproduce and validate the mechanism with compute workloads and directed microbenchmarks. Separate paper-mode whole-line DTC from modern sector-DTC. Graphics is supplemental unless calibrated against real/request-stream evidence.

## Immediate execution order

1. Keep both branches frozen except for coordination/spec documents.
2. Plan M1-M3 in ChatGPT with explicit implementation goals, tests, acceptance criteria, and STOP boundaries.
3. Update `CODEX_NEXT_STAGE.md` with the approved goal-mode plan.
4. Only then allow Codex implementation.
