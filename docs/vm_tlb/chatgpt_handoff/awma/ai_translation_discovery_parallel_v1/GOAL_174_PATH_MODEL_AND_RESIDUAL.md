# Goal 174-new — Translation/Cache Path Model + New-Trace Residual Qualification V1

Stage:
`AWMA_AI_TRANSLATION_PATH_AND_RESIDUAL_174NEW_V1`

Execution branch:
`hrl/awma-ai-translation-path-and-residual-174new-v1`

Node:
174-new

## 0. Purpose

Separate three things that were previously conflated:
1. program translation demand,
2. translation/cache access-path modeling,
3. genuine residual MMU resource pressure.

Then, if the node109 Native batch is available, evaluate new AI dimensions under the same discipline.

No mechanism search until a differentiated residual survives.

## 1. Authorities

Strong reference:
- `hrl/awma-intrawarp-translation-baseline-residual-v1`
- `9efe8236e0c6338addfef5480e1da91bffb504eb`

Post-classic result:
- `32854024b1b92313cf2dffc6280247a629033991`

Observatory:
- `b85d388abe98e5da70b749b52075c33fad7cede4`

Literature notebook:
- `177863f325d77278013e195528903ddc8b292e4e`

The accepted strong baseline remains frozen.
Path variants are diagnostics only and must not overwrite baseline authority.

## 2. Phase A — access-path source audit

Audit the current simulated ordering around:
- address generation/coalescing
- L1 TLB lookup
- L1D lookup/tag/data path
- L1 miss path
- L2/ICNT admission
- translation result apply/replay.

Document exactly which event currently waits for which.

Create:
`ACCESS_PATH_SOURCE_AUDIT.md`

## 3. Phase B — implement two bounded diagnostic path models

Keep classic warp-VPN dedup semantics identical.

### B0: CURRENT_SEQUENTIAL
Accepted strong reference unchanged.

### B1: VIPT_LIKE_PARALLEL_L1_DIAGNOSTIC
Literature-aligned diagnostic:
- L1 TLB and L1D lookup begin in parallel where source permits;
- L1D hit completion cannot use an unverified physical tag result before translation legality is satisfied;
- L1 miss / request to lower physical levels must wait for translation before L2/ICNT;
- no future information;
- no extra ports;
- no virtual-cache synonym shortcut;
- no claim that this is actual RTX4080 internals.

Model the minimum source-consistent overlap, not a zero-latency TLB.

### B2: VIRTUAL_L1_FILTER_BOUND_DIAGNOSTIC
A bound inspired by virtual-cache literature / MPW sensitivity:
- if the request is fully served by an L1 path under the diagnostic virtual-L1 assumption, no translation service is required for that request before completion;
- L1 miss still requires normal translation before lower physical levels;
- this is an idealized path bound, not a proposed mechanism and not a claim about Ada.

If B2 cannot be implemented without changing cache correctness semantics in a source-auditable way, mark NOT_IMPLEMENTED rather than inventing behavior.

## 4. Directed correctness / neutrality

Before workload runs, create directed fixtures for:
- L1D hit + L1 TLB hit
- L1D miss + L1 TLB hit
- L1D hit + L1 TLB miss
- L1D miss + L1 TLB miss
- replay after translation
- atomic/write where applicable

Verify:
- identical architectural result
- exactly-once translation/application where required
- no skipped lower-level translation on L1 miss
- no extra/missing memory request
- terminal/quiescence

## 5. Existing-trace path-model matrix

Pre-register and run on:
T0, T1, T2, A2.

For each:
- CURRENT_SEQUENTIAL strong reference
- VIPT_LIKE_PARALLEL_L1
- VIRTUAL_L1_FILTER_BOUND if legally implemented

Reuse accepted runs where possible.
Do not rerun strong baseline without need.

Record:
- cycles
- translation service counts
- L1D hit/miss/reservation outcomes
- time translation is exposed on the critical request path
- scheduler/memory localization with Observatory Level1 only if needed.

Question:
How much of the previously observed 0/80 sensitivity is caused by sequential path modeling rather than program-intrinsic translation pressure?

No performance claim about real RTX4080.

## 6. One-time node109 handoff check

Only after Phases A-E close, check once for branch:
`hrl/awma-ai-translation-native-atlas-capture-109-v1`

