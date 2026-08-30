# ChatGPT -> Codex Handoff

Ownership: ChatGPT.

Permanent coordination branch:

```text
hrl/ep-l2-exp-v0
```

## Lane A — current formal target mode

The existing Codex target-mode window owns Lane A only. Read:

```text
CURRENT_STATE.md
C7E_DISCUSSION_REFERENCE.md
C7E_IMPLEMENTATION_HANDOFF.md
C7E_ACCEPTANCE_CRITERIA.md
FINAL_26RUN_HANDOFF.md
FINAL_26RUN_ACCEPTANCE_CRITERIA.md
CODEX_TARGET_GOAL.md
CODEX_NEXT_STAGE.md
INTERIM_22OF26_CHATGPT_REVIEW.md
```

Do not expand this live formal window to own calibration lanes B-D.

## Parallel calibration lanes

The shared plan/progress board is:

```text
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

New Codex windows should first read:

```text
CURRENT_STATE.md
INTERIM_22OF26_CHATGPT_REVIEW.md
PARALLEL_MASTER_PLAN.md
../coordination/PARALLEL_WORKBOARD.md
```

Then read exactly one lane-specific handoff:

```text
Window B -> LANE_B_DESCRIPTOR512_HANDOFF.md
Window C -> LANE_C_L1_CAUSALITY_HANDOFF.md
Window D -> LANE_D_ANALYSIS_INFRA_HANDOFF.md
```

Recommended concurrency is **4 Codex windows total**: the existing Lane A window plus 3 new B/C/D windows. Each lane may launch multiple simulator processes internally; do not create a Codex window per simulator run.

## File roles

`CURRENT_STATE.md` records reviewed architecture/research state.

`*_DISCUSSION_REFERENCE.md` records source-audited rationale.

`*_HANDOFF.md` files define executable scopes and hard boundaries.

`PARALLEL_MASTER_PLAN.md` defines lane ownership, dependency handshakes, and concurrency rules.

Codex must not modify ChatGPT-owned handoff files unless explicitly instructed.

## Codex -> ChatGPT return path

Source is pushed on lane/stage implementation branches. Documentation-only status/review packs are mirrored to the coordination branch.

During parallel execution use dedicated reports to avoid write collisions:

```text
docs/ep_l2/codex_handoff/LATEST_REPORT.md       # Lane A/global formal owner
docs/ep_l2/codex_handoff/LANE_B_LATEST.md
docs/ep_l2/codex_handoff/LANE_C_LATEST.md
docs/ep_l2/codex_handoff/LANE_D_LATEST.md
```

Expected review-pack families include:

```text
docs/ep_l2/review_packs/C7E_FINAL_READINESS_r1/
docs/ep_l2/review_packs/FINAL_TARGET_BASELINE_850_r1/
docs/ep_l2/review_packs/D512_CALIBRATION_r1/
docs/ep_l2/review_packs/L1_CAUSALITY_r1/
docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1/
```

Calibration data is not automatically formal. The shared convergence gate is `BASELINE-DECISION` in `PARALLEL_WORKBOARD.md`.