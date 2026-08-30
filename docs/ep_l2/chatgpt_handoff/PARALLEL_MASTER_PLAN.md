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

Run four logically isolated work lanes in parallel without sacrificing experimental provenance or causal interpretation:

```text
Lane A — finish current formal D256 Target Baseline 26-run
Lane B — descriptor 256 -> 512 calibration
Lane C — L1 causality / headroom factorial
Lane D — calibration analysis, hardware-cost analysis, and opportunity-study scaffolding
```

Do not merge these into one live worktree or one simulator result root.

## Scheduling principle

The default EP-L2 workflow is now:

> **dependencies gate evidence promotion, not necessarily computation launch.**

If a candidate source/config definition is already frozen and only a validation gate remains, dependent simulations may start as `SPECULATIVE_PENDING_GATE`. If the gate later passes, the exact results may be promoted without rerun. If a producer/source/timing-equivalence gate fails, descendants are invalidated and rerun from the repaired candidate.

This spends otherwise-idle compute to reduce wall-clock time. It does not weaken the original acceptance criteria.

## Codex window ownership

Use one Codex window per lane, not one window per simulator process.

```text
Window A: existing target-mode window; owns Lane A only
Window B: owns Lane B
Window C: owns Lane C
Window D: owns Lane D
```

Use **4 Codex windows total**. Each lane may launch multiple simulator processes internally when runner/config/result-root isolation is proven.

Do not ask Lane A to absorb B-D; it owns the formal campaign and must remain provenance-stable.

## New-window bootstrap / read order

Every Lane B/C/D window first reads:

```text
docs/ep_l2/chatgpt_handoff/CURRENT_STATE.md
docs/ep_l2/chatgpt_handoff/INTERIM_22OF26_CHATGPT_REVIEW.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
docs/ep_l2/chatgpt_handoff/PARALLEL_MASTER_PLAN.md
docs/ep_l2/chatgpt_handoff/SPECULATIVE_PARALLEL_EXECUTION_POLICY.md
docs/ep_l2/chatgpt_handoff/PARALLEL_NEW_WINDOW_BOOTSTRAP.md
```

Current server anchors:

```text
Coordination:
/workspace/worktrees/accel-sim-ep-l2/
  hrl/ep-l2-exp-v0

Lane A formal Framework — read-only to B/C/D:
/workspace/worktrees/accel-sim-ep-l2-c7e/
  hrl/ep-l2-c7e-final-char-v0

Lane A formal Core/config — read-only to B/C/D:
/workspace/worktrees/gpgpu-sim-ep-l2-c7e/
  hrl/ep-l2-c7e-final-char-v0
```

Then read the lane-specific HANDOFF + ACCEPTANCE_CRITERIA + TARGET_GOAL.

## Shared coordination rules

1. Never modify/rebuild/reuse Lane A formal runtime worktrees, binaries, or result directories.
2. Every lane uses its own branch/worktree/config overlays/result root/manifest.
3. Before updating `PARALLEL_WORKBOARD.md`, fetch latest and preserve other lanes/ChatGPT review fields.
4. Push source to lane-specific branches; mirror documentation-only status/review packs to `hrl/ep-l2-exp-v0`.
5. Parallel reports remain separate:

```text
Lane A: docs/ep_l2/codex_handoff/LATEST_REPORT.md
Lane B: docs/ep_l2/codex_handoff/LANE_B_LATEST.md
Lane C: docs/ep_l2/codex_handoff/LANE_C_LATEST.md
Lane D: docs/ep_l2/codex_handoff/LANE_D_LATEST.md
```

6. Calibration results are never silently promoted to primary formal results; `BASELINE-DECISION` remains required.
7. `COMPLETE_VALID` means local run completion/invariants only. Cross-lane maturity is separately `SPECULATIVE_PENDING_GATE`, `PROMOTED_VALID_CALIBRATION`, or `INVALIDATED_BY_UPSTREAM_GATE`.
8. Do not run from moving branch tips. Every speculative campaign records exact immutable Core/Framework/config/trace identity and unresolved promotion gates.

## Universal code/counter correctness rule

Any lane changing simulator code, telemetry, parser/schema, or configuration plumbing must satisfy its lane acceptance criteria and bootstrap correctness gate. Source inspection alone is insufficient.

Minimum evidence:

```text
source semantic map for changed counters
Release build
relevant directed tests
natural-workload smoke
parser/analyzer regression when output changes
terminal invariants/no resource leak
git diff --check
clean frozen source worktree
```

Observation-only/generalization code must reproduce the original configuration exactly before its results can be promoted.

## Cross-lane dependency graph

### Lane A

Finishes the formal D256 26/26 baseline independently.

### Lane B

Current frozen D512 candidate is:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

The short D256 backward-equivalence checks (`vectorAdd_4M`, `spmv`) have passed; the long `scan` equivalence is still a mandatory **promotion** gate.

Lane B may now launch in parallel:

```text
D512 preflight workloads
full 13x2 D512 speculative mirror
```

without waiting for `scan`. These outputs remain `SPECULATIVE_PENDING_GATE` until both:

```text
D256_EQ_SCAN_PASS
D512_PREFLIGHT_PASS
```

are satisfied. Prefer prioritizing the preflight workloads inside the same frozen 26-run mirror so those rows serve both purposes rather than duplicating simulations.

`D512_READY` itself is still declared only after the original Lane-B acceptance criteria pass.

### Lane C

D256 META/BANK cells continue independently.

Lane C may also start D512 META/BANK interaction cells **before D512_READY** using the exact frozen Lane-B D512 candidate above. These are provisional children and must carry:

```text
D256_EQ_SCAN_PASS
D512_PREFLIGHT_PASS
```

as promotion dependencies. If Lane B changes the candidate source/config after a failed gate, those children are invalidated and rerun.

One-at-a-time D256 L1 decomposition may launch per workload as soon as that workload crosses the material-response trigger; do not wait for all seven screening workloads.

### Lane D

May ingest speculative outputs early for tooling/provisional dashboards, but accepted `CAL-ANALYSIS` deltas and `BASELINE-DECISION` use only promoted evidence with valid lineage/config contracts.

## Workboard handshake

Task IDs:

```text
SRC-C7E
D512-AUDIT
D512-PREFLIGHT
D512-MIRROR
D-COST
L1-D256-META
L1-D256-BANK
L1-D512-META
L1-D512-BANK
CAL-ANALYSIS
BASELINE-DECISION
OPP-PREP
```

For rows authorized by the speculative policy, `Dependency` means **promotion dependency**, not a hard launch barrier. A row may be `RUNNING` with `SPECULATIVE_PENDING_GATE` in `Progress / result`, but must not become `DONE` until original acceptance criteria pass.

## Factorial interpretation

```text
                         L1 BASE        L1 META-HR      L1 BANK-HR
Descriptor 256          existing        run             run
Descriptor 512          mirror          run             run
```

Interpret using speedup together with downstream-pressure movement, not blocker counts alone.

## Global scientific constraint

Do not tune resources until MSHR becomes the bottleneck by construction. D512 and L1 headroom remove potentially artificial ceilings and reveal where pressure naturally moves across:

```text
MSHR / descriptors / L1 / WAD / payload / bank / lower scheduler / bandwidth
```

## Final convergence

```text
promoted Lane-A/B/C evidence + Lane-D analyzer
    -> CAL-ANALYSIS
        -> BASELINE-DECISION
            -> freeze D256 or D512 + justified L1 baseline
                -> opportunity study
```

No lane independently declares the calibrated primary baseline.
