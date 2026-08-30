# EP-L2 Motivation Lane — Codex Target Goal

Status: **AUTONOMOUS TARGET MODE**

## Goal

Autonomously build, validate and run the timing-neutral motivation instrumentation required to produce the two primary EP-L2 motivation figures:

```text
Figure 1: L2 Reuse-Distance Distribution
Figure 2: L2 Miss-Admission Structural Blocking Breakdown
```

with simultaneous WBUF shadow sensitivity:

```text
C = 4 / 8 / 16
```

Continue until:

```text
MOTIVATION_FIGURES_REVIEW_READY
```

is fully supported by `MOTIVATION_INSTRUMENTATION_ACCEPTANCE_CRITERIA.md`.

## Authoritative contracts

Read and obey:

```text
docs/ep_l2/project_spec/MOTIVATION_FIGURES_PLAN.md
docs/ep_l2/project_spec/decisions/ADR-009-motivation-wbuf-shadow-definition.md
docs/ep_l2/chatgpt_handoff/MOTIVATION_INSTRUMENTATION_HANDOFF.md
docs/ep_l2/chatgpt_handoff/MOTIVATION_INSTRUMENTATION_ACCEPTANCE_CRITERIA.md
```

## Parent

```text
Core:
1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e

Framework runtime:
d61ffd23c926a25fa463a3e6e955c885b45f0f8a
```

## Isolation

Use only:

```text
Framework worktree:
/workspace/worktrees/accel-sim-ep-l2-motivation/

Core worktree:
/workspace/worktrees/gpgpu-sim-ep-l2-motivation/

branch:
hrl/ep-l2-motivation-v0

results:
/workspace/results/ep_l2_motivation/
```

Do not modify any active M0b, M3A, M0a, M1 or coordination simulator worktree/result root.

## Self-repair authority

If any build, directed test, parser test, timing-neutrality control, primary-accounting invariant, workload run or figure-normalization gate fails, diagnose and repair within this lane's authorized observation-only instrumentation/parser/runner/plotting scope and continue.

Do not stop merely because an intermediate test fails.

Stop early only if fixing the issue requires changing accepted baseline architecture semantics or functional request behavior.

## Execution priorities

1. Freeze source map and exact admission order.
2. Implement motivation telemetry default OFF.
3. Prove reuse-distance exactness through >1K bucket.
4. Prove WBUF creation->lower-accept lifecycle and 4/8/16 simultaneous shadow behavior.
5. Prove exclusive primary-block accounting.
6. Prove OFF/ON timing neutrality.
7. Complete the four pilots.
8. Launch broad workload set in parallel; do not serially wait for scan.
9. Generate deterministic CSVs and figure previews.
10. Build complete review pack and push.

## Deliverables

Update:

```text
docs/ep_l2/codex_handoff/LANE_MOTIVATION_LATEST.md
```

Create:

```text
docs/ep_l2/review_packs/MOTIVATION_FIGURES_r1/
```

Push exact source branches and documentation evidence.

## Stop condition

After reporting:

```text
MOTIVATION_FIGURES_REVIEW_READY
```

STOP for ChatGPT review.