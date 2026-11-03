# ATAX, MVT and BICG: matched F128 synthesis

These three fixed diagnostic cases now have all four closed sources: CH-P0, CH-F128, DH-P0 and DH-F128. The data retains original-reference aliases and the new first16 identities. This is a three-case analysis, not the first8 or32/35-program population. F256 is still pending for these inputs, so this does not select a uniform F configuration.

| Program | S_CH | S_DH | I=S_DH/S_CH | DH cycles above matched CH | CH kernel-cycle deltas | DH kernel-cycle deltas |
|---|---:|---:|---:|---:|---|---|
| ATAX | 0.951367 | 0.999548 | 1.050644 | 6.73% | [1452937, 331] | [14294, 123] |
| MVT | 1.039423 | 0.981743 | 0.944507 | 38.16% | [-1008477, 304] | [645835, -755] |
| BICG | 1.074957 | 0.982038 | 0.913561 | 19.40% | [0, -1833807] | [0, 524668] |

A speedup above1 means fewer cycles. I above1 is a relative change and does not mean DH is faster than its own P0 or than CH. ATAX is the direct counterexample: both designs regress, CH regresses more, and DH remains slower than CH. BICG changes are exactly K2; MVT and ATAX changes are mainly K1 with small real K2 changes. No small nonzero change is relabelled exact-zero.

## Revisiting the reported14%-32% DRAM-read gap

| Program | DH read atoms above CH atP0 | DH read atoms above CH atF128 | CH own read change | DH own read change |
|---|---:|---:|---:|---:|
| ATAX | 15.95% | 7.36% | +7.69% | -0.29% |
| MVT | 31.74% | 36.94% | -0.37% | +3.56% |
| BICG | 14.02% | 24.47% | -7.01% | +1.51% |

The original approximate14%-32% difference is reproduced in these exact P0 references. Matched F128 changes it in different directions; all three DH runs still issue more DRAM-read atoms and take more total cycles than CH. This is an observation, not proof that read volume alone caused the cycle gap. L2 input streams and filtering differ between CH and DH, so miss fractions are conditional on different request populations.

## Why the existing means do not prove complete L2-to-DRAM latency

| Program | CH P0 printed MRQ mean | CH F128 | DH P0 | DH F128 |
|---|---:|---:|---:|---:|
| ATAX | 412 | 553 | 745 | 1389 |
| MVT | 455 | 696 | 738 | 1366 |
| BICG | 526 | 807 | 791 | 1477 |

These raw diagnostics are cumulative, request-conditioned MRQ ages from DRAM-request construction to bank assignment, not complete L2->DRAM service/return or critical-path latency. MRQ mean rises in both designs for all three inputs, even though CH gets faster in MVT and BICG. A larger scheduler window and coupled credits can change where requests wait, their age/population and ordering. The table does not quantify an end-to-end delay increase caused by the14%-32% traffic gap. Other printed means retain the established sampling/fold/tail and population limitations; they are not summed or differenced into per-kernel latency.

## Facts, associations and remaining limits

All three nearly remove miss-queue-full retry attempts while entry-capacity retry attempts grow. MVT CH improves despite more aggregate reservation failures and ICNT-admission blockage; ATAX CH regresses despite fewer of those events. Therefore retry totals do not monotonically explain performance and are not occupancy or critical stall cycles. Entry capacity and per-address merge limits remain distinct. No resource-expansion speedup is predicted from these counts.

DH line-miss/tag-eviction improvements in MVT/BICG coexist with more downstream DRAM work; ATAX has more OO lower requests but slightly less DRAM work. These changes support investigating filtering/interleaving, useful concurrency, replacement and request dependencies, but do not isolate one cause. Mean PIB/service observations cannot rule out bursts, tails or local bottlenecks; unprinted counters remain missing.

ATAX tmp dependency and MVT independent output chains are inspected candidate-source properties, with capture-ELF/numerical-state binding limits retained. Frozen trace input identity, ordered kernels, instructions and grid scope are unchanged; source inspection is not a new numerical correctness certificate.

FR-FCFS64->128 also changes shared credits255->319. L2 capacity/MSHR/merge/missQ,850MHz DRAM and within-design L1 mechanisms stay fixed. CH PAPER_BASE commonPIB256 and DH PAPER_OO PIB128 differ; the rawDH common8 option is inactive for OO admission. Neither capacity nor physical area is matched. The old BICG f2b packet must be consumed with its frozen typed-field forward clarification4550.

The source quartet manifests, full input digests, RESULT/raw SHA and exact per-kernel deltas are in THREE_CASE_MATCHED_DIAGNOSIS.json. Detailed source/counter/latency boundaries remain in the three B packets and independent C reviews. This synthesis starts no simulation, changes no source or runtime identity, grants no new budget and does not release48 points or edit Englishv0.23. The first16 Goal remains active until all16 terminal and final review/publication.
