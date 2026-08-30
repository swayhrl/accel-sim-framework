# ChatGPT -> Codex Handoff

Ownership: ChatGPT.

Permanent coordination branch:

```text
hrl/ep-l2-exp-v0
```

## Canonical long-lived project specification

Before interpreting any lane-specific task as the overall project goal, read:

```text
docs/ep_l2/project_spec/README.md
docs/ep_l2/project_spec/RESEARCH_CHARTER.md
docs/ep_l2/project_spec/ARCHITECTURE_BLUEPRINT.md
docs/ep_l2/project_spec/EVIDENCE_AND_CLAIM_MODEL.md
docs/ep_l2/project_spec/WORKLOAD_CHARACTERIZATION_SCHEMA.md
docs/ep_l2/project_spec/WORKLOAD_ARCHETYPES_PRELIMINARY.md
docs/ep_l2/project_spec/MECHANISM_IMPLEMENTATION_PLAN.md
docs/ep_l2/project_spec/EXPERIMENT_ROADMAP.md
```

The project specification records the stable research objective, architecture thesis, claim standard, workload classification contract, implementation plan, and long-term roadmap. `chatgpt_handoff/` records only the currently authorized executable stage.

Current key objective:

> Under comparable L2 storage budget and basic L2 timing, improve the L2's ability to sustain concurrent misses, pending transactions, and payload state while reducing structural blocking caused by static resource/lifetime coupling. End-to-end speedup is stronger evidence, but is not the only valid evidence of a better L2 when another subsystem becomes the new bottleneck.

Performance-headroom policy lives in:

```text
docs/ep_l2/project_spec/PERFORMANCE_HEADROOM_PLAN.md
```

## Shared status board

```text
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

All active/new windows start from the coordination worktree:

```text
/workspace/worktrees/accel-sim-ep-l2/
```

and read:

```text
CURRENT_STATE.md
../coordination/PARALLEL_WORKBOARD.md
PARALLEL_MASTER_PLAN.md
SPECULATIVE_PARALLEL_EXECUTION_POLICY.md
PARALLEL_NEW_WINDOW_BOOTSTRAP.md
```

Then read the lane-specific `HANDOFF + ACCEPTANCE_CRITERIA + TARGET_GOAL` and any latest ChatGPT review/fanout file named by that target.

## Lane ownership

### Lane A — formal D256 Target Baseline

Lane A is frozen/closed after the reviewed 26/26 formal campaign. Its formal runtime worktrees are read-only anchors.

### Lane B — Descriptor 512 calibration

Lane B is complete at `D512_READY + D512_MIRROR_COMPLETE`.

### Lane C — L1 causality

Lane C is complete at `L1_CAUSALITY_SCREEN_COMPLETE`.

### Lane D — final calibration convergence

Current authorized target:

```text
FINAL_CALIBRATION_CONVERGENCE_HANDOFF.md
FINAL_CALIBRATION_CONVERGENCE_ACCEPTANCE_CRITERIA.md
LANE_D_FINAL_CONVERGENCE_TARGET_GOAL.md
```

Lane D must first publish a 13-workload archetype checkpoint, then finish the six-cell calibration convergence and baseline/mechanism-priority recommendation. No new simulator run is authorized in this stage.

### Lane E — Line-MSHR causality

Lane E is complete at `LINE_MSHR_CAUSALITY_PROBE_COMPLETE` and is supplemental controlled sensitivity evidence.

### Lane F — mechanism implementation preparation

Current authorized parallel source/design audit:

```text
LANE_F_MECHANISM_PREP_HANDOFF.md
LANE_F_MECHANISM_PREP_ACCEPTANCE_CRITERIA.md
LANE_F_TARGET_GOAL.md
```

Lane F converts the architecture roadmap into exact M0/M1/M2 source/state-machine modification plans. It may inspect source deeply but must not push a functional mechanism implementation yet.

One Codex window owns one scientific lane, not one simulator process. A lane may launch multiple processes internally only with isolated result directories and frozen source/config identities.

## Existing formal anchors

```text
Coordination / handoff:
/workspace/worktrees/accel-sim-ep-l2/
  hrl/ep-l2-exp-v0

Frozen C7e Framework:
/workspace/worktrees/accel-sim-ep-l2-c7e/
  hrl/ep-l2-c7e-final-char-v0

Frozen C7e Core/config:
/workspace/worktrees/gpgpu-sim-ep-l2-c7e/
  hrl/ep-l2-c7e-final-char-v0
```

Other lanes must never rebuild/edit/reuse these result roots as experimental workspaces.

## File roles

```text
project_spec/             long-lived goals/architecture/evidence/roadmap
chatgpt_handoff/          current ChatGPT-owned executable specifications
codex_handoff/            Codex-owned execution reports
review_packs/             Codex-generated independently reviewable evidence
coordination/workboard    shared execution/review state
```

Codex must not modify ChatGPT-owned `project_spec/` or `chatgpt_handoff/` files unless explicitly instructed.

## Codex -> ChatGPT return path

During parallel execution use dedicated reports to avoid collisions:

```text
docs/ep_l2/codex_handoff/LATEST_REPORT.md
docs/ep_l2/codex_handoff/LANE_B_LATEST.md
docs/ep_l2/codex_handoff/LANE_C_LATEST.md
docs/ep_l2/codex_handoff/LANE_D_LATEST.md
docs/ep_l2/codex_handoff/LANE_E_LATEST.md
docs/ep_l2/codex_handoff/LANE_F_LATEST.md
```

Calibration data is never silently promoted to the primary formal baseline. `BASELINE-DECISION` remains a reviewed convergence gate.
