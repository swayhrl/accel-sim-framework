# EP-L2 New Codex Window Bootstrap

Status: authoritative bootstrap for new Lane B/C/D/E Codex windows.

## 1. Existing local topology

```text
Coordination / handoff / review-pack worktree
/workspace/worktrees/accel-sim-ep-l2/
  branch: hrl/ep-l2-exp-v0

Frozen Lane-A formal Framework worktree
/workspace/worktrees/accel-sim-ep-l2-c7e/

Frozen Lane-A formal Core/config worktree
/workspace/worktrees/gpgpu-sim-ep-l2-c7e/
```

Formal runtime pair:

```text
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
```

Lane A is complete and independently reviewed PASS. The two formal worktrees remain immutable/read-only anchors for all calibration lanes. Never rebuild, clean, reset, checkout another branch, edit files, or write calibration results into them.

The coordination worktree is for handoff/workboard/review documentation only; do not use it as a simulator source worktree.

## 2. First actions in every new Codex window

Before implementation or simulator launch:

1. `cd /workspace/worktrees/accel-sim-ep-l2/`.
2. Fetch/pull latest `hrl/ep-l2-exp-v0` without overwriting user work.
3. Read:

```text
docs/ep_l2/chatgpt_handoff/CURRENT_STATE.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
docs/ep_l2/chatgpt_handoff/PARALLEL_MASTER_PLAN.md
docs/ep_l2/chatgpt_handoff/SPECULATIVE_PARALLEL_EXECUTION_POLICY.md
docs/ep_l2/chatgpt_handoff/PARALLEL_NEW_WINDOW_BOOTSTRAP.md
```

4. Verify formal anchors without modifying them:

```text
git -C /workspace/worktrees/accel-sim-ep-l2-c7e rev-parse HEAD
git -C /workspace/worktrees/gpgpu-sim-ep-l2-c7e rev-parse HEAD
```

5. Read the lane-specific HANDOFF + ACCEPTANCE_CRITERIA + TARGET_GOAL.
6. Create lane-specific worktrees/branches/config overlays/result roots/manifests.

If a required source identity differs from the handoff, record the mismatch and stop before launching affected runs.

## 3. Recommended lane worktrees

### Lane B

```text
Framework /workspace/worktrees/accel-sim-ep-l2-d512/
Core      /workspace/worktrees/gpgpu-sim-ep-l2-d512/
branch    hrl/ep-l2-d512-cal-v0
```

### Lane C

```text
Framework /workspace/worktrees/accel-sim-ep-l2-l1-causality/
Core      /workspace/worktrees/gpgpu-sim-ep-l2-l1-causality/
branch    hrl/ep-l2-l1-causality-v0
```

### Lane D

```text
Framework /workspace/worktrees/accel-sim-ep-l2-cal-analysis/
branch    hrl/ep-l2-cal-analysis-v0
```

### Lane E

```text
Framework /workspace/worktrees/accel-sim-ep-l2-mshr-causality/
Core      /workspace/worktrees/gpgpu-sim-ep-l2-mshr-causality/
branch    hrl/ep-l2-mshr-causality-v0
results   /workspace/results/ep_l2_line_mshr_causality/
```

## 4. Source-base rules

Lane B descriptor calibration derives from the exact formal source pair.

Lane C D256 work derives from the exact formal source; D512 descendants consume the exact frozen Lane-B D512 candidate.

Lane E consumes the exact frozen Lane-B D512 candidate as its source parent because it requires the already-reviewed Descriptor-512 telemetry generalization, while retaining the formal D256 pair as the semantic reference.

Current Lane-B candidate:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

Do not recreate equivalent source under a different semantic definition.

## 5. Isolation / concurrency

One Codex window owns one lane, not one simulator process. A lane may run multiple processes if each has:

```text
unique result directory
immutable source/config/trace identity
per-run status/manifest
no shared mutable output
no shared rebuild while runs are active
```

Never run two variants into one output directory.

## 6. Shared workboard protocol

Before every workboard update:

1. fetch/pull latest coordination branch;
2. preserve every other lane and ChatGPT field;
3. update only owned execution/progress/evidence cells;
4. use scoped Git adds/commits;
5. push promptly after meaningful transitions.

Codex must not overwrite ChatGPT PASS/FAIL conclusions.

## 7. Parallel report files

```text
Lane A: docs/ep_l2/codex_handoff/LATEST_REPORT.md
Lane B: docs/ep_l2/codex_handoff/LANE_B_LATEST.md
Lane C: docs/ep_l2/codex_handoff/LANE_C_LATEST.md
Lane D: docs/ep_l2/codex_handoff/LANE_D_LATEST.md
Lane E: docs/ep_l2/codex_handoff/LANE_E_LATEST.md
```

Experimental source stays on lane branches; documentation/review packs are mirrored to `hrl/ep-l2-exp-v0`.

## 8. Universal implementation-correctness gate

Any lane that changes simulator code, telemetry, parser/schema, or configuration plumbing must provide at minimum:

```text
source semantic map
Release build
relevant directed regression
natural-workload smoke
parser/analyzer regression if output changes
terminal invariants/no resource leak
exact authorized config diff
git diff --check
clean source worktree at frozen experiment SHA
```

Observation-only/generalization changes additionally require original-capacity timing/behavior equivalence on representative natural workloads.

Capacity experiments do not require equality between capacities; supporting code must first reproduce the original capacity exactly.

## 9. Universal hard stops

Stop and request review if completion would require:

```text
changing a variable outside the lane's authorized delta
changing traces/workloads to obtain a desired result
weakening/changing invariant meaning
accepting unexplained equivalence/timing mismatch
editing another lane's runtime worktree/results
promoting calibration data to the primary baseline without BASELINE-DECISION
```
