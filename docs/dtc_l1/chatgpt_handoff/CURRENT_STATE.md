# DTC-L1 Current State

Last coordination update: 2026-09-05

Status: **M1-M4 VALIDATED; M5.0A PASS; M5.0BT WAITING_FOR_EXACT_TRACE_CAPTURE; EXTENDED-20 APPROVED; GRAPHICS M5.7/M5.8 CLOSED SOURCE-BACKED-UNAVAILABLE**

## Current M5.0BT authority

Researcher authority supersedes the cap-256 execution-driven wait: Q1 is
`M5.0BF_Q1_REOPENED_FOR_EXACT_TRACE_RECAPTURE`, with trace capture authorized
and formal-path qualification pending. Q2/Q3 remain frozen at 80 SM and cap
10240 (128 credits/SM); cap-256 is obsolete diagnostic-only. Five live
cap-256 jobs were gracefully terminated only in their run-owned PGIDs and are
preserved as `RESEARCHER_ABORTED_SUPERSEDED_CAP256`, not failures. M5.0BT
exact Paper-10 capture/qualification now gates M5.0C; see
`m5/handoffs/M5_0BT_TRACE_CAPTURE_HANDOFF.md`.

## Validated anchors

M1-M4 remain frozen validated infrastructure:

- Core final M1-M4: `cdeec769fd0c1be12b45d58536ecb81074d4b415`.
- Framework final M1-M4: `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`.

Active M5 compute branches:

- Core `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`;
- Framework `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`.

## Current authority

Read current M5 authority in this order:

1. `docs/dtc_l1/m5/M5_V3_PARALLEL_TRACKS_APPROVAL.md`
2. `docs/dtc_l1/m5/M5_GRAPHICS_RESEARCH_CLOSEOUT_APPROVAL.md`
3. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
4. `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`
5. `docs/dtc_l1/m5/M5_EXTENDED20_APPROVAL.md`
6. `docs/dtc_l1/m5/M5_EXTENDED20_FORMAL_MATRIX.md`
7. `docs/dtc_l1/m5/M5_PARALLEL_BATCH_POLICY.md`
8. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
9. `docs/dtc_l1/m5/M5_EXTENDED20_HANDOFF_CONTRACT.md`
10. `docs/dtc_l1/m5/M5_BRANCH_OWNERSHIP.md`
11. `docs/dtc_l1/m5/M5_GRAPHICS_INDEPENDENT_WINDOW_HANDOFF.md`
12. `docs/dtc_l1/m5/M5_GRAPHICS_POST_COMPUTE_PLAN.md`
13. `docs/dtc_l1/m5/M5_GRAPHICS_HANDOFF_CONTRACT.md`
14. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
15. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`

The graphics closeout supersedes the previously active graphics-search state. M5.9-M5.11 are not active under current evidence.

## Research objective

M5 is mechanism/trend reproduction, not numerical fitting to thesis speedups.

`Base structural limits -> constrained live misses -> DTC removes limits -> concurrency/latency hiding changes -> performance effect`

Weak/negative results require causal classification rather than tuning.

## Frozen compute definitions

### Main paper configuration

- PAPER_BASE: conventional 16 KiB L1, 128B line, 4-way, PIB=8, MSHR=32.
- PAPER_IO: 16 KiB logical Tag + 80 KiB physical Cacheline Array, PIB=256.
- PAPER_OO: 16 KiB logical Tag + 80 KiB physical Cacheline Array, PIB=128.

### Dirty-victim policy

All paper-facing/formal M5 configs explicitly use:

`-gpgpu_l1_cache_write_ratio 0`

Ratio 25 remains diagnostic platform policy only.

### Figure 4.7

Live miss = new-miss lower-request commit through final lower response; primary metric = per-SM cycle average.

### Figure 4.2

Formal categories: PIB full, true Tag+Cacheline allocation failure, MSHR capacity/merge, Miss Queue/lower capacity. Tag-bank arbitration remains diagnostic.

## Current Paper-10 stage — M5.0B workload recovery

M5.0A is PASS.

M5-T005 is CLOSED. Canonical Parboil JDS SpMV medium ratio-zero LEGACY and PAPER_BASE both completed naturally with official output checking PASS. PAPER_BASE also closed PIB/lower accounting, so R5DV no longer blocks M5.0B.

Current committed M5.0B evidence reports:

- corrected BICG PAPER_BASE ratio-zero completion PASS with strict output/accounting checks;
- the remaining corrected Paper-10 Base jobs progressing in isolated output directories;
- no active formal Base run showing deadlock/assertion/fatal evidence at the last committed checkpoint;
- old ratio-25/old-runtime data retained as diagnostic only.

Paper progression:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`

