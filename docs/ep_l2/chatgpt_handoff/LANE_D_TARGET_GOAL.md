# EP-L2 Codex Target Goal — Lane D Analysis / Cost / Opportunity Prep

## One-line goal

> While simulation lanes run, autonomously complete the temporal-cardinality audit and robust 5K-window analysis, build a provenance-safe joint D256/D512 × L1 calibration analyzer, quantify descriptor-512 hardware metadata cost, optionally prepare only disabled-by-default timing-neutral opportunity-study scaffolding, continuously ingest completed Lane A/B/C outputs, update the shared workboard and Lane-D report, and STOP before making the baseline decision or implementing functional RO/TVD/Unified mechanisms.

## Read order

From `/workspace/worktrees/accel-sim-ep-l2/` fetch/pull latest `hrl/ep-l2-exp-v0`, then read:

```text
docs/ep_l2/chatgpt_handoff/CURRENT_STATE.md
docs/ep_l2/chatgpt_handoff/INTERIM_22OF26_CHATGPT_REVIEW.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
docs/ep_l2/chatgpt_handoff/PARALLEL_MASTER_PLAN.md
docs/ep_l2/chatgpt_handoff/PARALLEL_NEW_WINDOW_BOOTSTRAP.md
docs/ep_l2/chatgpt_handoff/LANE_D_ANALYSIS_INFRA_HANDOFF.md
docs/ep_l2/chatgpt_handoff/LANE_D_ANALYSIS_INFRA_ACCEPTANCE_CRITERIA.md
```

## Start immediately

Do not wait for Lane A/B/C completion.

Begin with the currently available 22/26 formal data:

```text
temporal stream cardinality audit
temporal distribution analysis
joint analyzer infrastructure
descriptor hardware-cost methodology
```

Refresh the same analysis as new lane outputs become DONE in the workboard.

## Target-mode behavior

Self-repair analysis/tooling/fixture/provenance issues until the Lane D acceptance criteria pass.

Allowed autonomous work:

```text
Framework analysis scripts/tests/docs
schema/provenance validation
review-pack generation
hardware metadata cost modeling with explicit assumptions
optional isolated disabled-by-default shadow bookkeeping scaffold
```

Do not modify Lane A/B/C active runtime roots. Do not invent missing telemetry and do not implement functional mechanisms.

## Completion condition

Required convergence milestones:

```text
TEMPORAL_ANALYSIS_READY
CALIBRATION_ANALYZER_READY
D512_COST_READY
```

Optional:

```text
OPPORTUNITY_SCAFFOLD_READY
```

only if the strict scaffold correctness/timing-neutrality gate passes.

## Required outputs

Mirror documentation-only outputs to coordination branch:

```text
docs/ep_l2/codex_handoff/LANE_D_LATEST.md
docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1/
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Keep source on the Lane D branch(es).

Then remain available to refresh CAL-ANALYSIS as Lane A/B/C data arrive, but do not independently freeze the primary baseline. `BASELINE-DECISION` requires combined review.
