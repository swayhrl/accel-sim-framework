# EP-L2 Codex Target Goal — Lane D Final Calibration Convergence

## One-line goal

> Consume only promoted/reviewed D256/D512/L1 calibration evidence plus the completed Line-MSHR causal supplement, produce an immediate 13-workload archetype checkpoint and then a provenance-safe final calibration convergence pack that recommends the calibrated research baseline and first EP-L2 mechanism targets without launching new simulations or implementing any mechanism.

## Start location

```text
/workspace/worktrees/accel-sim-ep-l2/
branch hrl/ep-l2-exp-v0
```

Fetch/pull latest before reading or updating shared files.

## Required read order

```text
docs/ep_l2/project_spec/README.md
docs/ep_l2/project_spec/RESEARCH_CHARTER.md
docs/ep_l2/project_spec/ARCHITECTURE_BLUEPRINT.md
docs/ep_l2/project_spec/EVIDENCE_AND_CLAIM_MODEL.md
docs/ep_l2/project_spec/EXPERIMENT_ROADMAP.md
docs/ep_l2/project_spec/PERFORMANCE_HEADROOM_PLAN.md
docs/ep_l2/project_spec/WORKLOAD_CHARACTERIZATION_SCHEMA.md
docs/ep_l2/project_spec/MECHANISM_IMPLEMENTATION_PLAN.md

docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
docs/ep_l2/codex_handoff/LANE_B_LATEST.md
docs/ep_l2/codex_handoff/LANE_C_LATEST.md
docs/ep_l2/codex_handoff/LANE_E_LATEST.md

docs/ep_l2/chatgpt_handoff/LANE_D_CHATGPT_FINAL_REVIEW.md
docs/ep_l2/chatgpt_handoff/FINAL_CALIBRATION_CONVERGENCE_HANDOFF.md
docs/ep_l2/chatgpt_handoff/FINAL_CALIBRATION_CONVERGENCE_ACCEPTANCE_CRITERIA.md
```

Treat the handoff and acceptance criteria as the mandatory autonomous target contract.

## Source/worktree rule

Use the existing isolated Lane-D analysis worktree/source as the starting point:

```text
/workspace/worktrees/accel-sim-ep-l2-cal-analysis/
branch hrl/ep-l2-cal-analysis-v0
reviewed Lane-D V3 source cb83606eb8640382b7c1932d8981b70608d9d130
```

If the local path differs, record the exact path/SHA. Do not use any active simulator worktree as the analysis source.

## Execute now

### Phase 1 — workload archetype checkpoint first

Before writing the full final convergence narrative, produce all-13 workload characterization files required by the handoff.

Use measured data first. Label unsupported mechanism-specific properties as `UNKNOWN_NEEDS_TELEMETRY`.

This phase is intended to expose the first implementation targets quickly; do not wait for the rest of the report to begin it.

### Phase 2 — final calibration matrix

Consume only the six promoted V2-contract cells:

```text
D256_BASE
D512_BASE
D256_META_HR
D256_BANK_HR
D512_META_HR
D512_BANK_HR
```

Validate all runtime config hashes, source lineage/equivalence, trace/frequency identity and allowed config deltas before computing comparisons.

### Phase 3 — Line-MSHR supplement

Integrate the completed Lane-E convolution 2x2 and spmv negative control as supplemental controlled sensitivity evidence.

### Phase 4 — recommendation

Produce:

```text
BASELINE_DECISION_EVIDENCE.md
MECHANISM_PRIORITY_RECOMMENDATION.md
PERFORMANCE_HEADROOM_CANDIDATES.md
```

Recommend, but do not enact, a primary baseline choice.

## No simulator work

Do not launch `accel-sim.out`, do not rebuild Lane A/B/C/E binaries, and do not run 1GHz/headroom simulations in this stage.

## Required completion

Publish:

```text
docs/ep_l2/review_packs/FINAL_CALIBRATION_CONVERGENCE_r1/
docs/ep_l2/codex_handoff/LANE_D_LATEST.md
```

with status:

```text
FINAL_CALIBRATION_CONVERGENCE_REVIEW_READY
```

Push documentation/analysis-only changes, update only Lane-D execution/progress/evidence fields in the shared workboard, preserve ChatGPT review fields, then STOP and request ChatGPT independent review.
