# Accepted-results refresh — frozen 2026-10-28 18:09 CST

**V2 correction:** Reuses the exact V1 18:09 CST source snapshot. Only F128/F256 set wording and the scope of the failed-M16 option comparison were corrected; no new data, collector, simulation or tests. V1 preimage remains intact. READY/publication should reference this V2 directory.

Snapshot UTC `2026-10-28T10:09:38.618532+00:00`. **Primary 316/350 accepted** = 310 new runs + 6 references; 12 confirmed live, 21 pending, and original scan/M16 unaccepted technical negative. **Supplemental R2 accepted separately: 6,702,538 cycles.** This is one read-only analysis invocation, not an analysis daemon. Counts are frozen, not live promises.

## Uniform DH sensitivity and coverage

DH self speedup = DH P0 / DH variant. Fixed intersection across all eight profiles is **30 programs**; available sets vary. No accepted non-P0 CH exists, so CH speedup, variant CH/DH and relative DTC improvement are unavailable. Neither table ranks a final 35-program winner.

| Profile | Available n/35 | GM | + / = / - | Missing | Fixed common30 GM |
|---|---:|---:|---:|---:|---:|
| E384 | 32/35 | 1.000874 | 5 / 21 / 6 | 3 | 1.000721 |
| E768 | 32/35 | 1.000874 | 5 / 21 / 6 | 3 | 1.000721 |
| M8 | 31/35 | 1.000289 | 5 / 19 / 7 | 4 | 1.000490 |
| M16 | 30/35 | 1.001027 | 5 / 20 / 5 | 5 | 1.001027 |
| Q64 | 31/35 | 0.997136 | 4 / 19 / 8 | 4 | 0.997180 |
| Q128 | 31/35 | 0.996752 | 4 / 19 / 8 | 4 | 0.996840 |
| F128 | 32/35 | 1.012595 | 7 / 19 / 6 | 3 | 1.008535 |
| F256 | 31/35 | 1.019762 | 7 / 18 / 6 | 4 | 1.011969 |

All previous315 accepted RESULT SHAs match the fixed published315 anchor. The only newly accepted primary cell in this snapshot is CUTCP DH-F128. Full per-suite populations, GMs, sign counts and every missing identity are in ANALYSIS.json; the following suite table preserves coverage explicitly.

| Suite | E384 n / GM | E768 n / GM | M8 n / GM | M16 n / GM | Q64 n / GM | Q128 n / GM | F128 n / GM | F256 n / GM |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CUDA Samples | 9/9 / 1.000991 | 9/9 / 1.000991 | 9/9 / 0.999364 | 8/9 / 1.000000 | 9/9 / 1.000271 | 9/9 / 0.999935 | 9/9 / 1.037979 | 9/9 / 1.059559 |
| Parboil | 7/7 / 0.999835 | 7/7 / 0.999835 | 6/7 / 0.999718 | 6/7 / 0.999797 | 6/7 / 0.999813 | 6/7 / 1.000375 | 7/7 / 1.002002 | 6/7 / 1.004013 |
| PolyBench/GPU | 8/9 / 1.002529 | 8/9 / 1.002529 | 8/9 / 1.002864 | 8/9 / 1.004295 | 8/9 / 0.988787 | 8/9 / 0.987269 | 8/9 / 1.006401 | 8/9 / 1.007772 |
| Rodinia | 8/10 / 1.000000 | 8/10 / 1.000000 | 8/10 / 0.999190 | 8/10 / 0.999715 | 8/10 / 1.000000 | 8/10 / 1.000000 | 8/10 / 1.000000 | 8/10 / 1.000000 |

## Every frozen program, one uniform profile per column

All ratios below are DH-self. `—` means not yet paired accepted, never 1.0 or zero. The machine-readable pairs retain full input/binding SHA, suite, cohort, UUID, cycles, RESULT path/SHA, source Core/Framework/binary, scope and counters. No per-program best values are combined into a GM.

