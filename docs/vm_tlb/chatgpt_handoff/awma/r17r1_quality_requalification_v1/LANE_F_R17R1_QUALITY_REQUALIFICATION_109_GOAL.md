# Codex Goal — Lane F / node109
## AWMA R17R1 CAGRA baseline quality requalification and continuation V1

Date: 2026-09-30

Execution branch:
`hrl/awma-r17r1-quality-requalification-109-v1`

Scientific parent:
`78874fbfd767ec1321d41a04e4c51589a3c07298`

This is one unattended solve-and-continue Goal. Do not stop after quality qualification if the gate passes; continue through formal timing/localization/holdout under the rules below.

---

## 0. Question

Repair exactly one uncertainty:

> Did R17 V1 fail because the preregistered strong CAGRA quality baseline was too narrow / used a weaker default-build index, or does a mature CAGRA baseline still fail the frozen recall@10 >=0.95 contract on this input?

Only after quality qualifies may the original R17 low-concurrency performance question resume.

Do not lower the recall threshold.

---

## 1. Reuse and verify accepted authority

Reuse, do not redownload unless a hash repair is needed:
- normalized GloVe-100-angular base/query/GT;
- discovery queries 0..255;
- sealed holdout 256..511;
- V1 IVF_PQ CAGRA index:
  graph SHA `a68d4a2905fcab13a40872db73165fb4271a493f09b9fd61f5f1e9a401f073b8`;
  serialized SHA `6cddddb35f63d31b1308d1411d76aabcef910b11caea1778ca823f4fb63e7151`.

Reuse runtime:
`cuvs-cu12==26.8.1`
source:
`NVIDIA/cuvs v26.08.01 @ 25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab`.

Re-read stable:
`python/cuvs_bench/cuvs_bench/config/algos/cuvs_cagra.yaml`

Bind in the receipt that benchmark-base build is NN_DESCENT and base search grid includes itopk through 512 and search_width through 64.

If any accepted identity cannot be reproduced, STOP:
`R17R1_PARENT_IDENTITY_NOT_REPRODUCIBLE`.

---

## 2. Stage A — quality extension on the existing IVF_PQ index

No formal latency claim in Stage A.
No holdout.
No profiler.

All points use Q1, discovery IDs 0..255, k=10, same index.

Previously measured points may be reused by hash/receipt; do not rerun them just to fill tables.

### A1 — source-supported high-itopk completion

Measure these missing points:

SINGLE_CTA:
- (itopk=128, search_width=1)
- (256,1)
- (512,1)

MULTI_CTA:
- (512,1)

For MULTI_CTA report source-derived CTAs/query:
`max(search_width, ceil(itopk/32))`.

If one or more points reach recall>=0.95, proceed to Stage C candidate selection.
Do not automatically run A2.

### A2 — only if A1 has no recall-qualified point

Use only the top official itopk=512.

SINGLE_CTA:
- width=2
- width=4
- width=8

MULTI_CTA:
- width=32
- width=64

Rationale:
- widths <=16 do not increase MULTI_CTA trajectories beyond ceil(512/32)=16;
- single-CTA widths 2/4/8 are explicitly used by the stable persistent benchmark group.

If a point is rejected by the runtime because of resource/layout limits, record INVALID_SOURCE_SUPPORTED_POINT and continue to the next bounded point.

If any A2 point reaches >=0.95, proceed to Stage C.

If no A1/A2 point reaches >=0.95, proceed to Stage B. Do not expand further on the IVF_PQ index.

---

## 3. Stage B — one official-base NN_DESCENT index, only if Stage A fails

Build exactly one new index on the same normalized base:

- graph_degree=64
- intermediate_graph_degree=128
- graph_build_algo="NN_DESCENT"
- same metric and FP32 input
- no compression/filter/update.

Record:
- build time
- graph hash
- serialized index hash
- residency
- memory
- exact source/runtime identity.

This is a strong-baseline qualification repair, not a performance intervention.

### B1 quality ladder

Use discovery Q1 only.

First:
- AUTO 64/1
- SINGLE_CTA 64/1
- MULTI_CTA 64/1

Then if still needed:
- SINGLE_CTA 256/1
- MULTI_CTA 256/1
- SINGLE_CTA 512/1
- MULTI_CTA 512/1

Then only if still needed:
- SINGLE_CTA 512/2
- 512/4
- 512/8
- MULTI_CTA 512/32
- 512/64.

Stop the quality ladder as soon as at least one qualified SINGLE_CTA or MULTI_CTA configuration is found **and** there is enough information to form the Stage-C candidate set below.

Do not tune graph degree/build parameters.
Do not build a third index.

If even the complete bounded NN_DESCENT ladder has no recall>=0.95:
final decision:
`R17_CAGRA_QUALITY_BASELINE_NOT_QUALIFIED_V2`
Publish closure and STOP.

This is still not a graph-search performance negative.

---

## 4. Stage C — freeze strong quality-qualified Q1 candidates

From all discovery points on the **qualified index only** (IVF_PQ if A passed; otherwise NN_DESCENT), form at most three candidates:

