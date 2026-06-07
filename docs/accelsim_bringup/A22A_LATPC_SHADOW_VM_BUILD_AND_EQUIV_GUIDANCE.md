# A22A LATPC shadow VM build and behavior equivalence guidance

## Goal

Build the simulator and run baseline vs shadow VM default on NW.

Validate that enabling the shadow VM substrate does not change standard simulator behavior.

## Required script

Create:

scripts/accelsim/a22a_latpc_shadow_vm_build_equiv.py

## Inputs

A21C runner matrix.
A21B modified source files report.
A16 selected workload JSON.

## Required tasks

1. Determine whether nested simulator source changed.
2. Build if source changed.
3. Run baseline_no_shadow.
4. Run shadow_vm_default.
5. Parse standard stats and latpc_* stats.
6. Compare behavior fields:
   - cycles
   - instructions
   - IPC
   - L2 accesses
   - L2 misses
7. Write behavior compare CSV and report.

## Build policy

Use existing build command from prior rounds.

Likely:

make -C gpu-simulator

or exact command from A1/A6/A18.

Write build log:

.local_logs/A22A_<timestamp>_build.log

## Run policy

Use A21C runner.

Only selected workload.

No full benchmark campaign.

No tracer.

## Behavior tolerance

Integer fields:

- exact equality

Floating fields:

- absolute tolerance 1e-9
- relative tolerance 1e-6

If shadow VM default changes any exact behavior field, mark FAIL_BEHAVIOR_CHANGED.

## Required output files

.local_reports/A22A_latpc_shadow_vm_build_equiv_<timestamp>.md
.local_reports/A22A_latpc_behavior_compare_<timestamp>.csv
.local_logs/A22A_<timestamp>_build.log
.local_logs/A22A_<timestamp>_baseline.log
.local_logs/A22A_<timestamp>_shadow_vm.log

## Behavior compare CSV columns

- field
- baseline_value
- shadow_value
- abs_diff
- rel_diff
- tolerance_abs
- tolerance_rel
- status
- notes

## Summary report sections

1. Build status.
2. Run commands.
3. Standard stats.
4. latpc stats extracted.
5. Behavior comparison.
6. Final status.
7. Limitations.

## Status rules

PASS:
Build passes, both runs pass, behavior unchanged, shadow stats emitted.

PASS_WITH_WARNINGS:
Behavior unchanged but shadow stats partial.

PASS_DESIGN_ONLY:
Source implementation blocked, no build/run required.

FAIL_BUILD:
Build failed.

FAIL_RUN:
Run failed.

FAIL_BEHAVIOR_CHANGED:
Behavior fields changed.

FAIL_STATS_EMPTY:
Shadow VM stats missing or all important counters zero.
