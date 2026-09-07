# B8 Acceptance Matrix

Goal：`B8_CROSS_WINDOW_HYPOTHESIS_AND_EXPERIMENT_PRIORITIZATION`

| ID | Acceptance criterion | Required evidence |
| --- | --- | --- |
| B8-A1 | Analysis-only | No simulator, build, trace generation, worker, large ROI scan |
| B8-A2 | Isolation | Window A/C worktrees, processes and scratch untouched |
| B8-A3 | Provenance | B7 `118ead03...` and C7 `ea07cb0...` inputs bound by SHA/path |
| B8-A4 | Evidence scope | Partial/smoke/planned/static/opportunity labels preserved |
| B8-A5 | Hypothesis coverage | H1-H6 covered or superseded by stronger evidence-backed partition |
| B8-A6 | Falsifiability | Every retained hypothesis has counter-evidence and explicit falsifier |
| B8-A7 | Cross-window synthesis | B and C evidence compared without merging incompatible metrics/proxies |
| B8-A8 | Confirmation-bias guard | At least one experiment can reject each Segment/Sub-entry hypothesis and test conventional alternatives |
| B8-A9 | Object-attribution risk | UNKNOWN traffic treated as unresolved, never silently reassigned |
| B8-A10 | Minimum experiment set | Small first-batch set, approximately 8-20 items or fewer if justified |
| B8-A11 | Resource awareness | Every proposed experiment has resource class and gate requirements |
| B8-A12 | Decision usefulness | Positive/negative/no-difference outcomes map to next decisions |
| B8-A13 | No execution | B8 does not automatically run any proposed experiment |
| B8-A14 | Deliverables | Required review-pack files produced and internally consistent |
| B8-A15 | Closeout | Commit/push then STOP for independent review |

Any violation of A1/A2/A13 is a hard FAIL for this stage. Runtime evidence unavailable in B8 must be marked `NEEDS_RUNTIME_EVIDENCE`, not fabricated or inferred from analytical proxies.