# AWMA：经典基线闭合后的剩余问题发现 V1

日期：2026-09-26。ChatGPT-owned coordination / execution goal。

## 0. 科学状态重置

已接受 Lane B：
- branch `hrl/awma-intrawarp-translation-baseline-residual-v1`
- commit `9efe8236e0c6338addfef5480e1da91bffb504eb`
- judgement `CLASSIC_INTRAWARP_CAPABILITY_COVERS_CURRENT_BENEFIT`

七个开发 target 上：
- frozen PREL1 followers 与 SAME_DYNAMIC_WARP_INSTRUCTION VPN dedup reference 的可覆盖集合逐请求完全重合；
- PREL1_ONLY=0、WARP_ONLY=0、UNKNOWN=0；
- A1/A2/T2 周期完全相同；
- T0/T1/SPLITKV/COMBINE reference 更快；
- 因此 current PREL1 不再作为 novel mechanism candidate。保留为历史失败/对照资产，不继续调优、holdout 或 PPA。

已接受 Lane E prep：
- branch `hrl/awma-post-coalescing-research-hypotheses-v1`
- commit `b06ebfe66ab862c1fffa5f0bc3340a8814f26ec9`
- status `PREP_COMPLETE_AWAITING_BASELINE`

LATPC 全文补充：
- coordination commit `3594aa192a9362dbd5b15e8bd7508773a17cc1a7`
- file `LATPC_FULL_TEXT_REVIEW_AND_LANE_ADDENDUM_V1.md`
- LATPC baseline itself already includes same-warp-instruction page coalescing before L1 TLB.
- LATPC additions are unique-VPN regularity detection, multi-VPN miss compression, and page-walk batching.

Additional closest work now reviewed:
Seunghee Shin et al., "Scheduling Page Table Walks for Irregular GPU Applications", ISCA 2018, DOI 10.1109/ISCA.2018.00025.
Primary PDF:
https://www.csa.iisc.ac.in/~arkapravab/papers/GPU_page_walk_scheduler_ISCA_18.pdf

Key primary-text facts:
- same-page translations from one SIMD instruction are already coalesced before TLB;
- authors explicitly state instruction progress is determined by the last walk request completing;
- they batch page walks from the same SIMD instruction;
- they prioritize instructions estimated to require less translation work;
- scheduler uses per-instruction identity in the IOMMU/page-walk queue.

Consequence:
H1_LAST_UNRESOLVED_PAGE_GROUP_CRITICALITY has HIGH_CLOSEST_WORK_OVERLAP.
Do not promote H1 as a new mechanism merely because its exact predicate says "last unresolved group".
It may be used only as a diagnostic observation unless a later result demonstrates a materially different service level/problem that the ISCA 2018 scheduler cannot address.

H2_DEMAND_BEFORE_RESIDENT_PRELAUNCH remains diagnostic only.
Demand-over-prefetch priority is conventional; a positive result can identify a baseline pathology but is not by itself a publication-level mechanism.

## 1. New objective

The next research question is NOT "how do we rescue PREL1?"

It is:

> After installing the reasonable classic warp-instruction VPN-dedup capability, does address translation still expose a material, localized optimization opportunity in the current AI workload evidence? If yes, what exact unresolved resource/path causes it, and is that unresolved problem not already covered by closest work?

The strong reference from Lane B becomes the default scientific baseline for new mechanism discovery:

`WARP_VPN_DEDUP_REFERENCE`

Historical OFF is retained only for historical comparison/attribution.

## 2. Execution lane

Continue the existing Lane E Codex window.

Stage:
`AWMA_POST_CLASSIC_BASELINE_RESIDUAL_DISCOVERY_V1`

Branch:
`hrl/awma-post-classic-baseline-residual-discovery-v1`

Parent/fetch authorities:
- Lane B `9efe8236e0c6338addfef5480e1da91bffb504eb`
- Lane E prep `b06ebfe66ab862c1fffa5f0bc3340a8814f26ec9`
- LATPC review `3594aa192a9362dbd5b15e8bd7508773a17cc1a7`
- Observatory `b85d388abe98e5da70b749b52075c33fad7cede4`

