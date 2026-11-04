# Accepted-results refresh V4 — 21:38 CST frozen snapshot

UTC `2026-10-28T13:38:06.883166+00:00`: **322/350 primary accepted** (316 new +6 references),12 confirmed live,15 pending,1 original scan/M16 technical negative retained. **R2 separate accepted6,702,538 cycles**, excluded from every primary statistic. This directory is immutable; later results require a new version.

## Uniform profiles and populations

DH self = same-input accepted DH P0 / DH variant cycles. Fixed all-eight-profile intersection remains **31 programs**. Available populations differ and must not be ranked as final35 results. No non-P0 CH is accepted; CH speedups, variant CH/DH and relative DTC improvement remain unavailable.

| Profile | Available n/35 | GM | + / = / - | Missing | Fixed common31 GM |
|---|---:|---:|---:|---:|---:|
| E384 | 32/35 | 1.000874 | 5 / 21 / 6 | 3 | 1.000697 |
| E768 | 32/35 | 1.000874 | 5 / 21 / 6 | 3 | 1.000697 |
| M8 | 32/35 | 1.000280 | 5 / 20 / 7 | 3 | 1.000474 |
| M16 | 31/35 | 1.000994 | 5 / 21 / 5 | 4 | 1.000994 |
| Q64 | 32/35 | 0.997226 | 4 / 20 / 8 | 3 | 0.997271 |
| Q128 | 32/35 | 0.996854 | 4 / 20 / 8 | 3 | 0.996942 |
| F128 | 32/35 | 1.012595 | 7 / 19 / 6 | 3 | 1.008259 |
| F256 | 32/35 | 1.019138 | 7 / 19 / 6 | 3 | 1.011581 |

Per-suite available coverage and GM (fixed common populations and sign counts are also in JSON):

| Suite | E384 n / GM | E768 n / GM | M8 n / GM | M16 n / GM | Q64 n / GM | Q128 n / GM | F128 n / GM | F256 n / GM |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CUDA Samples | 9/9 / 1.000991 | 9/9 / 1.000991 | 9/9 / 0.999364 | 8/9 / 1.000000 | 9/9 / 1.000271 | 9/9 / 0.999935 | 9/9 / 1.037979 | 9/9 / 1.059559 |
| Parboil | 7/7 / 0.999835 | 7/7 / 0.999835 | 7/7 / 0.999758 | 7/7 / 0.999826 | 7/7 / 0.999840 | 7/7 / 1.000322 | 7/7 / 1.002002 | 7/7 / 1.003439 |
| PolyBench/GPU | 8/9 / 1.002529 | 8/9 / 1.002529 | 8/9 / 1.002864 | 8/9 / 1.004295 | 8/9 / 0.988787 | 8/9 / 0.987269 | 8/9 / 1.006401 | 8/9 / 1.007772 |
| Rodinia | 8/10 / 1.000000 | 8/10 / 1.000000 | 8/10 / 0.999190 | 8/10 / 0.999715 | 8/10 / 1.000000 | 8/10 / 1.000000 | 8/10 / 1.000000 | 8/10 / 1.000000 |

All319 previously accepted RESULT SHAs are unchanged. Full available/common populations, per-suite sign/missing counts, source bindings and every cell/RESULT SHA are retained in EVIDENCE.json. The common intersection excludes SYRK, hybridsort, lavamd, scan; excluded means incomplete intersection, not discarded scientific data.

## Newly accepted since V3

| Program / profile / cell | Cycles | DH self | Counter observation |
|---|---:|---:|---|
| cutcp / M8 / DH | 4,490,473 | 1.000000 | DRAM reads 0; L2 reads 1605996; reservation fails 0; last MRQ None |
| cutcp / Q128 / DH | 4,490,473 | 1.000000 | DRAM reads 0; L2 reads 1605996; reservation fails 0; last MRQ None |
| cutcp / Q64 / DH | 4,490,473 | 1.000000 | DRAM reads 0; L2 reads 1605996; reservation fails 0; last MRQ None |

**Facts:** newly accepted CUTCP M8/Q64/Q128 all equal DH P0 at4,490,473 cycles,1.0x. All eight non-P0 DH variants are now paired. Recorded DRAM reads, L2 read misses, reservation failures and dramfull remain explicitly0; L2 reads1,605,996; MRQ missing. The three RESULT SHA values exactly match Main's supplied receipts. No prior accepted result changed.

