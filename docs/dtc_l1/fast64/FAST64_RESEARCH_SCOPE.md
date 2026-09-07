# DTC FAST64 Research Scope

Status: **ACTIVE — PRIMARY PERFORMANCE PIVOT APPROVED**

Framework branch: `hrl/decoupled-l1-fast64-v0`

Pivot parent: `a9cdb3328a346cbc9a76b7ffadae3725b4209ab5`

Core authority remains:

- branch: `hrl/decoupled-l1-m5-v0`
- commit: `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`

## 1. Research objective

FAST64 is the primary performance-evaluation path for the implemented
Decoupled-Tag Cache (DTC) mechanism in Accel-Sim/GPGPU-Sim.

The target is **mechanism and trend reproduction**, not numerical recreation of
one dissertation platform or one published +X% aggregate.

The experiment must establish the causal chain:

`conventional-L1 structural pressure -> constrained live misses -> DTC removes
or decouples the limiting structures -> more useful memory-level concurrency
and/or better latency hiding -> performance effect`.

IO and OO must remain the implemented mechanisms. FAST64 may change only the
performance-evaluation platform shell and workload payloads under this contract;
it may not simplify, replace, or retune the DTC mechanism to produce a desired
speedup.

## 2. Evidence tiers

### Tier A — Mechanism-fidelity anchors

Retain and cite existing evidence from the M5 branch, including:

- DTC directed/unit tests and lifecycle/accounting tests;
- repaired-Core BICG same-bundle Base/IO/OO qualification;
- stats-light A1 terminal-equivalence and same-placement confirmation;
- lower-create-queue repair source/tests and preserved failures;
- existing valid SpMV heavy/exact-trace evidence.

Tier A proves mechanism implementation/correctness. FAST64 does not erase or
rewrite it.

### Tier B — FAST64 primary performance evidence

This branch supplies the principal performance results:

- frozen 64-SM platform shell;
- DTC-specific Base/IO/OO cache-resource contracts;
- frozen FAST12 workload roster;
- Base characterization;
- Base/IO/OO primary matrix;
- causal analysis;
- bounded sensitivity study.

### Tier C — Heavy auxiliary evidence

The following heavy M5 payloads are no longer primary-path blockers:

- 80-SM large ATAX recovery replays;
- SYR2K large immutable payload/replay;
- 2MM large immutable receipt/replay;
- other very-large trace payloads.

They remain preserved as stress/robustness/auxiliary evidence. They must never
be silently relabelled as FAST64 results.

## 3. Explicit exclusions from the FAST64 primary path

FAST64 does not require, before its primary performance matrix:

- completing 2MM local immutable unpack/receipt;
- completing SYR2K replay;
- waiting for the existing very-large 80-SM ATAX triplet to naturally terminate;
- completing Extended-20 E1/E2;
- reproducing the dissertation's absolute numeric aggregate.

Those items may continue independently if resources permit, but cannot block
FAST64 after FAST64's own repair-qualification gate passes.

## 4. Scientific non-negotiables

1. Workload membership must be frozen before observing FAST64 IO/OO benefit.
2. Inputs may not be changed based on DTC speedup.
3. Base/IO/OO in one triplet must share the same payload and unrelated GPU
   configuration.
4. All rows require natural termination and accounting drain unless explicitly
   marked diagnostic.
5. Negative/zero speedups remain results; they are never dropped for being
   unfavorable.
6. A workload-local infrastructure defect is isolated and repaired; it does
   not justify architecture retuning.
7. The Core mechanism SHA remains `15cfa76e...` unless a source-correct generic
   bug is demonstrated. Any Core change requires explicit invalidation mapping.

## 5. Reporting boundary

FAST64 result labels must be explicit:

- `FAST64_BASE`
- `FAST64_IO`
- `FAST64_OO`
- `GM-FAST12`

Do not call FAST64 aggregates `GM-ALL`, `GM-PAPER`, or a dissertation-exact
aggregate.

Paper-facing wording should state that FAST64 is a frozen simulator platform
used to reproduce the DTC mechanism and causal trends, with heavy/exact-trace
M5 evidence retained separately as implementation/stress support.

## 6. Completion target

FAST64 is complete only after:

`FAST64.0 -> FAST64.1 -> FAST64.2 -> FAST64.3 -> FAST64.4 -> FAST64.5 ->
FAST64.6 -> FAST64.7`

all satisfy their HARD acceptance gates in `FAST64_ACCEPTANCE_CONTRACT.md`.
