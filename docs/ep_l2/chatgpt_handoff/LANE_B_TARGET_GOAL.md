# EP-L2 Codex Target Goal — Lane B Descriptor-512 Calibration

## One-line goal

> Starting from the exact C7e formal source pair, autonomously make descriptor capacity safely parameterized to 512 if necessary, prove D256 backward equivalence, pass D512 boundary and natural preflight validation, then complete one frozen 13x2 @850 MHz D512 speculative mirror with analysis-ready evidence; update the shared workboard and Lane-B handoff; STOP before promoting D512 to the primary baseline or implementing RO/TVD/Unified.

## Read order

From `/workspace/worktrees/accel-sim-ep-l2/` fetch/pull latest `hrl/ep-l2-exp-v0`, then read:

```text
docs/ep_l2/chatgpt_handoff/CURRENT_STATE.md
docs/ep_l2/chatgpt_handoff/INTERIM_22OF26_CHATGPT_REVIEW.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
docs/ep_l2/chatgpt_handoff/PARALLEL_MASTER_PLAN.md
docs/ep_l2/chatgpt_handoff/PARALLEL_NEW_WINDOW_BOOTSTRAP.md
docs/ep_l2/chatgpt_handoff/LANE_B_DESCRIPTOR512_HANDOFF.md
docs/ep_l2/chatgpt_handoff/LANE_B_DESCRIPTOR512_ACCEPTANCE_CRITERIA.md
```

## Target-mode behavior

Do not stop at the first failed build/test/preflight. Within the authorized Lane B scope, diagnose and repair until every applicable acceptance gate passes.

Allowed autonomous repairs include:

```text
descriptor-capacity parameterization
telemetry histogram/cardinality generalization
parser/analyzer/schema support
D512 config overlays
runner/provenance/test/review-pack fixes
```

Not allowed:

```text
Line MSHR change
per-address cap change
L1 change
WAD/payload/bank functional change
queue/DRAM change
trace/workload change
Lane A runtime modification
```

If a fix would cross that boundary, record the blocker and stop.

## Completion states

The Lane B target is complete only when:

```text
D512_READY
and
D512_MIRROR_COMPLETE
```

have both been supported by the acceptance criteria and the workboard contains exact branch/SHA/config/result paths.

## Final outputs

Push Lane B source branches and documentation. Mirror documentation-only outputs to the coordination branch:

```text
docs/ep_l2/codex_handoff/LANE_B_LATEST.md
docs/ep_l2/review_packs/D512_CALIBRATION_r1/
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Then STOP. Do not independently declare D512 the calibrated primary baseline.
