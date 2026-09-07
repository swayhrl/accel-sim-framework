# B8 Cross-Window Hypothesis and Experiment Prioritization

**Evidence label:** `SPECULATIVE_DIAGNOSTIC`
**B authority:** `hrl/vm-spec-farm-v0` at `d22756c4c71e7f76425bcab3122a7534707f39f9`
**C read-only evidence anchor:** `ea07cb0ec6fb3212c18f3435637f055e1296d737`

## Boundary

This pack synthesizes bounded B7 farm evidence with committed C4/C7 evidence
into falsifiable hypotheses and a small, gated recovery set. It is analysis-only:
no simulator, worker, trace generation, rebuild, smoke rerun, or full ROI was
started for B8.

Window C material was read only with `git show <C-anchor>:<path>`. No Window C
worktree, scratch area, process, configuration, or private artifact was
accessed. Window A was not accessed or modified.

The pack does **not** establish a full-workload result, a formal conclusion, a
candidate speedup, or a cross-window numeric comparison. B and C values remain
separate evidence for shared questions and are never pooled metrics.

## Contents

1. `INPUT_PROVENANCE.tsv` binds each permitted input to a revision and path.
2. `HYPOTHESIS_MATRIX.tsv` states H1--H6 with support, counterevidence,
   falsifiers, observables, and a minimum discriminating experiment.
3. `EVIDENCE_CONFLICTS_AND_LIMITS.md` records scope boundaries and conflicts.
4. `MINIMUM_INFORMATION_EXPERIMENT_SET.tsv` contains 18 gated bundles with
   positive, negative, and no-difference decision paths.
5. `RESUME_PLAN_AFTER_A_TERMINAL.md` defines later recovery gates; it is not
   permission to execute now.
6. `FINAL_REPORT.md` is the decision-ready synthesis.

## Terms

- `B`: Window B VM speculative experiment farm evidence.
- `C`: Window C committed C4/C7 speculative-candidate evidence.
- B7 coverage labels retain their original meanings; none is promoted here.
- `NEEDS_RUNTIME_EVIDENCE` means static, smoke, or bounded replay cannot decide
  the question.
- Outcome columns are decision branches, not predicted outcomes.
