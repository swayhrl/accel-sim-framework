# EP-L2 Motivation Figures — Target Goal

Mode: **Codex target/autonomous execution**

## Target

Starting from the current Motivation lane state, autonomously complete the entire remaining Motivation Figures pipeline:

```text
FINAL PREFLIGHT
-> BROAD 10-WORKLOAD CAMPAIGN
-> AGGREGATION / FIGURES / FINAL REVIEW PACK
-> MOTIVATION_FIGURES_REVIEW_READY
```

Do not stop for ordinary intermediate success. Continue automatically when each mandatory stage gate passes.

Use as authoritative execution contracts:

```text
docs/ep_l2/chatgpt_handoff/MOTIVATION_FINAL_PIPELINE_HANDOFF.md
docs/ep_l2/chatgpt_handoff/MOTIVATION_FINAL_PIPELINE_ACCEPTANCE_CRITERIA.md
```

Also preserve all frozen semantics in:

```text
docs/ep_l2/project_spec/MOTIVATION_FIGURES_PLAN.md
docs/ep_l2/project_spec/decisions/ADR-009-motivation-wbuf-shadow-definition.md
```

## Current candidate entering the goal

```text
Core
2a6a31591bc42023e5997cca969e4b672efe0405

Framework
02f36816f60afcff55e910cdef2b60937e691cdc

Branch
hrl/ep-l2-motivation-v0
```

Continue in:

```text
Framework worktree
/workspace/worktrees/accel-sim-ep-l2-motivation/

Core worktree
/workspace/worktrees/gpgpu-sim-ep-l2-motivation/

Result root
/workspace/results/ep_l2_motivation/
```

## Autonomous execution behavior

1. Finish the exact-provenance final preflight pilots and all required neutrality/parser/invariant checks.
2. If Stage-4 gates pass, freeze the candidate and immediately launch the broad ten-workload Motivation-ON campaign in parallel where safe.
3. Do not wait for `scan` before launching independent broad workloads.
4. Continue parsing/validating/compressing completed short rows while long rows run.
5. After all ten broad rows are `COMPLETE_VALID`, aggregate them into one provenance-bound machine-readable dataset.
6. Generate the two primary paper-facing figures and the WBUF sensitivity figure from those committed tables.
7. Generate the final findings, validation evidence, manifests and checksums.
8. Push the final review pack and handoff.
9. Stop only at:

```text
MOTIVATION_FIGURES_REVIEW_READY
```

and request independent ChatGPT review.

## Self-repair policy

If a mandatory gate fails:

- diagnose root cause before patching;
- repair autonomously when the failure is within Motivation observation-only instrumentation, parser, runner, analysis or plotting scope;
- preserve the failed result as diagnostic evidence;
- if Core/Framework runtime semantics or source changes, create a new frozen candidate and invalidate/rerun all formal evidence required by the handoff;
- parser/plot-only fixes may reuse raw logs only when provenance and semantic completeness are provable;
- never silently omit, substitute, renormalize away, or reinterpret a failing workload/category.

If the blocker requires a new architecture/research-policy decision outside this authorized scope, stop and report the exact blocker instead of guessing.

## Required final publication

Push:

```text
docs/ep_l2/review_packs/MOTIVATION_FIGURES_r1/
docs/ep_l2/codex_handoff/LANE_MOTIVATION_LATEST.md
```

The final handoff must report:

```text
Stage 4: MOTIVATION_INSTRUMENTATION_PREFLIGHT_PASS
Stage 5: MOTIVATION_BROAD_10OF10_PASS
Stage 6: MOTIVATION_FIGURES_REVIEW_READY
```

with exact final Core/Framework/runtime provenance and evidence paths.

Do not self-declare `MOTIVATION_FIGURES_FINAL_PASS`; that is assigned only after ChatGPT independently reviews the final pack.
