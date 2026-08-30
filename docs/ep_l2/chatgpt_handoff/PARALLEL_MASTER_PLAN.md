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

Recommended initial setup:

```text
Window A: existing target-mode window; owns Lane A only
Window B: new; owns Lane B
Window C: new; owns Lane C
Window D: new; owns Lane D
```

Thus run **4 Codex windows total, 3 additional windows**.

Each window may launch multiple simulator processes internally when its own runner/config/result-root isolation is proven.

Do not ask the existing Lane A window to absorb B-D: it owns the formal campaign and must remain provenance-stable.

## Required read order for all new windows

```text
docs/ep_l2/chatgpt_handoff/CURRENT_STATE.md
docs/ep_l2/chatgpt_handoff/INTERIM_22OF26_CHATGPT_REVIEW.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
docs/ep_l2/chatgpt_handoff/PARALLEL_MASTER_PLAN.md
```

Then read the lane-specific handoff:

```text
Lane B: LANE_B_DESCRIPTOR512_HANDOFF.md
Lane C: LANE_C_L1_CAUSALITY_HANDOFF.md
Lane D: LANE_D_ANALYSIS_INFRA_HANDOFF.md
```

## Shared coordination rules

1. Never modify/rebuild/reuse Lane A formal runtime worktrees, binaries, or result directories.
2. Every lane uses its own branch/worktree/config overlays/result root/manifest.
3. Before updating `PARALLEL_WORKBOARD.md`, fetch the latest coordination branch and edit only the relevant execution/progress/evidence cells; preserve ChatGPT review fields and other lanes.
4. Push source to lane-specific branches; mirror documentation-only status/review packs to `hrl/ep-l2-exp-v0`.
5. Do not let multiple windows overwrite `codex_handoff/LATEST_REPORT.md` during parallel execution. Use dedicated reports:

```text
docs/ep_l2/codex_handoff/LANE_B_LATEST.md
docs/ep_l2/codex_handoff/LANE_C_LATEST.md
docs/ep_l2/codex_handoff/LANE_D_LATEST.md
```

Lane A continues to own the global `LATEST_REPORT.md` until the formal 26-run closeout. A later convergence step may replace it with a combined calibration report.
6. Calibration results are never silently promoted to primary formal results. Promotion requires `BASELINE-DECISION` review.
7. If a calibration result exposes a producer/parser bug that would invalidate Lane A formal data, record it immediately in the workboard and stop only the affected calibration lane; do not kill Lane A jobs unless the bug is proven to affect formal producer semantics.

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

Use the existing task IDs rather than informal chat messages:

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

A downstream lane may treat a dependency as satisfied only when the corresponding row is `DONE` and includes an exact branch/SHA/result path.

## Global scientific constraint

Do not tune the machine until MSHR becomes the bottleneck by construction. The purpose of D512 and L1 headroom is to remove potentially artificial upstream metadata/flow-control ceilings and observe where pressure naturally moves.

The final mechanism motivation must follow the evidence:

```text
MSHR / descriptors / L1 / WAD / payload / bank / lower scheduler / bandwidth
```

rather than selecting a preferred bottleneck in advance.

## Final convergence

When Lane A, required Lane B/C experiments, and Lane D analysis are complete:

```text
CAL-ANALYSIS
    -> BASELINE-DECISION
        -> freeze D256 or D512 + justified L1 baseline
            -> opportunity study
```

No lane may independently declare the calibrated primary baseline.