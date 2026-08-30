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

## Parallel calibration lanes — new Codex windows

Shared status board:

```text
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Every new Lane B/C/D window begins from the coordination worktree:

```text
/workspace/worktrees/accel-sim-ep-l2/
```

and first reads:

```text
CURRENT_STATE.md
INTERIM_22OF26_CHATGPT_REVIEW.md
../coordination/PARALLEL_WORKBOARD.md
PARALLEL_MASTER_PLAN.md
PARALLEL_NEW_WINDOW_BOOTSTRAP.md
```

Then read one complete lane contract:

### Window B — Descriptor 512

```text
LANE_B_DESCRIPTOR512_HANDOFF.md
LANE_B_DESCRIPTOR512_ACCEPTANCE_CRITERIA.md
LANE_B_TARGET_GOAL.md
```

### Window C — L1 causality

```text
LANE_C_L1_CAUSALITY_HANDOFF.md
LANE_C_L1_CAUSALITY_ACCEPTANCE_CRITERIA.md
LANE_C_TARGET_GOAL.md
```

### Window D — analysis / cost / opportunity prep

```text
LANE_D_ANALYSIS_INFRA_HANDOFF.md
LANE_D_ANALYSIS_INFRA_ACCEPTANCE_CRITERIA.md
LANE_D_TARGET_GOAL.md
```

`*_HANDOFF.md` defines the detailed scientific/experimental task.

`*_ACCEPTANCE_CRITERIA.md` defines the mandatory implementation-correctness, validation, self-repair and completion gates.

`*_TARGET_GOAL.md` is the Codex goal-mode entry point.

Recommended concurrency is **4 Codex windows total**: the existing Lane A window plus 3 new B/C/D windows. Each lane may launch multiple simulator processes internally; do not create a Codex window per simulator run.

## Existing local formal anchors

The new-window bootstrap records the current topology:

```text
Coordination / handoff:
/workspace/worktrees/accel-sim-ep-l2/
  hrl/ep-l2-exp-v0

Lane A C7e Framework — read-only to B/C/D:
/workspace/worktrees/accel-sim-ep-l2-c7e/
  hrl/ep-l2-c7e-final-char-v0

Lane A C7e Core/config — read-only to B/C/D:
/workspace/worktrees/gpgpu-sim-ep-l2-c7e/
  hrl/ep-l2-c7e-final-char-v0
```

B/C/D must create independent worktrees and never rebuild/edit the two Lane A formal worktrees.

## File roles

`CURRENT_STATE.md` records reviewed architecture/research state.

`*_DISCUSSION_REFERENCE.md` records source-audited rationale.

`*_HANDOFF.md` files define executable scopes and hard boundaries.

`*_ACCEPTANCE_CRITERIA.md` files define exact PASS conditions and implementation/counter correctness tests.

`*_TARGET_GOAL.md` files define autonomous target-mode loops.

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
docs/ep_l2/review_packs/L1_CAUSALITY_CALIBRATION_r1/
docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1/
```

Calibration data is not automatically formal. The shared convergence gate is `BASELINE-DECISION` in `PARALLEL_WORKBOARD.md`.