Do not redo closed R5DV unless a later source-correct behavior change invalidates it.

## Extended-20 state

Selection branch:

`hrl/decoupled-l1-exp-m5-extended20-select-v0`

Reviewed selection commit:

`d43b6eec93f68efa94057f34ffa699463b53e6a6`

Independent review verdict: **APPROVED WITH PRE-PERFORMANCE REFINEMENT**.

Final approved primary set and alternates are authoritative in:

`docs/dtc_l1/m5/M5_EXTENDED20_APPROVAL.md`

Key review refinements:

- Rodinia `lud` replaces PolyBench `3mm` in the primary 20 to reduce near-duplicate dense-family/Q4-cost bias;
- `3mm` becomes ALT01;
- CUDA SDK `BlackScholes` metadata is corrected to `Black-Scholes option pricing`, not assumed Monte Carlo.

Extended progression:

`M5.E1 formalization -> M5.E2 60-run Base/IO/OO wave -> M5.E3 synthesis`

E1 may prepare source/build/input/PTX/output identity early when host resources allow. E2 begins only after M5.2 freezes the common formal anchor.

Extended jobs must use the resource-aware worker pool in `M5_PARALLEL_BATCH_POLICY.md`; unnecessary one-by-one execution is forbidden.

## Graphics state — research complete

Graphics research branch:

`hrl/decoupled-l1-exp-m5-graphics-research-v0@ed36abb8f98372dbd1fef11d5b0e8780fb8bf17d`

Accepted terminal state:

`GRAPHICS_SOURCE_BACKED_UNAVAILABLE`

M5.7 established source-equivalent glmark2 provenance for `jellyfish`, `cat-tex`, `cube-tex`, and `horse`, while retaining `2D-tex` as unresolved with no visual near-match substitution.

M5.8 exhaustively audited the authorized original-artifact, historical-simulator, direct-front-end, and source-backed trace/replay routes. No route establishes the required shader/grouping/request/texture/order/draw-frame/framebuffer/timing contract needed to exercise Base/IO/OO through the same DTC mechanism.

The negative conclusion is bounded to available/recovered evidence. A genuinely new original/source-backed artifact may reopen M5.8 only under its explicit admission contract.

Current consequence:

- graphics research branch is evidence/read-only;
- no M5.9/M5.10/M5.11 execution;
- no graphics Core integration branches are needed after compute freeze under current evidence;
- no formal `GM-GRAPHICS` or `GM-ALL-PAPER`;
- final M5.12 carries the graphics negative evidence explicitly.

Authoritative review:

`docs/dtc_l1/m5/M5_GRAPHICS_RESEARCH_CLOSEOUT_APPROVAL.md`

## Compute-freeze join barrier

M5.6 alone does not freeze compute.

`M5.COMPUTE_FREEZE` requires:

- Paper M5.6 PASS;
- Extended M5.E3 PASS;
- no unresolved correctness/fidelity issue;
- active compute branches pushed/clean.

Then record immutable `COMPUTE_FREEZE_CORE_SHA` and `COMPUTE_FREEZE_FRAMEWORK_SHA` in:

`docs/dtc_l1/m5/handoffs/M5_COMPUTE_FREEZE.md`

## Final M5 dependency

M5.12 now requires:

- Paper-10 through M5.6;
- Extended-20 through M5.E3;
- `M5.COMPUTE_FREEZE`;
- accepted graphics closeout commit `ed36abb8f98372dbd1fef11d5b0e8780fb8bf17d`;
- no unresolved correctness/fidelity issue.

Reporting groups:

- `GM-PAPER10` / `GM-GP`;
- `GM-EXTENDED20`;
- `GM-ALL-COMPUTE30` supplemental.

Under the current graphics closeout:

- no `GM-GRAPHICS`;
- no `GM-ALL-PAPER`.

## Final state

Current expected M5 terminal state:

`M5_COMPUTE30_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`

Figure 4.6 fresh area/synthesis is outside M5 and remains a separate M6 decision.
