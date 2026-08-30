# EP-L2 Lane E — Line-MSHR Causality Acceptance Criteria

This is the mandatory self-gating contract for Lane E.

Lane E is a controlled causal sensitivity probe. `Line MSHR=256` is a headroom control, not a proposed baseline.

## E0. Source identity / isolation — mandatory

PASS only if:

```text
Lane-E source is an exact descendant of the frozen Lane-B candidate
Core base      878f80869ce212e779df20b6421e4dc7f987825d
Framework base aae62b66685f15437cecf0193934f628e6fac6ae

formal D256 semantic base remains
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507

Lane A/B/C/D active worktrees and result roots are untouched
Lane E uses isolated branches/worktrees/results
all runs record exact Core/Framework/config/trace identities
```

D512 descendants may launch speculatively before `D512_PREFLIGHT_PASS`, but remain `SPECULATIVE_PENDING_GATE` until that exact Lane-B candidate is promoted.

## E1. Authorized experimental dimensions — mandatory

Primary new modeled delta:

```text
Line-MSHR entries: 128 -> 256
```

Matching Descriptor base remains either exactly:

```text
D256
or
D512
```

Frozen:

```text
per-address cap = 32
L1 BASE configuration
L2 sets/ways/line geometry
L2 miss queue / lower queue other than Line-MSHR entry count
WAD
payload capacity/organization
bank arbitration
DRAM queues/scheduler/timing
850 MHz
trace/workload
```

Any other modeled resource/timing change is a hard failure.

## E2. Line-MSHR cardinality / telemetry audit — mandatory

Audit allocator and observation paths for >128 entries.

PASS only if:

```text
allocator/full reason honors configured capacity
per-address and descriptor blockers remain independent
line occupancy max is exact
line occupancy histogram/p95 cannot clip >128
kernel/window delta state supports the configured capacity
parser/analyzer accepts >128 values
```

If code changes are needed, they must be parameterization/observation-only.

## E3. MSHR128 equivalence after source generalization — mandatory if source changes

At minimum:

```text
D512/B0-Banked/vectorAdd_4M/MSHR128
D512/B0-Banked/convolutionSeparable/MSHR128
```

compare final Lane-E source against the frozen Lane-B source.

Require exact simulated equality for:

```text
cycles
instructions
Descriptor need/full
Line-MSHR need/full
per-address cap
L1 key counters
bank conflict/wait
L2->DRAM/scheduler counts
DRAM bytes
terminal invariants
```

Any unexplained cycle/timing difference at identical config is a hard stop.

## E4. Directed MSHR256 boundary tests — mandatory

Tests must isolate Line-MSHR capacity from descriptor/per-address limits.

Required checkpoints:

```text
127, 128, 129 live distinct-line MSHRs
255, 256 live distinct-line MSHRs
allocation attempt at 256/full
release one then allocate again
no duplicate live line ownership
no leak
telemetry >128 not clipped
exact full_reason == LINE_MSHR_FULL
```

Use enough descriptor capacity and distinct addresses that another blocker cannot fire first.

## E5. Effective config diff — mandatory

Generate machine-readable effective-config evidence for each new row.

PASS only if:

```text
D256/MSHR256 vs D256/MSHR128:
  changed modeled field set == {line_mshr_entries}

D512/MSHR256 vs D512/MSHR128:
  changed modeled field set == {line_mshr_entries}

D512/spmv/MSHR256 vs D512/spmv/MSHR128:
  changed modeled field set == {line_mshr_entries}
```

Descriptor capacity is not an uncontrolled delta; it selects which matching base is used.

## E6. Release / regression — mandatory

Final experiment source must have:

```text
Release build PASS
existing relevant C7e/D512 regressions PASS
new MSHR256 boundary tests PASS
config-diff tests PASS
parser/analyzer tests PASS if changed
git diff --check PASS
clean frozen Lane-E source worktrees
```

## E7. Primary convolution 2x2 — mandatory

Required matrix:

```text
                         MSHR128             MSHR256
D256                     existing formal     new valid Lane-E row
D512                     existing Lane-B     new valid Lane-E row
```

All are `convolutionSeparable / B0-Banked / 850MHz / L1 BASE`.

New rows require:

```text
COMPLETE_VALID
normal exit
expected source/config/trace identities
terminal_clean = 1
payload consistency = 1
parser success
required C7e telemetry present
```

D512/MSHR256 remains provisional until Lane-B `D512_PREFLIGHT_PASS` for the exact candidate.

## E8. Negative control — mandatory

Run:

```text
spmv / D512 / B0-Banked / MSHR256
```

The matching MSHR128 base has no exact MSHR-full block. A material cycle response here must be investigated before claiming the convolution result uniquely demonstrates MSHR capacity causality.

## E9. Causal analysis — mandatory

Report at least:

```text
cycles and speedup
Descriptor need/full/occupancy
Line-MSHR need/full/avg/p95/max
per-address blocks
L1 blockers
L2->DRAM / scheduler / ReturnQ
DRAM bytes and native physical bus metric when available
5K temporal movement
```

Use the 2x2 interaction explicitly:

```text
Effect of MSHR256 under D256
vs
Effect of MSHR256 under D512
```

Do not infer causality from occupancy/full count alone.

Classification must be one of:

```text
MSHR_CAUSAL_AFTER_DESCRIPTOR_RELIEF
MSHR_ADMISSION_THROTTLE_DOWNSTREAM_LIMITED
MSHR_FULL_MOSTLY_SYMPTOMATIC
MSHR256_STILL_LIMITED
MIXED_OR_INSUFFICIENT
```

Screening interpretation:

```text
<2% cycle improvement     weak performance sensitivity
2-5%                      moderate
>5%                       strong
```

Pressure movement remains required in addition to speedup.

## E10. Review pack — mandatory

Publish:

```text
docs/ep_l2/codex_handoff/LANE_E_LATEST.md
docs/ep_l2/review_packs/LINE_MSHR_CAUSALITY_r1/
```

with source/config anchors, equivalence, directed tests, exact rows, 2x2 table, negative control, temporal/lower movement, raw-log index and hashes.

Update the Lane-E rows in `PARALLEL_WORKBOARD.md`.

## Completion state

Lane E is complete only at:

```text
LINE_MSHR_CAUSALITY_PROBE_COMPLETE
```

with all required evidence promoted/valid.

## Hard stops

Stop and request review if completion requires:

```text
changing MSHR lifetime/merge semantics rather than capacity
changing Descriptor beyond the frozen D256/D512 definitions
changing per-address cap
changing L1/WAD/payload/bank/lower/DRAM resources
accepting unexplained MSHR128 timing mismatch
changing workload/trace
modifying another lane's active worktree/results
silently promoting MSHR256 as the primary baseline
implementing RO/TVD/Unified
```
