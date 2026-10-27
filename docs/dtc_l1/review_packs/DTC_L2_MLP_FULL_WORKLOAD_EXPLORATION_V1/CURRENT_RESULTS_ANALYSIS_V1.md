# Current results: three-agent read-only analysis

The campaign remains active. Agent A analyzed uniform-parameter cycles; Agent D analyzed counters and timing associations; Agent C analyzed workload coverage and completion bias. No analysis started a model or changed original accepted/negative/repair identities.

A and C use the same fixed 2026-10-27 19:32:14 CST snapshot: 117 accepted cells = 111 new strict/archive/native-restore PASS plus six exact P0 references, out of350. D's paired traffic snapshot is separately labelled19:28:08; the targeted raw-reason addendum was obtained later from the same immutable closed identities. These timestamps are not combined into one atomic live count.

| Uniform DH variant | Same-input DH-P0 pairs /35 | DH self-speedup GM |
|---|---:|---:|
| E384 |10|1.000000000|
| E768 |10|1.000000000|
| M8 |9|0.999533309|
| M16 |9|1.000000000|
| Q64 |9|1.000000000|
| Q128 |10|1.000000000|
| F128 |8|1.000000000|
| F256 |8|1.000000000|

There are73 paired variant cells:72 have exactly equal integer cycles to their DH-P0; heartwall M8 increases from8551 to8587 cycles. Distinct row populations are not a configuration ranking. The common population across all eight variants is only five inputs: BlackScholes, gaussian, heartwall, histogram and lud. Their common-population M8 GM is0.999160114; the other seven are1.0. These five inputs represent only0.11365% of the frozen35 expected instruction population. The shortest nine inputs have76/90 cells accepted, while the longest eight have0/80; this is strong completion censoring, not a basis to exclude or replace any workload.

P0 CH/DH has13/35 pairs, GM0.987113633 and median1.008484898, with DTC8 faster/5 slower. It includes the three diagnostic P0 references ATAX/MVT/BICG and ten newly completed input pairs. It is not a full35 suite result. Non-P0 CH matching is currently absent, so same-configuration DTC relative improvement remains unproven.

The heartwall counter comparison separates facts from mechanism inference. Merge failures fall241→207/144 for M8/M16; cycles respectively worsen by36/remain equal. Accepted read sectors, misses and DRAM reads are unchanged. D's70 matched traffic pairs all preserve these three volumes. Six of the ten paired programs issue zero DRAM read atoms. These observations explain why current short-input results do not yet test the long-input DRAM-pressure hypothesis.

Targeted closed raw verifies that L2 failure reasons exist beyond the frozen proof parser: heartwall MSHR_MERGE_ENRTY_FAIL=241/207/144, and vectorAdd DH-E384 has5,486,196 MISS_QUEUE_FULL attempts across reads/writes. vectorAdd lacks matched DH-P0 at the evidence snapshot, so no speedup is inferred. gpu_stall_dramfull is a label for ICNT-to-memory-subpartition admission stalls, not L2-to-DRAM queue latency. See [counter clarification](COUNTER_CLARIFICATION_V1.md).

Among the12 formerly incomplete old quads, this snapshot has new strict performance evidence for bfs(four cells), scalarProd(one) and vectorAdd(two); none of the12 yet has a DH self-speedup pair. Prior repair correctness is never substituted. The other original missing/negative identities remain preserved.

The background sole owner continues the complete35-input scan. No uniform winner is selected from this partial subset, no pending input is dropped, and no old PQ/PS result is substituted for a different L2 factor. ATAX/MVT/BICG/3MM/GEMM variants remain pending in this snapshot. Full35 terminal evidence, extensions/combinations and matched CH validation remain necessary.

Detailed reports: [A cycles](agents/A/current_results_analysis_v1/REPORT.md), [D counters V2](agents/D/current_results_analysis_v1/REPORT_V2.md), [C coverage](agents/C/current_results_analysis_v1/REPORT.md). Each includes full input identities, exact source paths and SHA evidence.