Do not modify any of those branches.

No node109.
No new capture.
No RTL/PPA.
No PREL1 repair.
No paper packaging.

## 3. Phase A — consume accepted Lane B and retire invalid candidates

Fetch Lane B once and read:
`docs/vm_tlb/review_packs/AWMA_INTRAWARP_TRANSLATION_BASELINE_AND_RESIDUAL_V1/CONSUMER_HANDOFF.json`
plus REPORT / COMPARISON_RESULTS / REQUEST_SCOPE.

Update E prior-work state with LATPC full text and ISCA 2018 page-walk scheduler.

Candidate classification:
- current PREL1: RETIRED_AS_NOVEL_MECHANISM
- H1 last-unresolved-group: CLOSEST_WORK_OVERLAP_HIGH / DIAGNOSTIC_ONLY unless a materially different unresolved service level is demonstrated
- H2 demand-before-prelaunch: DIAGNOSTIC_ONLY / NOT_A_NOVELTY_CLAIM

Do not spend candidate replay budget on H1/H2 merely because fixtures already exist.

## 4. Phase B — strong-baseline residual characterization

Use `WARP_VPN_DEDUP_REFERENCE` as baseline.

Reuse existing Lane B run logs first. Add only missing observability needed to answer the residual question.

Targets:
T0, T1, T2, SPLITKV, COMBINE, A1, A2.

For each target report at minimum:

### B1. Remaining translation work after classic dedup
- dynamic memory instructions
- unique VPN groups per instruction histogram
- L1 launches / hit-source breakdown where source-supported
- L2 launches
- MSHR allocations/merges/reservation failures
- PTW starts / PWQ waiting / PTE requests
- L1 port denials
- resident-prelaunch attempts versus head-demand attempts
- exact head-demand-versus-prelaunch same-cycle collision count
- translation-ready -> address-apply delay
- address-apply -> cache-admission delay
- head translation pending exposure

Do not relabel translate() retries as physical work.

### B2. Multi-page diagnostic
For max-two-page current targets, compute exact number of dynamic instructions with one versus two unique page groups.

If an exact last-unresolved-group condition is observed, record:
- count/cycles
- service level where it waits (L1 port, L2/MSHR, PTW/PWQ, result apply)
- whether it actually reaches the instruction head/critical progress point
- competing work type.

This is diagnostic only because ISCA 2018 already covers last-walk/batched instruction-level page-walk scheduling.

### B3. H2 diagnostic
Instrument only if Lane B logs cannot answer it.

Count exact cycles where:
- a baseline-eligible head demand needs the finite L1 TLB port, AND
- a resident non-head prelaunch consumes/wins that same port first.

Also record displaced prelaunch and whether demand-first would merely reorder work.

Do NOT implement demand-first performance policy in this phase unless the count is nonzero and the residual analysis shows this collision is a material mediator.

## 5. Phase C — residual headroom, not raw activity

Raw translation activity is not sufficient.

Use two complementary forms of evidence:

1. Observational localization with accepted Bottleneck Observatory Level 1; Level 2 only on targets where aggregate evidence cannot localize a material residual.
2. A bounded causal diagnostic only if source-composable without changing the classic grouping semantics:
   - classic reference + accepted 0/80 L1-hit-latency intervention, and/or
   - classic reference + accepted zero-modeled-translation-service intervention.

These are diagnostics, not hardware proposals or upper bounds.
Do not run both diagnostics on every target automatically.

Preselect high-value targets before viewing new results:
- T0: prefill Flash, large historical response
- T1: prefill GEMM, large work / different sensitivity
- T2: decode GEMV
- A2: long-context exact GEMV
Optional SPLITKV only if it carries a distinct residual location.

Maximum new full-kernel diagnostic replays for Phase C: 8.
Reuse all existing reference results; do not rerun baseline ceremonially.