| Program / suite | E384 | E768 | M8 | M16 | Q64 | Q128 | F128 | F256 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BlackScholes / CUDA Samples | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| convolutionSeparable / CUDA Samples | 0.993961 | 0.993961 | 1.000000 | 1.000000 | 1.002851 | 1.014358 | 1.187151 | 1.422263 |
| fastWalshTransform / CUDA Samples | 0.999849 | 0.999849 | 1.000000 | 1.000000 | 0.999445 | 0.998830 | 0.999649 | 0.997723 |
| histogram / CUDA Samples | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| mergeSort / CUDA Samples | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| scalarProd / CUDA Samples | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.998952 | 1.004467 |
| scan / CUDA Samples | 1.006375 | 1.006375 | 0.994288 | — | 0.995834 | 0.994126 | 1.156693 | 1.283635 |
| transpose / CUDA Samples | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| vectorAdd / CUDA Samples | 1.008811 | 1.008811 | 1.000000 | 1.000000 | 1.004331 | 0.992251 | 1.019957 | 0.919938 |
| bfs / Parboil | 1.000000 | 1.000000 | 0.999997 | 0.999997 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| cutcp / Parboil | 1.000000 | 1.000000 | — | — | — | — | 1.000000 | — |
| histo / Parboil | 0.998847 | 0.998847 | 0.998270 | 0.998775 | 0.997651 | 1.001022 | 1.013203 | 1.023415 |
| mri-q / Parboil | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.001231 | 1.001231 | 1.000886 | 1.000886 |
| sad / Parboil | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| sgemm / Parboil | 1.000000 | 1.000000 | 0.999968 | 0.999968 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| stencil / Parboil | 1.000000 | 1.000000 | 1.000073 | 1.000042 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| 2DCONV / PolyBench/GPU | 1.002246 | 1.002246 | 1.036346 | 1.036346 | 1.001645 | 1.002368 | 1.057515 | 1.078012 |
| 3DCONV / PolyBench/GPU | 0.998748 | 0.998748 | 1.006512 | 1.006512 | 0.998146 | 0.997830 | 0.997599 | 0.994891 |
| 3MM / PolyBench/GPU | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| ATAX / PolyBench/GPU | 1.028813 | 1.028813 | 1.014056 | 0.980088 | 0.986344 | 0.943917 | 0.999548 | 1.017823 |
| BICG / PolyBench/GPU | 0.994996 | 0.994996 | 0.967226 | 1.012241 | 0.961800 | 0.982571 | 0.982038 | 0.993156 |
| GEMM / PolyBench/GPU | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| GESUMMV / PolyBench/GPU | 1.000868 | 1.000868 | 1.000000 | 1.000000 | 0.982493 | 0.994925 | 1.035131 | 0.992797 |
| MVT / PolyBench/GPU | 0.994968 | 0.994968 | 1.000052 | 1.000039 | 0.980552 | 0.977938 | 0.981743 | 0.988434 |
| SYRK / PolyBench/GPU | — | — | — | — | — | — | — | — |
| dwt2d / Rodinia | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| gaussian / Rodinia | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| heartwall / Rodinia | 1.000000 | 1.000000 | 0.995808 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| hybridsort / Rodinia | — | — | — | — | — | — | — | — |
| lavamd / Rodinia | — | — | — | — | — | — | — | — |
| lud / Rodinia | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| myocyte / Rodinia | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| particlefilter_float / Rodinia | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| particlefilter_naive / Rodinia | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| srad_v1 / Rodinia | 1.000000 | 1.000000 | 0.997719 | 0.997719 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| Uniform profile | Two strongest observed positives | Two strongest observed negatives |
|---|---|---|
| E384 | ATAX 1.028813x, vectorAdd 1.008811x | convolutionSeparable 0.993961x, MVT 0.994968x |
| E768 | ATAX 1.028813x, vectorAdd 1.008811x | convolutionSeparable 0.993961x, MVT 0.994968x |
| M8 | 2DCONV 1.036346x, ATAX 1.014056x | BICG 0.967226x, scan 0.994288x |
| M16 | 2DCONV 1.036346x, BICG 1.012241x | ATAX 0.980088x, srad_v1 0.997719x |
| Q64 | vectorAdd 1.004331x, convolutionSeparable 1.002851x | BICG 0.961800x, MVT 0.980552x |
| Q128 | convolutionSeparable 1.014358x, 2DCONV 1.002368x | ATAX 0.943917x, MVT 0.977938x |
| F128 | convolutionSeparable 1.187151x, scan 1.156693x | MVT 0.981743x, BICG 0.982038x |
| F256 | convolutionSeparable 1.422263x, scan 1.283635x | vectorAdd 0.919938x, MVT 0.988434x |

## Strongest observed cases — descriptive partial results

