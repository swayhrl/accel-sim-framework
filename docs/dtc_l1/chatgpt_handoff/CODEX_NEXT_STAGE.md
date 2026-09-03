# CODEX_NEXT_STAGE

## Status

**ACTIVE — FINISH PAPER COMPUTE, EXECUTE EXTENDED-20 IN PARALLEL AFTER M5.2, COORDINATE WITH SEPARATE GRAPHICS RESEARCH WINDOW**

Current scheduling authority:

`docs/dtc_l1/m5/M5_V3_PARALLEL_TRACKS_APPROVAL.md`

M1-M4 remain closed PASS. M5.0A is PASS. Current Paper-10 work remains M5.0B/R5DV until canonical ratio-zero SpMV closes M5-T005.

## Active compute branches owned by this window

Core:

`hrl/decoupled-l1-m5-v0`

Framework:

`hrl/decoupled-l1-exp-m5-v0`

Do not modify validated M1-M4 branches or the independent graphics-research branch.

## Mandatory read order after integrating latest docs

1. Framework `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/m5/M5_V3_PARALLEL_TRACKS_APPROVAL.md`
4. `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`
5. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
6. `docs/dtc_l1/m5/M5_EXTENDED20_APPROVAL.md`
7. `docs/dtc_l1/m5/M5_EXTENDED20_FORMAL_MATRIX.md`
8. `docs/dtc_l1/m5/M5_PARALLEL_BATCH_POLICY.md`
9. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
10. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
11. `docs/dtc_l1/m5/M5_EXTENDED20_HANDOFF_CONTRACT.md`
12. `docs/dtc_l1/m5/M5_BRANCH_OWNERSHIP.md`
13. `docs/dtc_l1/m5/M5_GRAPHICS_INDEPENDENT_WINDOW_HANDOFF.md`
14. `docs/dtc_l1/m5/M5_GRAPHICS_HANDOFF_CONTRACT.md`
15. this file
16. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
17. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
18. `docs/dtc_l1/implementation/M5_ISSUE_LOG.md`
19. Core `AGENTS.md` and `docs/dtc_l1/DTC_L1_SPEC.md`

## Immediate work — do not disturb active R5DV jobs

Preserve every currently running canonical SpMV/diagnostic job and all existing uncommitted Framework experiment/graphics artifacts.

Finish R5DV according to the approved ratio-zero policy:

- canonical SpMV medium LEGACY/PAPER_BASE complete;
- output checks PASS;
- no old dirty-set deadlock;
- accounting drains;
- close M5-T005;
- resume remaining M5.0B workload recovery.

Do not redo already valid R5DV evidence.

## Paper compute sequence

Continue automatically:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`

Use existing stage acceptance/handoff contracts.

## Extended-20 sequence owned by this compute window

Selection is already reviewed/approved. Do not rerun the 52-candidate selection.

Approved selection anchor:

`hrl/decoupled-l1-exp-m5-extended20-select-v0@d43b6eec93f68efa94057f34ffa699463b53e6a6`

### M5.E1

Source/build/input/output/PTX formalization of all approved 20 may begin opportunistically when it does not disturb active Paper jobs.

Do not launch the 60 formal runs before M5.2.

Correct BlackScholes metadata to `Black-Scholes option pricing`; do not assume Monte Carlo.

### M5.E2

After M5.2 PASS, verify E1 identities against the frozen M5.2 Core/Framework/config/parser anchor, then launch:

`20 workloads x {PAPER_BASE,PAPER_IO,PAPER_OO} = 60 primary runs`.

Execute through `M5_PARALLEL_BATCH_POLICY.md`:

- dynamic measured-safe worker pool;
- isolated output directories;
- resumable job registry;
- mix workload/mode/heavy classes;
- do not run one workload triplet at a time unnecessarily;
- keep unrelated jobs progressing while an isolated issue is diagnosed when scientifically safe.

Paper M5.3/M5.4/M5.5/M5.6 and Extended E2/E3 are allowed to overlap in wall-clock time after M5.2.

### M5.E3

Produce causal/generalization synthesis, `GM-EXTENDED20` and `GM-ALL-COMPUTE30`. Preserve weak/negative results. Blanket parameter sweeps across all 20 are not required; targeted diagnostic follow-ups only for specific causal ambiguity.

## Compute freeze

M5.6 PASS alone is not the compute-freeze boundary.

If Paper M5.6 finishes before Extended E3, use status:

`M5_PAPER10_READY_WAITING_FOR_EXTENDED20`

Create `M5.COMPUTE_FREEZE` only after:

- Paper M5.6 PASS;
- Extended M5.E3 PASS;
- no unresolved correctness/fidelity issue;
- both active compute branches pushed/clean.

Then emit `docs/dtc_l1/m5/handoffs/M5_COMPUTE_FREEZE.md` with exact Core/Framework freeze SHAs.

## Graphics coordination

A separate Codex window owns Framework graphics research branch:

`hrl/decoupled-l1-exp-m5-graphics-research-v0`

That window may do M5.7/M5.8 only and must not modify this compute worktree/Core or this window's `LATEST_REPORT.md`.

Do not perform graphics M5.9+ integration on compute branches. After compute freeze, fresh graphics integration branches must be created from the exact freeze SHAs.

## Problem behavior

Ordinary workload/build/PTX/assertion/parser/counter/timeout/performance problems remain resolve-in-goal. Reproduce -> classify -> repair/reconstruct -> regress -> invalidate stale data -> continue.

A weak or negative DTC result is evidence, not a stop condition.

## Pause conditions

Pause only for a genuine researcher-decision boundary, for example:

- required change to frozen DTC/M0-M4 architecture semantics;
- irreducible experiment-meaning ambiguity;
- approved Extended workload becomes unusable and substitution choice cannot be resolved using pre-performance alternate rules;
- a cross-track finding requires changing a frozen common metric/config definition;
- final M5 review state after graphics/final synthesis.

Do not stop merely at Paper M5.6 or Extended E3; their join produces compute freeze for the graphics integration track.