The output must answer:
- Is there material residual translation headroom after classic intrawarp dedup?
- Is it L1-hit-path bandwidth/latency, miss-side MSHR/PTW, result-application timing, or downstream hiding?
- Which target/family exhibits it?
- Does the residual survive the reasonable baseline, rather than historical OFF only?

If residual headroom is negligible or dominated by non-translation bottlenecks:
output `CURRENT_AI_TRANSLATION_MECHANISM_SEARCH_NOT_JUSTIFIED` and STOP.
This is a valid result; do not force a new mechanism.

## 6. Phase D — closest-work screen before mechanism code

Only if Phase C identifies a concrete residual problem:

Search/read the closest primary work for that exact service level/rule.

Mandatory already-known references:
- Pichai et al. ASPLOS 2014 / DCS-TR-703
- Shin et al. ISCA 2018 page-walk scheduling
- Shin et al. MICRO 2018 Neighborhood-Aware Address Translation if miss/walk locality is involved
- Lee et al. HPCA 2025 Marching Page Walks if PTW batching/concurrency is involved
- LATPC MICRO 2025 if warp VPN regularity, MSHR compression, prefetch or walk batching is involved
- MASK ASPLOS 2018 if translation/data scheduling or post-translation bursts are involved
- RPAWS 2026 if generic compute/memory pressure scheduling is involved
- segmentation-based LLM translation if contiguous/range/tensor translation is involved.

CAC PACT 2018 full text remains desirable for compiler/coalescing candidates, but does not block an unrelated residual problem.

For each surviving problem write:
- exact existing capability
- exact uncovered limitation
- why current AI behavior makes it relevant
- online information available
- finite resource requirement
- likely cost/pathology
- minimal falsifying experiment.

At most TWO problem cards; zero is allowed.

## 7. Phase E — only if a genuinely residual, differentiated problem survives

A candidate may enter code only when:
1. residual is material under WARP_VPN_DEDUP_REFERENCE;
2. service location is localized;
3. closest primary work does not already provide the same capability;
4. candidate uses current/online information only;
5. finite resources and fallback are explicit;
6. one minimal counterexample/falsification criterion is preregistered.

Then allow at most ONE primary candidate in this Goal.
A second may remain paper design only.

Performance baseline must be `WARP_VPN_DEDUP_REFERENCE`, not historical OFF.

Pre-register max 3 development targets based on Phase C residual symptoms before viewing candidate outputs.
Max candidate full replays: 3 main + up to 3 matched controls = 6.
No parameter sweep.
No automatic repair V2/V3 after failure.

If no candidate satisfies the gate:
output `NO_NOVEL_RESIDUAL_MECHANISM_IDENTIFIED_V1` and STOP.

## 8. Deliverables

At minimum:

- REPORT.md
- STRONG_BASELINE_RESIDUAL_MATRIX.tsv
- MULTIPAGE_AND_HEAD_EXPOSURE.tsv
- HEAD_PRELAUNCH_COLLISION.tsv
- RESIDUAL_LOCALIZATION.md
- RESIDUAL_HEADROOM.tsv
- CLOSEST_WORK_AFTER_BASELINE.md
- HYPOTHESIS_DISPOSITION.tsv
- NEW_PROBLEM_CARD_1.md if any
- NEW_PROBLEM_CARD_2.md if any
- PROTOTYPE_DECISION.md
- if prototype runs: candidate/control matrix + correctness receipts
- RAW_INDEX.tsv
- SHA256SUMS

Final status must be exactly one of:
- `CURRENT_AI_TRANSLATION_MECHANISM_SEARCH_NOT_JUSTIFIED`
- `NO_NOVEL_RESIDUAL_MECHANISM_IDENTIFIED_V1`
- `NOVEL_RESIDUAL_PROBLEM_IDENTIFIED_READY_FOR_FORMAL_DEVELOPMENT`
- `RESIDUAL_PROTOTYPE_SUPPORTED_DEVELOPMENT`
- `RESIDUAL_PROTOTYPE_NOT_SUPPORTED`

Do not output PAPER_READY.

## 9. Closure

Commit/push/fetch-back/remote HEAD+tree/hash/clean.
STOP.