If not present or not status `READY_FOR_AI_TRANSLATION_RESIDUAL_174NEW`:
output `PREP_COMPLETE_AWAITING_NATIVE_ATLAS`
and close.

No polling.

If ready:
consume `NATIVE_ATLAS_CONSUMER_HANDOFF.json` and continue.

## 7. New-trace qualification

For every qualified node109 target (max six):
first run CURRENT_SEQUENTIAL + WARP_VPN_DEDUP_REFERENCE qualification.

Require:
- target identity
- instructions/CTA/UID
- translated coverage
- untranslated/unobserved/duplicate=0
- terminal/quiescence

Then collect the strong-baseline residual matrix:
- L1 launches/hits/misses
- L2 launches
- MSHR alloc/merge/full
- PWQ/walker/PTW/PTE if modeled
- L1D behavior
- translation-not-ready exposure
- scheduler/memory bottleneck location.

## 8. Adaptive diagnostic decision tree

Do NOT run every diagnostic on every target.

### Case H: hit-dominated residual
If high L1-TLB hit service dominates and miss-side pressure is low:
run VIPT-like path diagnostic.
Use B2 bound only if necessary.

### Case W: walker/PWQ pressure
Only if a target shows material PTW/PWQ/walker queueing:
run a bounded walker-throughput diagnostic inspired by MPW:
- remove/reduce walker queueing or increase service concurrency only as a causal bound;
- do not implement MPW as a candidate;
- preserve page walk memory accesses unless the diagnostic explicitly studies them.

### Case M: MSHR/miss-side pressure
Only if MSHR full/merge/translation miss-side service is material:
use existing source-supported capacity/ideal diagnostic.
Compare to LATPC/NeuMMU/ISCA2018 closest work before any candidate.

### Case P: mapping-predictability idea
Virtual-page locality alone is insufficient.
Do not infer Avatar applicability without physical mapping + validation evidence.
No speculative translation candidate in this Goal.

Max new full-kernel diagnostics after the strong baseline:
12 total across all new targets.
Choose by observed service location, not by desire for a positive result.

## 9. Residual problem gate

A new problem may survive only if:
1. material under WARP_VPN_DEDUP_REFERENCE,
2. remains material under the appropriate access-path diagnostic/bound,
3. localized to a concrete service/resource,
4. not already provided by Pichai/Virtual Caching/ISCA2018/Neighborhood/LATPC/MPW/Avatar/MASK or other closest primary work,
5. uses online/source-available information for any future solution.

Produce at most TWO problem cards.

If none:
`NO_NEW_AI_TRANSLATION_PROBLEM_IDENTIFIED_V1`

## 10. Optional single prototype

Only if one problem passes all gates:
- preregister max 3 development targets from the node109 batch;
- implement at most ONE primary prototype;
- baseline is WARP_VPN_DEDUP_REFERENCE + the appropriate realistic path model, not historical OFF;
- max 3 main + 3 matched-control full replays;
- no parameter sweep;
- no V2/V3 repair loop.

Otherwise do not write mechanism code.

Possible final statuses:
- `PREP_COMPLETE_AWAITING_NATIVE_ATLAS`
- `NO_NEW_AI_TRANSLATION_PROBLEM_IDENTIFIED_V1`
- `NOVEL_AI_TRANSLATION_PROBLEM_IDENTIFIED_READY_FOR_FORMAL_DEVELOPMENT`
- `AI_TRANSLATION_PROTOTYPE_SUPPORTED_DEVELOPMENT`
- `AI_TRANSLATION_PROTOTYPE_NOT_SUPPORTED`

## 11. Deliverables

- ACCESS_PATH_SOURCE_AUDIT.md
- PATH_MODEL_CONTRACT.md
- DIRECTED_PATH_CORRECTNESS.tsv
- EXISTING_TRACE_PATH_MATRIX.tsv
- EXISTING_TRACE_INTERPRETATION.md
- NEW_TRACE_QUALIFICATION.tsv (if node109 ready)
- NEW_AI_RESIDUAL_MATRIX.tsv
- DIAGNOSTIC_DECISION_LOG.tsv
- CLOSEST_WORK_SCREEN.md
- PROBLEM_CARD_1.md / PROBLEM_CARD_2.md if any
- PROTOTYPE_DECISION.md
- REPORT.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Commit/push/fetch-back/remote tree+hash/clean and STOP.