CUTCP's completion grows the all-profile intersection from 30 to 31. Available M8/Q64/Q128 each add one neutral point; the other available sets stay unchanged. Every fixed-common GM is recomputed on the new common set; do not call the population-induced change a new performance effect on prior programs.

Hybridsort DH P0 is now18,563,916 cycles. Accepted variants currently paired for hybridsort: 0/8. Completing its baseline alone does not invent variant data or complete its CH/DH comparison.

## Per-program sensitivity and major signs

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
| cutcp / Parboil | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
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

The following extrema are listed separately for each uniform profile; they are never combined into an oracle GM.

| Uniform profile | Strongest two positives | Strongest two negatives |
|---|---|---|
| E384 | ATAX 1.028813x, vectorAdd 1.008811x | convolutionSeparable 0.993961x, MVT 0.994968x |
| E768 | ATAX 1.028813x, vectorAdd 1.008811x | convolutionSeparable 0.993961x, MVT 0.994968x |
| M8 | 2DCONV 1.036346x, ATAX 1.014056x | BICG 0.967226x, scan 0.994288x |
| M16 | 2DCONV 1.036346x, BICG 1.012241x | ATAX 0.980088x, srad_v1 0.997719x |
| Q64 | vectorAdd 1.004331x, convolutionSeparable 1.002851x | BICG 0.961800x, MVT 0.980552x |
| Q128 | convolutionSeparable 1.014358x, 2DCONV 1.002368x | ATAX 0.943917x, MVT 0.977938x |
| F128 | convolutionSeparable 1.187151x, scan 1.156693x | MVT 0.981743x, BICG 0.982038x |
| F256 | convolutionSeparable 1.422263x, scan 1.283635x | vectorAdd 0.919938x, MVT 0.988434x |

F128/F256 have the same sign counts (7 positive,6 negative), **different program sets**: vectorAdd/GESUMMV are positive under F128 but negative under F256; ATAX/scalarProd have the reverse signs. These cases are descriptive observations of uniform configurations, not a per-program best suite.

## Counter associations and separate supplemental

F256 helps convolutionSeparable1.422263x,scan1.283635x and2DCONV1.078012x while vectorAdd regresses0.919938x. Faster convolutionSeparable/scan coexist with higher last MRQ averages321→905 and184→628. vectorAdd has unchanged DRAM reads and approximately51% fewer reservation-fail events despite slower completion. These events are not critical-path cycle attribution.

ATAX E384/E7681.028813x and F2561.017823x coexist with a Q128 regression0.943917x; MVT remains mostly flat/negative, BICG M16 improves1.012241x while M8 regresses0.967226x. 3MM/GEMM/particlefilter_naive are flat across their accepted DH scans. 3MM/GEMM DRAM counters are explicitly0, not missing: percentage null means zero denominator; MRQ is missing. Such simulator trace/kernel statistics do not prove zero DRAM access by the real application. GEMM and Parboil sgemm retain different input identities.

R2 scan/M16 accepted independently at6,702,538 cycles, descriptive DH P0/R2=0.992011x. It is not included in M16's 31 primary pairs or common31. Original M16 remains unaccepted. R2 has nearly unchanged DRAM reads21,712,700→21,712,552 and last MRQ184→183; these counters do not explain causally its slight regression. The preserved lineage/certificate/RESULT/archive SHA are in EVIDENCE.json. Only declared expected physics option values can be compared to the original failed spec; the failed run has no accepted actual-effective-options verification.

**Cannot confirm:** final35 winning configuration, relative advantage over CH, queue occupancy, latency-critical path or causality. L2 counters follow the existing complete-single-stream header/binding scope; otherwise whole-declared-trace values stay null. DRAM is global cumulative; last MRQ is not a weighted application average, and dramfull is ICNT-to-memory blockage. Missing MSHR reasons stay missing. No instrumentation or new experiment is authorized by this report.

## Reproduction and publication boundary

`collect.py` called existing qualified generator SHA `9ad9cdf8db29eb062f8053b51b3396a1bac6ff9132f6ad0d89ac64aac58786d7` once, writing only this new directory. PRIMARY_SNAPSHOT.json records coherent source SHA per file and live PID identity evidence. `analyze.py` reused the frozen V3 source snapshot for the delta and performs JSON arithmetic only. No Git access, raw-log scan, test rerun, native restore, controller/registry/source modification, model launch or budget action occurred. Main reviews and publishes via the existing sole publisher; this analysis is not another controller.
