# EP-L2 Parallel Lane Master Plan

Status: **authorized dependency-graph parallel calibration with speculative execution when compute is abundant.**

Permanent coordination branch:

```text
hrl/ep-l2-exp-v0
```

Shared progress board:

```text
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Speculative scheduling policy:

```text
docs/ep_l2/chatgpt_handoff/SPECULATIVE_PARALLEL_EXECUTION_POLICY.md
```

## Goal

Run five logically isolated work lanes without sacrificing experimental provenance or causal interpretation:

```text
Lane A — frozen formal D256 Target Baseline 26-run (completed / reviewed)
Lane B — Descriptor 256 -> 512 calibration
Lane C — L1 causality / headroom factorial
Lane D — calibration analysis / provenance / hardware-cost infrastructure
Lane E — Line-MSHR causality probe after Descriptor relief
```

Do not merge these into one live worktree or one simulator result root.

## Scheduling principle

> **Dependencies gate evidence promotion, not necessarily computation launch.**

If source/config semantics are frozen and only a validation gate remains, dependent simulations may launch as `SPECULATIVE_PENDING_GATE`. Exact matching results may later be promoted without rerun. A real source/config/producer/timing defect invalidates descendants and requires rerun from the repaired candidate.

This spends compute to reduce wall-clock time; acceptance standards do not change.

## Codex window ownership

Use one Codex window per lane, not one per simulator process:

```text
Window A: Lane A final baseline / closeout only
Window B: Descriptor-512 calibration
Window C: L1 causality
Window D: analysis/provenance infrastructure
Window E: Line-MSHR causality
```

Use **5 Codex windows total** when all lanes are active. Each window may launch multiple isolated simulator processes.

Lane A has now completed its formal campaign and should not absorb new calibration implementation work.

## Server anchors

Coordination:

```text
/workspace/worktrees/accel-sim-ep-l2/
branch hrl/ep-l2-exp-v0
```

Frozen formal Lane-A Framework/Core remain read-only to other lanes:

```text
/workspace/worktrees/accel-sim-ep-l2-c7e/
/workspace/worktrees/gpgpu-sim-ep-l2-c7e/
```

Lane E uses its own isolated worktrees defined in `LANE_E_TARGET_GOAL.md`.

## Parallel report ownership

```text
Lane A: docs/ep_l2/codex_handoff/LATEST_REPORT.md
Lane B: docs/ep_l2/codex_handoff/LANE_B_LATEST.md
Lane C: docs/ep_l2/codex_handoff/LANE_C_LATEST.md
Lane D: docs/ep_l2/codex_handoff/LANE_D_LATEST.md
Lane E: docs/ep_l2/codex_handoff/LANE_E_LATEST.md
```

## Shared correctness rules

1. Every lane uses separate branch/worktree/config overlay/result root/manifest.
2. Never modify another lane's active runtime worktree or result root.
3. Before workboard updates, fetch latest and preserve other lanes/ChatGPT review fields.
4. Calibration data are never silently promoted to formal/primary baseline data.
5. `COMPLETE_VALID` is local run validity only; maturity is tracked separately.
6. Do not run from moving branch tips; record exact immutable Core/Framework/config/trace identities.
7. Any simulator/telemetry/parser/config-plumbing change requires Release build, directed tests, natural smoke, parser/analyzer regression as applicable, terminal invariants, `git diff --check`, and clean frozen source.
8. Observation-only/generalization changes require exact original-config timing/behavior equivalence before promotion.

## Lane A

Final D256 850-MHz formal campaign is complete and independently reviewed PASS:

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
26/26 accepted
```

It is the frozen calibration reference dataset, not yet automatically the final calibrated primary baseline.

## Lane B

Frozen D512 candidate:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

D256 backward equivalence has passed `vectorAdd_4M`, `spmv`, and `scan`.

The full D512 mirror is already running speculatively; completed rows remain provisional until `D512_PREFLIGHT_PASS`.

Important current causal observation from the 22/26 interim review:

```text
convolutionSeparable D256:
  descriptor full 3,373,327
  Line-MSHR full 0

convolutionSeparable D512:
  descriptor full 0
  Line-MSHR full 931,416
```

with no performance gain. This motivates Lane E.

## Lane C

D256 L1 META-HR/BANK-HR cells are locally accepted. D512 interaction cells may execute speculatively from the exact Lane-B candidate and promote only after Lane-B promotion gates pass.

## Lane D

Lane-D V3 analysis/provenance/cost infrastructure is reviewed PASS and its semantics are frozen except for bug fixes.

It may ingest speculative data for provisional dashboards, but accepted `CAL-ANALYSIS` uses promoted evidence only.

Lane E uses a separate causality analysis/report and does not modify Lane-D V3 merely to add the MSHR dimension.

## Lane E

Dedicated small Line-MSHR causal probe.

Primary matrix:

```text
convolutionSeparable / B0-Banked

                         MSHR128             MSHR256
Descriptor256            existing formal     new Lane-E
Descriptor512            existing Lane-B     new Lane-E
```

Plus short negative control:

```text
spmv / D512 / B0-Banked / MSHR256
```

Line-MSHR256 is sensitivity headroom, not a proposed baseline. D512 descendants may launch before preflight completion but remain `SPECULATIVE_PENDING_GATE` until the exact Lane-B candidate is promoted.

Lane-E task IDs are defined in:

```text
docs/ep_l2/chatgpt_handoff/LANE_E_WORKBOARD_ROWS.md
```

and its execution contract is:

```text
LANE_E_LINE_MSHR_CAUSALITY_HANDOFF.md
LANE_E_LINE_MSHR_CAUSALITY_ACCEPTANCE_CRITERIA.md
LANE_E_TARGET_GOAL.md
```

## Global scientific constraint

Do not tune the machine to manufacture an MSHR-centric story. Descriptor, L1 and MSHR headroom experiments are controls that reveal where pressure naturally moves across:

```text
Descriptor / Line-MSHR / per-address cap / L1 / WAD / payload / bank / lower scheduler / DRAM
```

## Final convergence

```text
Lane A frozen formal baseline
+ promoted Lane B D512 mirror
+ promoted Lane C L1 causality
+ reviewed Lane E Line-MSHR causality
+ Lane D V3 analysis/provenance
        -> CAL-ANALYSIS
            -> BASELINE-DECISION
                -> freeze calibrated D256 or D512 + justified L1 settings
                    -> opportunity study / RO-TVD-Unified mechanism work
```

No lane independently declares the calibrated primary baseline.
