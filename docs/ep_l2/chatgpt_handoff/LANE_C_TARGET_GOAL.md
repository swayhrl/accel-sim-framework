# EP-L2 Codex Target Goal — Lane C L1 Causality

## One-line goal

> Starting from the exact C7e D256 B0-Banked baseline, autonomously complete the selected-workload L1 META-HR and BANK-HR causality screen, self-repair all authorized config/instrumentation/tooling issues until Lane C acceptance passes, consume Lane B's exact D512_READY definition when available for the D512 interaction cells, decompose any materially sensitive META-HR result one resource at a time, produce a causal classification pack, update the shared workboard, then STOP before changing the primary L1 baseline or implementing EP-L2 mechanisms.

## Read order

From `/workspace/worktrees/accel-sim-ep-l2/` fetch/pull latest `hrl/ep-l2-exp-v0`, then read:

```text
docs/ep_l2/chatgpt_handoff/CURRENT_STATE.md
docs/ep_l2/chatgpt_handoff/INTERIM_22OF26_CHATGPT_REVIEW.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
docs/ep_l2/chatgpt_handoff/PARALLEL_MASTER_PLAN.md
docs/ep_l2/chatgpt_handoff/PARALLEL_NEW_WINDOW_BOOTSTRAP.md
docs/ep_l2/chatgpt_handoff/LANE_C_L1_CAUSALITY_HANDOFF.md
docs/ep_l2/chatgpt_handoff/LANE_C_L1_CAUSALITY_ACCEPTANCE_CRITERIA.md
```

## Start immediately

Do not wait for Lane A 26/26 or Lane B D512 to finish before starting the D256 cells.

Immediately execute:

```text
D256 + L1 META-HR: 7 selected workloads, B0-Banked
D256 + L1 BANK-HR: 7 selected workloads, B0-Banked
```

When workboard `D512-PREFLIGHT` becomes DONE/PASS, consume Lane B's exact D512_READY source/config and continue with D512 interaction cells.

## Target-mode behavior

If a build, config-delta audit, parser test, counter test, or run fails, repair and continue within the Lane C boundaries.

Allowed autonomous work:

```text
isolated L1 sensitivity config overlays
runner/provenance plumbing
L1 observation-only telemetry fixes when required
parser/analyzer/tests/review packaging
one-at-a-time decomposition for sensitive META-HR cases
```

Hard boundaries are defined in the acceptance file. Never modify Lane A/B active runtime worktrees.

## Completion condition

Complete only when:

```text
L1_CAUSALITY_SCREEN_COMPLETE
```

is supported by the acceptance criteria and the workboard/review pack contain exact evidence paths.

## Required outputs

Mirror documentation-only outputs to coordination branch:

```text
docs/ep_l2/codex_handoff/LANE_C_LATEST.md
docs/ep_l2/review_packs/L1_CAUSALITY_CALIBRATION_r1/
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Then STOP. Do not decide D256 vs D512 or change the primary L1 configuration; those belong to convergence/BASELINE-DECISION.
