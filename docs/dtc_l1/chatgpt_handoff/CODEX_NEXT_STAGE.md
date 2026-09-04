# CODEX_NEXT_STAGE

## Status

**ACTIVE — CONTINUE PAPER COMPUTE; PREPARE/EXECUTE EXTENDED-20; GRAPHICS RESEARCH CLOSED SOURCE-BACKED-UNAVAILABLE**

Current scheduling authority:

- `docs/dtc_l1/m5/M5_V3_PARALLEL_TRACKS_APPROVAL.md`
- `docs/dtc_l1/m5/M5_GRAPHICS_RESEARCH_CLOSEOUT_APPROVAL.md`

M1-M4 remain closed PASS. M5.0A is PASS. M5-T005/R5DV is CLOSED. Current Paper-10 work is M5.0B workload recovery.

## Active compute branches owned by this window

Core:

`hrl/decoupled-l1-m5-v0`

Framework:

`hrl/decoupled-l1-exp-m5-v0`

Do not modify validated M1-M4 branches or the frozen graphics-research branch.

## Mandatory read order after integrating latest docs

1. Framework `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/m5/M5_V3_PARALLEL_TRACKS_APPROVAL.md`
4. `docs/dtc_l1/m5/M5_GRAPHICS_RESEARCH_CLOSEOUT_APPROVAL.md`
5. `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`
6. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
7. `docs/dtc_l1/m5/M5_EXTENDED20_APPROVAL.md`
8. `docs/dtc_l1/m5/M5_EXTENDED20_FORMAL_MATRIX.md`
9. `docs/dtc_l1/m5/M5_PARALLEL_BATCH_POLICY.md`
10. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
11. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
12. `docs/dtc_l1/m5/M5_EXTENDED20_HANDOFF_CONTRACT.md`
13. `docs/dtc_l1/m5/M5_BRANCH_OWNERSHIP.md`
14. this file
15. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
16. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
17. `docs/dtc_l1/implementation/M5_ISSUE_LOG.md`
18. Core `AGENTS.md` and `docs/dtc_l1/DTC_L1_SPEC.md`

Graphics M5.7/M5.8 handoffs remain evidence inputs for final M5.12 but are not active work for this compute window.

## Immediate work — continue M5.0B

Do not redo R5DV. Canonical ratio-zero SpMV LEGACY/PAPER_BASE completed with correct output and clean accounting; M5-T005 is CLOSED.

Preserve all currently running corrected M5.0B Base jobs and their isolated output directories. Continue remaining workload recovery and strict output/accounting validation.

At the last committed checkpoint BICG completed PASS and the remaining corrected Paper-10 Base runs were progressing without deadlock/assertion/fatal evidence.

## Paper compute sequence

Continue automatically:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`

Use existing stage acceptance/handoff contracts.

## Extended-20 sequence owned by this compute window

Selection is already reviewed/approved. Do not rerun the 52-candidate selection.

Approved final portfolio is authoritative in:

- `docs/dtc_l1/m5/M5_EXTENDED20_APPROVAL.md`
- `docs/dtc_l1/m5/extended20/EXTENDED20_APPROVED.tsv`

### M5.E1

Source/build/input/output/PTX formalization of all approved 20 may begin opportunistically when host CPU/RAM/disk/I/O conditions permit and when it does not disturb active Paper jobs.

Do not force large source materialization/builds merely to keep E1 busy while Paper-10 jobs are already resource-heavy. It is acceptable to defer expensive checkout/build work until the host has safe headroom, while continuing source-object/provenance audit that does not interfere with the active batch.

Do not launch the 60 formal runs before M5.2.

Use the review correction:

- `BlackScholes` = `Black-Scholes option pricing`, not assumed Monte Carlo.

### M5.E2

After M5.2 PASS, verify E1 identities against the frozen M5.2 Core/Framework/config/parser/metric anchor, then launch:

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

Produce causal/generalization synthesis, `GM-EXTENDED20` and `GM-ALL-COMPUTE30`. Preserve weak/negative results. Blanket parameter sweeps across all 20 are not required; use targeted diagnostic follow-ups only for specific causal ambiguity.

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

## Graphics coordination — closed under current evidence

Independent graphics research closed at:

`hrl/decoupled-l1-exp-m5-graphics-research-v0@ed36abb8f98372dbd1fef11d5b0e8780fb8bf17d`

Accepted terminal state:

`GRAPHICS_SOURCE_BACKED_UNAVAILABLE`

Do not:

- reopen graphics research without genuinely new source-backed/original artifacts;
- create graphics integration branches after compute freeze under current evidence;
- modify Core for graphics;
- run M5.9/M5.10/M5.11;
- emit graphics performance bars, `GM-GRAPHICS`, or `GM-ALL-PAPER`;
- use a memory proxy as formal paper reproduction.

After `M5.COMPUTE_FREEZE`, proceed directly to M5.12 negative-evidence synthesis and include the accepted M5.7/M5.8 handoffs/commit in the final review pack.

## Problem behavior

Ordinary workload/build/PTX/assertion/parser/counter/timeout/performance problems remain resolve-in-goal. Reproduce -> classify -> repair/reconstruct -> regress -> invalidate stale data -> continue.

A weak or negative DTC result is evidence, not a stop condition.

## Pause conditions

Pause only for a genuine researcher-decision boundary, for example:

- required change to frozen DTC/M0-M4 architecture semantics;
- irreducible experiment-meaning ambiguity;
- an approved Extended workload becomes unusable and substitution choice cannot be resolved using pre-performance alternate rules;
- a cross-track finding requires changing a frozen common metric/config definition;
- final M5 review state after M5.12.

Do not stop merely at Paper M5.6 or Extended E3; their join produces compute freeze, then M5.12 closes the current graphics-unavailable path.