1. lowest-search-effort qualified MULTI_CTA point;
2. lowest-search-effort qualified SINGLE_CTA point;
3. AUTO/default if it independently qualifies and is not source-identical to one above.

"Lowest search effort" is ordered by:
- lower itopk first;
- then lower search_width.

Do not choose by preliminary screen time.

Run formal paired timing on these <=3 candidates:
- 3 groups
- 2 warmups/arm/group
- 5 formal repeats/arm/group
- each repeat = all 256 discovery queries as individual Q1 searches
- alternate arm order
- save every sample.

Select the fastest formally measured candidate at recall>=0.95 as:
`Q1_STRONG_V2`.

If all formal candidates are unstable or quality no longer reproduces:
`R17_RESULT_MIXED_NEEDS_REVIEW`
STOP.

---

## 5. Stage D — matched low-concurrency characterization

Use `Q1_STRONG_V2` explicit mode/params.

Run the exact same search configuration on:
- Q1: 256 individual queries
- Q32: same 256 queries in eight batches.

Do not allow AUTO to switch mode for this matched comparison unless AUTO itself is the frozen strong arm and source identity is part of the claim.

Report:
- complete host time
- synchronized GPU time
- recall
- per-query Q1 latency distribution
- Q32 batch times
- throughput
- allocations/workspace
- any exposed executed-iteration/work counters.

`Q32 batch time / 32` may be reported only as an amortized throughput diagnostic, never as a Q1 latency bound.

If there is no material low-concurrency loss after the strong baseline:
`R17_CAGRA_EXISTING_SOFTWARE_SUFFICIENT`
STOP.

---

## 6. Stage E — wrapper gate

If host/wrapper/allocation is >=10% of complete Q1 time:
- build/use one preallocated C/C++/C-API harness against the same stable cuVS behavior;
- rerun only Q1_STRONG_V2.

If strong preallocated Q1 remains wrapper dominated or a clean device-local boundary cannot be established:
`R17_HOST_OR_WRAPPER_DOMINANT`
STOP.

Do not use persistent SINGLE_CTA as a substitute for MULTI_CTA strong Q1. Persistent may be used only as a launch-control if a recall-qualified SINGLE_CTA arm exists.

---

## 7. Stage F — bounded profiling only if unexplained GPU residual survives

Trigger only after D/E.

At most:
- one NSYS capture with clearly separated Q1_STRONG_V2 and matched Q32 ranges;
- two NCU exact traversal targets: one Q1, one Q32.

Query SM89-supported metrics first.

Classify evidence into:
- utilization/eligible warps
- memory/dependency
- compute/distance
- launch/runtime.

No SASS/NVBit.

Do not equate:
- low occupancy with mechanism headroom;
- long scoreboard with graph dependency;
- DRAM bytes with a cache opportunity.

If necessary distance math dominates:
`R17_DISTANCE_COMPUTE_DOMINANT`
STOP.

If a GPU-local low-concurrency traversal/state residual is supported, proceed to holdout.

---

## 8. Stage G — sealed holdout

Only now open queries 256..511.

No tuning after opening.

Rerun only:
- Q1_STRONG_V2
- the single preselected comparator that motivated the residual
- same profiling/accounting only if needed to confirm direction; no new metric hunt.

If holdout does not reproduce:
`R17_RESULT_MIXED_NEEDS_REVIEW`.

If it reproduces:
`R17_LOW_CONCURRENCY_TRAVERSAL_RESIDUAL_READY_FOR_REVIEW`.

Even this label does not authorize 174 or hardware.

---

## 9. Forbidden

Do not:
- lower recall below 0.95
- inspect holdout during quality tuning
- build more than one new NN_DESCENT index
- change graph degree/intermediate degree
- switch dataset
- add compression/filtering/dynamic update
- run Jasper as a replacement benchmark
- do exhaustive search_width/itopk sweeps
- use second model/dataset
- run NVBit/SASS
- start Accel-Sim/node174
- design hardware
- reopen Round16.

---

## 10. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R17R1_GRAPH_SEARCH_109_V2/`

Include:
- README.md
- PARENT_AUTHORITY.json
- SOURCE_BASELINE_AUDIT.md
- QUALITY_EXTENSION_IVFPQ.tsv
- NNDESCENT_INDEX_RECEIPT.json if triggered
- QUALITY_NNDESCENT.tsv if triggered
- STRONG_CANDIDATE_FREEZE.md
- FORMAL_Q1_TIMING.tsv if quality qualifies
- MATCHED_Q1_Q32.tsv if triggered
- WRAPPER_ACCOUNTING.md
- PROFILE_SUMMARY.tsv if triggered
- HOLDOUT_TIMING.tsv if triggered
- FINAL_DECISION.md
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Large index/raw remains on node164.

---

## 11. Closure

Release GPU lock after every campaign.
Commit/push/fetch-back exact SHA/tree.
Clean worktree.
STOP.

Do not auto-start another research problem even if unattended time remains.
