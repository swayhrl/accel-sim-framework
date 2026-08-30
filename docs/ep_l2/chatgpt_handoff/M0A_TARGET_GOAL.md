# EP-L2 Codex Target Goal — M0a Generic Observability

## Goal

> Starting from the accepted D512 research baseline, implement timing-neutral cycle-based L2 admission-blocking and useful-service telemetry, prove OFF/ON functional equivalence, characterize the representative workload set, publish independent review evidence, and STOP before any functional EP-L2 mechanism.

## Read first

```text
docs/ep_l2/project_spec/README.md
docs/ep_l2/project_spec/decisions/ADR-005-calibrated-research-baseline.md
docs/ep_l2/project_spec/MECHANISM_SEQUENCE_CURRENT.md
docs/ep_l2/project_spec/EVIDENCE_AND_CLAIM_MODEL.md
docs/ep_l2/chatgpt_handoff/LANE_D_FINAL_CONVERGENCE_CHATGPT_REVIEW.md
docs/ep_l2/chatgpt_handoff/LANE_F_MECHANISM_PREP_CHATGPT_REVIEW.md
docs/ep_l2/chatgpt_handoff/M0A_OBSERVABILITY_HANDOFF.md
docs/ep_l2/chatgpt_handoff/M0A_OBSERVABILITY_ACCEPTANCE_CRITERIA.md
```

Treat the acceptance criteria as mandatory.

## Semantic parent

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

Use the calibrated resource configuration from ADR-005.

## Worktree

Prefer:

```text
Framework /workspace/worktrees/accel-sim-ep-l2-m0a/
Core      /workspace/worktrees/gpgpu-sim-ep-l2-m0a/
branch    hrl/ep-l2-m0a-observability-v0
results   /workspace/results/ep_l2_m0a/
```

## Execute autonomously

1. Audit the exact preview/admission decision and determine whether independent multi-cause reason predicates are available without short-circuit distortion.
2. Implement M0a observation-only producers and explicit enable/disable configuration.
3. Extend parser/analyzer/schema without changing old field semantics.
4. Add unit/directed tests for once-per-cycle denominator/any-blocked/reason-overlap and useful-admit/response semantics.
5. Release build + existing EP-L2 regression.
6. Prove M0a OFF vs ON simulated equivalence on vectorAdd, convolution and sad.
7. Freeze exact source/config.
8. Run M0a ON representative characterization for convolution, scan, vectorAdd, spmv, cfd and sad; launch independent rows in parallel and do not wait serially for scan.
9. Produce cumulative and temporal workload summaries.
10. Package/push evidence.

Self-repair only within observation/parser/runner/test scope. Any fix requiring a functional cache/admission/arbitration change is a hard stop.

## Required status

```text
M0A_OBSERVABILITY_REVIEW_READY
```

Then STOP for ChatGPT review.
