# EP-L2 Parallel Lane Master Plan

Status: **authorized parallel calibration while Lane A formal TB26 continues.**

Permanent coordination branch:

```text
hrl/ep-l2-exp-v0
```

Shared progress board:

```text
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
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

## Codex window ownership

Use one Codex window per lane, not one window per simulator process.

Recommended setup:

```text
Window A: existing target-mode window; owns Lane A only
Window B: new; owns Lane B
Window C: new; owns Lane C
Window D: new; owns Lane D
```

Thus use **4 Codex windows total, 3 additional windows**.

Each window may launch multiple simulator processes internally when its own runner/config/result-root isolation is proven.

Do not ask the existing Lane A window to absorb B-D: it owns the formal campaign and must remain provenance-stable.

## New-window bootstrap

Every new Lane B/C/D window first reads:

```text
docs/ep_l2/chatgpt_handoff/CURRENT_STATE.md
docs/ep_l2/chatgpt_handoff/INTERIM_22OF26_CHATGPT_REVIEW.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
docs/ep_l2/chatgpt_handoff/PARALLEL_MASTER_PLAN.md
docs/ep_l2/chatgpt_handoff/PARALLEL_NEW_WINDOW_BOOTSTRAP.md
```

The bootstrap records the current server topology:

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

Then read the lane contract:

### Lane B

```text
LANE_B_DESCRIPTOR512_HANDOFF.md
LANE_B_DESCRIPTOR512_ACCEPTANCE_CRITERIA.md
LANE_B_TARGET_GOAL.md
```

### Lane C

```text
LANE_C_L1_CAUSALITY_HANDOFF.md
LANE_C_L1_CAUSALITY_ACCEPTANCE_CRITERIA.md
LANE_C_TARGET_GOAL.md
```

### Lane D

```text
LANE_D_ANALYSIS_INFRA_HANDOFF.md
LANE_D_ANALYSIS_INFRA_ACCEPTANCE_CRITERIA.md
LANE_D_TARGET_GOAL.md
```

The `TARGET_GOAL` file is the autonomous Codex goal-mode entry; the `ACCEPTANCE_CRITERIA` file is the self-repair/self-gating contract.

## Shared coordination rules

1. Never modify/rebuild/reuse Lane A formal runtime worktrees, binaries, or result directories.
2. Every lane uses its own branch/worktree/config overlays/result root/manifest.
3. Before updating `PARALLEL_WORKBOARD.md`, fetch the latest coordination branch and edit only the relevant execution/progress/evidence cells; preserve ChatGPT review fields and other lanes.
4. Push source to lane-specific branches; mirror documentation-only status/review packs to `hrl/ep-l2-exp-v0`.
5. Do not let multiple windows overwrite `codex_handoff/LATEST_REPORT.md` during parallel execution. Use:

```text
Lane A: docs/ep_l2/codex_handoff/LATEST_REPORT.md
Lane B: docs/ep_l2/codex_handoff/LANE_B_LATEST.md
Lane C: docs/ep_l2/codex_handoff/LANE_C_LATEST.md
Lane D: docs/ep_l2/codex_handoff/LANE_D_LATEST.md
```

6. Calibration results are never silently promoted to primary formal results. Promotion requires `BASELINE-DECISION` review.
7. If a calibration result exposes a producer/parser bug that would invalidate Lane A formal data, record it immediately in the workboard; do not kill Lane A unless the defect is proven to affect formal producer semantics.

## Universal code/counter correctness rule

Any lane that changes simulator code, counter logic, telemetry, parser/schema, or configuration plumbing must satisfy its lane-specific acceptance criteria and the bootstrap universal gate. Source inspection alone is insufficient.

Minimum evidence includes:

```text
exact source semantic map for each new/changed counter
Release build
relevant directed tests
natural-workload smoke
parser/analyzer regression if output changes
terminal invariants/no resource leak
git diff --check
clean frozen source worktree
```

For observation-only/generalization code, prove timing neutrality or old-capacity backward equivalence at the original config. If that equality fails without an intended experimental resource change, it is a hard blocker.

## Cross-lane dependencies

```text
Lane A
  -> publishes/finalizes exact C7e formal source pair and D256 26/26 baseline

Lane B
  -> requires exact C7e source identity
  -> publishes D512_READY only after D256-equivalence + D512 preflight pass

Lane C
  -> D256 L1 META/BANK cells may start immediately from exact C7e D256 source
  -> D512 L1 cells wait for Lane B D512_READY

Lane D
  -> may start immediately on 22/26 data, temporal analysis tooling, cost methodology, and analysis framework
  -> consumes Lane A/B/C outputs as they appear
  -> opportunity scaffold may be prepared, but no functional RO/TVD/Unified mechanism or performance claim before BASELINE-DECISION
```

## Handshake through the workboard

Use these task IDs:

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

A downstream lane treats a dependency as satisfied only when the corresponding row is `DONE` and includes exact branch/SHA/config/result paths.

## Global scientific constraint

Do not tune the machine until MSHR becomes the bottleneck by construction. D512 and L1 headroom remove potentially artificial ceilings and reveal where pressure naturally moves.

The final mechanism motivation must follow evidence across:

```text
MSHR / descriptors / L1 / WAD / payload / bank / lower scheduler / bandwidth
```

## Factorial interpretation

For selected workloads:

```text
                         L1 BASE        L1 META-HR      L1 BANK-HR
Descriptor 256          existing        run             run
Descriptor 512          mirror          run             run
```

Interpret using both performance and downstream-pressure movement:

| Observation after L1 headroom | Interpretation |
| --- | --- |
| Little speedup; L2/lower pressure nearly unchanged | L1 events mostly symptoms/backpressure. |
| Clear speedup; L2/lower pressure changes little | L1-local independent bottleneck. |
| Clear speedup and L2 descriptor/lower demand rises materially | L1 was throttling and masking L2 opportunity. |
| L1 events fall but speedup is small while scheduler/BW pressure rises | Bottleneck moved downstream. |

## Descriptor-512 interpretation

```text
Descriptor blocks collapse + meaningful speedup + Line-MSHR pressure emerges
  => D512 strong calibrated-baseline candidate.

Descriptor blocks collapse + little speedup + lower-path pressure rises
  => D256 throttled, but true limit is downstream.

Descriptor blocks collapse + little other change
  => D256 caused retry pressure with low performance sensitivity.

Descriptor blocks remain material at 512
  => further calibration requires explicit hardware-cost justification.
```

## Final convergence

When Lane A and required Lane B/C/D milestones complete:

```text
CAL-ANALYSIS
    -> BASELINE-DECISION
        -> freeze D256 or D512 + justified L1 baseline
            -> opportunity study
```

No lane may independently declare the calibrated primary baseline.
