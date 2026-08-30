# EP-L2 New Codex Window Bootstrap

Status: authoritative bootstrap for new Lane B/C/D Codex windows.

## 1. Existing local topology — treat as authoritative until superseded

```text
Coordination / handoff / review-pack worktree
/workspace/worktrees/accel-sim-ep-l2/
  branch: hrl/ep-l2-exp-v0

Lane A current C7e formal Framework worktree
/workspace/worktrees/accel-sim-ep-l2-c7e/
  branch: hrl/ep-l2-c7e-final-char-v0

Lane A current C7e Core/config worktree
/workspace/worktrees/gpgpu-sim-ep-l2-c7e/
  branch: hrl/ep-l2-c7e-final-char-v0
```

The two C7e formal worktrees are **read-only anchors for Lane B/C/D** while Lane A is active. Never rebuild, clean, reset, checkout another branch, edit files, or write calibration results into them.

The coordination worktree is for reading/updating handoff/workboard/review documentation. Do not use it as the simulator source worktree for Lane B/C/D code experiments.

## 2. First actions in every new Codex window

Before implementation or launching any simulator process:

1. `cd /workspace/worktrees/accel-sim-ep-l2/`.
2. Fetch/pull the latest `hrl/ep-l2-exp-v0` without overwriting local user work.
3. Read the common context in this exact order:

```text
docs/ep_l2/chatgpt_handoff/CURRENT_STATE.md
docs/ep_l2/chatgpt_handoff/INTERIM_22OF26_CHATGPT_REVIEW.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
docs/ep_l2/chatgpt_handoff/PARALLEL_MASTER_PLAN.md
docs/ep_l2/chatgpt_handoff/PARALLEL_NEW_WINDOW_BOOTSTRAP.md
```

4. Verify the current formal C7e anchors without modifying them:

```text
git -C /workspace/worktrees/accel-sim-ep-l2-c7e rev-parse HEAD
git -C /workspace/worktrees/gpgpu-sim-ep-l2-c7e rev-parse HEAD
```

Expected current formal pair from the 22/26 manifest:

```text
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
```

If the local tips differ, do not guess which source is authoritative. Record the mismatch in the workboard and stop before launching calibration runs.

5. Read the lane-specific `HANDOFF`, `ACCEPTANCE_CRITERIA`, and `TARGET_GOAL` files.
6. Create lane-specific worktree(s), branch(es), config overlays, result root(s), and manifests. Do not reuse the Lane A paths above.

## 3. Recommended lane worktrees

These names are recommended to reduce accidental cross-lane writes; Codex may choose equivalent isolated names if a path already exists, but must record the actual paths in the workboard.

### Lane B

```text
Framework: /workspace/worktrees/accel-sim-ep-l2-d512/
Core:      /workspace/worktrees/gpgpu-sim-ep-l2-d512/
branches:  hrl/ep-l2-d512-cal-v0
```

### Lane C

```text
Framework: /workspace/worktrees/accel-sim-ep-l2-l1-causality/
Core:      /workspace/worktrees/gpgpu-sim-ep-l2-l1-causality/
branches:  hrl/ep-l2-l1-causality-v0
```

### Lane D

Primary Framework analysis worktree:

```text
/workspace/worktrees/accel-sim-ep-l2-cal-analysis/
branch: hrl/ep-l2-cal-analysis-v0
```

Optional Core opportunity-scaffold worktree, only if needed and only after the Lane D handoff permits it:

```text
/workspace/worktrees/gpgpu-sim-ep-l2-opportunity-scaffold/
branch: hrl/ep-l2-opportunity-scaffold-v0
```

## 4. Source-base rule

Lane B/C calibration code/config must derive from the **exact C7e formal source pair**, not from the coordination branch and not from an older C7d branch.

If the exact formal commits are not yet remotely published, Lane B/C may inspect the read-only local C7e worktrees and prepare their own worktrees from the exact local commits, but they must not rewrite or rebuild the Lane A worktrees. Remote publication of the exact formal commits remains a required provenance action.

## 5. Isolation and concurrency

A Codex window owns one lane, not one simulator process. A lane may launch multiple simulator processes if its runner has:

```text
unique result directories
immutable config/trace/source identity
per-run status/manifest
no shared mutable output files
no shared rebuild step during active runs
```

Do not run two variants into the same output directory.

## 6. Shared workboard protocol

Shared file:

```text
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Before every update:

1. fetch/pull latest coordination branch;
2. preserve every row/field owned by other lanes and ChatGPT;
3. modify only your lane's execution/progress/evidence cells;
4. use explicit scoped Git adds/commits;
5. push promptly after a meaningful transition such as PREP -> RUNNING or RUNNING -> DONE.

Codex must never replace a previous ChatGPT PASS/FAIL conclusion. Add new evidence and let ChatGPT update review fields.

## 7. Parallel report files

Do not overwrite Lane A global report while it owns the formal campaign.

```text
Lane A: docs/ep_l2/codex_handoff/LATEST_REPORT.md
Lane B: docs/ep_l2/codex_handoff/LANE_B_LATEST.md
Lane C: docs/ep_l2/codex_handoff/LANE_C_LATEST.md
Lane D: docs/ep_l2/codex_handoff/LANE_D_LATEST.md
```

Mirror documentation-only reports/review packs to `hrl/ep-l2-exp-v0`; keep experimental source on the lane branch.

## 8. Universal implementation-correctness rule

If a lane adds or changes simulator code, telemetry, counters, parser fields, or configuration plumbing, it must not rely on source inspection alone. At minimum require:

```text
source semantic map: event -> exact production point -> field
Release build
relevant directed regression
natural-workload smoke
parser/analyzer regression if output changes
terminal resource/invariant check
no unexpected source/config delta outside lane scope
git diff --check
clean source worktree at frozen experiment SHA
```

For observation-only instrumentation/generalization, additionally require an exact OFF/ON or old/new-base timing-equivalence check on representative natural workload(s). Compare simulated cycles and selected functional/native counters exactly; host wall-time may differ.

For capacity/config experiments, do not demand timing equality between the two capacity settings—the difference is the experiment—but first prove that any supporting code generalization configured back to the original capacity reproduces the original formal behavior exactly.

## 9. Universal hard stops

Stop the lane and request review rather than self-justifying a result if completion would require:

```text
changing a variable outside the lane's authorized experimental delta
changing trace/workload inputs to obtain a desired result
changing invariant meaning
accepting unexplained D256-equivalence or instrumentation timing mismatch
editing/rebuilding Lane A formal worktrees during active runs
promoting calibration data to primary formal data without BASELINE-DECISION
```