F256 helps convolutionSeparable **1.422263x**, scan **1.283635x**, 2DCONV **1.078012x**; it regresses vectorAdd **0.919938x**, MVT **0.988434x**, BICG **0.993156x**. F128 and F256 have the same positive/negative counts (7/6), but different program sets: vectorAdd and GESUMMV are positive for F128 and negative for F256, while ATAX and scalarProd are negative for F128 and positive for F256; adding flat CUTCP changes its available GM from 1.013004 to **1.012595**, without changing any existing result or its common30 GM **1.008535**. F256 remains 1.019762 on available31 and 1.011969 on common30.

ATAX E384/E768 are 1.028813x, F256 1.017823x, but Q128 0.943917x. MVT remains mostly flat-to-negative; BICG M16 is 1.012241x while M8 is 0.967226x. 3MM/GEMM and particlefilter_naive are flat across their complete DH scans. Larger entries or queues are not universally beneficial.

## New CUTCP and separate R2

**Fact — CUTCP F128:** 4,490,473 -> 4,490,473 cycles, exactly 1.0x. Its recorded DRAM reads, L2 read misses, reservation failures and dramfull are all explicitly zero; L2 reads stay 1,605,996; MRQ average is missing. Percentage nulls on zero counters mean zero denominator, not missing counts. F256 is still RUNNING_CONFIRMED at acquisition; M16 also running and M8/Q64/Q128 pending. No F256 value is inferred.

**Fact — supplemental scan R2:** UUID `438ec9bb-077f-4eb5-a9df-5472adcaa996`, strict accepted 6,702,538 cycles, the same 270 expected physics option values declared by the frozen specs, with the same input/Core/Framework/binary identity; this is a declared-spec comparison, not validation of the failed M16 run's actual effective options. Its separately descriptive DH P0/R2 is **0.992011x**, with P0 6,648,993 cycles. Original M16 remains absent/unaccepted in primary; no union is authorized and primary M16 still has30 pairs, not31. R2's archive contains23 independently verified entries; raw/RESULT/archive/lineage SHAs are in ANALYSIS.json and SUPPLEMENTAL_SNAPSHOT.json.

**Association — R2 vs P0:** DRAM reads are nearly unchanged (21,712,700 -> 21,712,552), L2 reads 21,859,084 -> 21,852,796, and the last MRQ average 184 -> 183. This does not identify why the independent M16 run is slightly slower. Its IO-qualified new launch and preserved negative lineage establish an independent result, not a repair correctness replacement.

## What counters do and do not establish

Observed F improvements often coexist with *higher* last-printed MRQ averages: convolutionSeparable F256 321 -> 905 and scan 184 -> 628. vectorAdd F256 has unchanged DRAM reads and roughly51% fewer reservation-fail events yet slower completion. ATAX F256 has 2.213% fewer DRAM reads and 3.100% fewer reservation-fail events with 1.017823x speedup; MVT/BICG F256 still regress. These are associations, not causal cycle decomposition or proof of queue occupancy/criticality. Specific MSHR reasons are absent, not zero.

3MM/GEMM DRAM counters explicitly remain0; their percent changes are undefined zero-denominator values. MRQ is missing. Kernel/preloaded trace statistics cannot establish zero DRAM traffic for the real application. GEMM (PolyBench) and sgemm (Parboil) retain different input identities.

The current pattern supports the already registered V3 rationale for full35 entries×FRFCFS, merge×sending/queue and wide/ablation tests; flat OFAT does not disprove interaction. This report adds no proposal, changes no stage gate and selects no final configuration. Required full35 parent evidence, distinct moderate/high CH/DH validation, original-negative disposition and the existing budget/owner remain authoritative.

## Reproduction and provenance

`collect.py` called qualified generator SHA `9ad9cdf8db29eb062f8053b51b3396a1bac6ff9132f6ad0d89ac64aac58786d7` once, with every JSON source SHA retained in PRIMARY_SNAPSHOT.json. `analyze_refresh.py` only reads frozen JSON plus the fixed315 anchor (commit280abe32e1090366cfaabaf5895662300c2f9f27). Request-time GitHEAD was2b545e7f54b0111a17c1ee1e5d124bd9acf1ee3d; this independent output is not yet a new Git commit. Main alone publishes it.

Stream scope follows the existing header/binding qualification: whole-declared-trace L2 counters only under complete single-stream scope, otherwise null; DRAM counters are global cumulative. No huge raw log, native restore or prior test was rerun. Source files are individually coherent snapshots, not one atomic transaction across the controller. No live registry/controller/source or scientific identity was modified. `EVIDENCE.json` is the canonical machine-readable handoff; ANALYSIS.json is an identical alias. This directory is a frozen one-shot snapshot; subsequent results belong in a new directory, never by rerunning collect.py here.
