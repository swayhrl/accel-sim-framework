# scan: six closed sources and 33-kernel phase decomposition

**Finding:** CH and DH both obtain substantial F128/F256 speedups. Most benefit is shared system improvement; F128 slightly reduces DTC relative advantage, while F256 adds only a small relative improvement. F256 CH/DH speedups are 1.272539/1.283635 and I=1.008719. Same-F CH/DH=1.018102, favoring DH modestly. This is one frozen input, not a selected-suite GM.

All six sources are naturally closed accepted results; both new CH runs passed an independent frozen read-only strict/true164/native-restore audit. No live input or controller observation was consumed as performance, no new model was launched, and no original identity, source, budget, registry, controller, owner or manuscript was changed.

## Identity and actual 33-kernel contract

Full digest `6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39`. Actual ordered full-body qualification and strict/raw stats:33kernels,1,963,460,720retired active-thread instructions and 166,608 CTAs. Each kernel's own grid/block/name/instruction count is verified, including fresh bounded 4096-byte header reads. There are 17 LocalScan, 8 Partials and 8 UniformUpdate launches, not 11 identical triplets: the initial 10 LocalScan captures have the same grid/block but differing instruction counts, followed by the actual remaining partial/update/local sequence. No native full-application or capture ELF/numeric completeness is newly certified.

Fixed Core `9eedb3131937748f0492fa83aad37d3691118d70`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`, binary SHA `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`. Original CH-P0/DH-P0/DH-F128/DH-F256 are exact original-index full-digest/cell/profile matches, including disclosed inherited aliases. New CH roles remain STAGEII_AUTHORIZED_CH. No R2/IR/EP/PQPS replacement occurs.

## Matched performance

| Profile | CH cycles | DH cycles | S_CH | S_DH | CH_F/DH_F | I=S_DH/S_CH |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | 6,710,840 | 6,648,993 | 1 | 1 | 1.009302 | 1 |
| F128 | 5,695,578 | 5,748,280 | 1.178254 | 1.156693 | 0.990832 | 0.981700 |
| F256 | 5,273,582 | 5,179,817 | 1.272539 | 1.283635 | 1.018102 | 1.008719 |

F128 CH gains 17.8254% in reciprocal-cycle speed versus DH 15.6693%, yielding I 0.981700 and DH 0.9253% more cycles than CH. F256 CH gains 27.2539% versus DH 28.3635%, yielding I1.008719. Do not describe the 28.36% DH self-speedup as 28.36% improvement relative to CH: the relative increment is 0.8719%. No per-program best-F choice is used to create a unified GM.

## Every captured kernel: actual shape/instructions/cycles

Symbols are actual trace/strict names. Phase labels are fixed source candidate mappings: LocalScan=`scanExclusiveShared`, Partials=`scanExclusiveShared2`, UniformUpdate=`uniformUpdate`. Source mapping is conditional, while kernel identity/order/shape/instruction/cycles below are trace/runtime evidence.

| K | Kernel symbol | Candidate phase | Grid/block | Instructions | CTAs | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 52,822,016 | 6,656 | 214,546 | 175,972 | 169,513 | 206,833 | 176,694 | 168,728 |
| 2 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 66,453,504 | 6,656 | 273,484 | 208,678 | 208,420 | 247,826 | 212,954 | 207,112 |
| 3 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 81,788,928 | 6,656 | 260,878 | 227,495 | 211,007 | 273,596 | 224,689 | 211,193 |
| 4 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 97,124,352 | 6,656 | 267,308 | 229,112 | 209,674 | 267,065 | 226,699 | 210,842 |
| 5 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 112,459,776 | 6,656 | 268,977 | 219,321 | 211,016 | 264,588 | 233,366 | 210,364 |
| 6 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 127,795,200 | 6,656 | 274,844 | 225,920 | 211,001 | 276,714 | 232,459 | 204,455 |
| 7 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 103,620,608 | 6,656 | 269,944 | 223,665 | 204,942 | 265,487 | 224,567 | 202,215 |
| 8 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 104,099,840 | 6,656 | 267,462 | 227,116 | 212,633 | 259,955 | 230,722 | 206,342 |
| 9 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 104,579,072 | 6,656 | 267,977 | 228,851 | 208,896 | 258,985 | 229,831 | 202,482 |
| 10 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 104,579,072 | 6,656 | 268,745 | 224,844 | 212,141 | 261,709 | 231,143 | 209,908 |
| 11 | _Z20scanExclusiveShared2PjS_S_jj | Partials | [26, 1, 1]/[256, 1, 1] | 279,552 | 26 | 30,675 | 30,873 | 30,384 | 30,895 | 30,989 | 30,671 |
| 12 | _Z13uniformUpdateP5uint4Pj | UniformUpdate | [6656, 1, 1]/[256, 1, 1] | 34,098,688 | 6,656 | 238,637 | 202,727 | 184,422 | 232,270 | 189,314 | 187,064 |
| 13 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 104,579,072 | 6,656 | 280,334 | 236,573 | 222,207 | 280,616 | 237,545 | 204,398 |
| 14 | _Z20scanExclusiveShared2PjS_S_jj | Partials | [26, 1, 1]/[256, 1, 1] | 339,456 | 26 | 30,959 | 30,722 | 30,902 | 30,738 | 30,796 | 30,769 |
| 15 | _Z13uniformUpdateP5uint4Pj | UniformUpdate | [6656, 1, 1]/[256, 1, 1] | 34,098,688 | 6,656 | 223,870 | 197,528 | 187,734 | 225,166 | 199,891 | 176,605 |
| 16 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 104,579,072 | 6,656 | 273,649 | 234,893 | 218,123 | 266,800 | 239,762 | 216,623 |
| 17 | _Z20scanExclusiveShared2PjS_S_jj | Partials | [26, 1, 1]/[256, 1, 1] | 399,360 | 26 | 30,816 | 30,904 | 30,703 | 31,055 | 30,980 | 30,997 |
| 18 | _Z13uniformUpdateP5uint4Pj | UniformUpdate | [6656, 1, 1]/[256, 1, 1] | 34,098,688 | 6,656 | 230,341 | 197,771 | 186,400 | 233,697 | 202,623 | 181,854 |
| 19 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 104,579,072 | 6,656 | 275,328 | 232,344 | 212,648 | 282,584 | 234,018 | 200,787 |
| 20 | _Z20scanExclusiveShared2PjS_S_jj | Partials | [26, 1, 1]/[256, 1, 1] | 459,264 | 26 | 30,948 | 30,998 | 30,761 | 30,968 | 31,028 | 30,778 |
| 21 | _Z13uniformUpdateP5uint4Pj | UniformUpdate | [6656, 1, 1]/[256, 1, 1] | 34,098,688 | 6,656 | 230,058 | 201,835 | 185,912 | 227,352 | 199,012 | 180,637 |
| 22 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 104,579,072 | 6,656 | 287,377 | 235,516 | 217,089 | 267,843 | 237,895 | 205,951 |
| 23 | _Z20scanExclusiveShared2PjS_S_jj | Partials | [26, 1, 1]/[256, 1, 1] | 519,168 | 26 | 30,867 | 31,031 | 30,962 | 30,995 | 31,007 | 30,718 |
| 24 | _Z13uniformUpdateP5uint4Pj | UniformUpdate | [6656, 1, 1]/[256, 1, 1] | 34,098,688 | 6,656 | 229,294 | 201,474 | 182,404 | 246,643 | 206,810 | 177,561 |
| 25 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 104,579,072 | 6,656 | 290,443 | 240,169 | 212,478 | 285,242 | 236,602 | 213,224 |
| 26 | _Z20scanExclusiveShared2PjS_S_jj | Partials | [26, 1, 1]/[256, 1, 1] | 430,976 | 26 | 31,013 | 30,934 | 30,818 | 31,182 | 31,028 | 31,195 |
| 27 | _Z13uniformUpdateP5uint4Pj | UniformUpdate | [6656, 1, 1]/[256, 1, 1] | 34,098,688 | 6,656 | 239,031 | 197,177 | 178,730 | 233,310 | 207,510 | 188,443 |
| 28 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 104,579,072 | 6,656 | 286,494 | 237,208 | 208,456 | 276,791 | 243,519 | 204,263 |
| 29 | _Z20scanExclusiveShared2PjS_S_jj | Partials | [26, 1, 1]/[256, 1, 1] | 432,848 | 26 | 31,335 | 30,953 | 30,953 | 31,118 | 31,157 | 31,038 |
| 30 | _Z13uniformUpdateP5uint4Pj | UniformUpdate | [6656, 1, 1]/[256, 1, 1] | 34,098,688 | 6,656 | 219,231 | 201,681 | 179,398 | 242,290 | 200,603 | 180,181 |
| 31 | _Z19scanExclusiveSharedP5uint4S0_j | LocalScan | [6656, 1, 1]/[256, 1, 1] | 104,579,072 | 6,656 | 285,042 | 239,233 | 213,168 | 284,235 | 234,349 | 209,229 |
| 32 | _Z20scanExclusiveShared2PjS_S_jj | Partials | [26, 1, 1]/[256, 1, 1] | 434,720 | 26 | 31,247 | 31,230 | 31,223 | 31,280 | 31,250 | 30,943 |
| 33 | _Z13uniformUpdateP5uint4Pj | UniformUpdate | [6656, 1, 1]/[256, 1, 1] | 34,098,688 | 6,656 | 239,686 | 200,830 | 178,464 | 233,165 | 207,468 | 172,247 |

| SUM | Instructions | CTAs | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| All33 | 1,963,460,720 | 166,608 | 6,710,840 | 5,695,578 | 5,273,582 | 6,648,993 | 5,748,280 | 5,179,817 |

All 33 cycle sums exactly equal their accepted whole-replay cycles. Different LocalScan instruction counts and the initial sequence are preserved; no aggregation substitutes an assumed repeated triplet.

## Phase cycle contributions

| Candidate phase | Launches | Instructions | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LocalScan | 17 | 1,687,375,872 | 4,612,832 | 3,846,910 | 3,563,412 | 4,526,869 | 3,886,814 | 3,488,116 |
| Partials | 8 | 3,295,344 | 247,860 | 247,645 | 246,706 | 248,231 | 248,235 | 247,109 |
| UniformUpdate | 8 | 272,789,504 | 1,850,148 | 1,601,023 | 1,463,464 | 1,873,893 | 1,613,231 | 1,444,592 |

| Design | Variant | Phase | Cycle delta vs P0 | Share of total saved cycles % |
| --- | --- | --- | --- | --- |
| CH | F128 | LocalScan | -765,922 | 75.440822 |
| CH | F128 | Partials | -215 | 0.021177 |
| CH | F128 | UniformUpdate | -249,125 | 24.538001 |
| CH | F256 | LocalScan | -1,049,420 | 73.015422 |
| CH | F256 | Partials | -1,154 | 0.080292 |
| CH | F256 | UniformUpdate | -386,684 | 26.904286 |
| DH | F128 | LocalScan | -640,055 | 71.060926 |
| DH | F128 | Partials | 4 | -0.000444 |
| DH | F128 | UniformUpdate | -260,662 | 28.939518 |
| DH | F256 | LocalScan | -1,038,753 | 70.703102 |
| DH | F256 | Partials | -1,122 | 0.076369 |
| DH | F256 | UniformUpdate | -429,301 | 29.220529 |

F256 CH saves 1,437,258 cycles: LocalScan 1,049,420, Partials 1,154, UniformUpdate 386,684. DH saves 1,469,176: LocalScan 1,038,753, Partials 1,122, UniformUpdate 429,301. LocalScan and UniformUpdate dominate both designs' gains; partial-sum stages are a very small contributor. DH F128 Partials slightly regress by 4 cycles and remain present. These shares are arithmetic decomposition of measured cycles, not causal attribution to a particular counter.

## Traffic and retry evidence with explicit endpoints

L2 GLOBAL accepted/miss counts are 32-byte sectors; accepted excludes retry events and misses=MISS+SECTOR_MISS. DRAM data values are issued 32-byte atoms across 20 controllers. All-L2 retries and ICNT blocked admission are events, not occupancy or critical-path stall time. The final additive stream0 snapshot covers all 33 kernels and is not added to earlier cumulative snapshots.

| Counter | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- |
| L2 GLOBAL accepted read sectors32B | 21,861,372 | 21,874,304 | 21,874,120 | 21,859,084 | 21,871,544 | 21,875,344 |
| L2 GLOBAL read misses32B | 21,712,692 | 21,712,576 | 21,712,848 | 21,712,700 | 21,711,132 | 21,712,484 |
| DRAM reads32B | 21,712,692 | 21,712,576 | 21,712,848 | 21,712,700 | 21,711,132 | 21,712,484 |
| DRAM writes32B | 20,978,534 | 20,978,280 | 20,978,540 | 20,978,484 | 20,978,504 | 20,978,484 |
| All-L2 retry events | 67,020,407 | 68,351,326 | 61,455,450 | 67,640,158 | 66,178,318 | 65,039,619 |
| ICNT-to-memory blocked admission events | 63,757,142 | 68,139,468 | 61,972,432 | 62,446,861 | 64,348,187 | 64,612,708 |

Whole-replay DRAM read and write volumes are nearly unchanged across profiles, despite sizable cycle improvement. F128 can improve runtime while visible retry/admission events rise in a design; F256 changes retry composition rather than eliminating all pressure. Traffic volume alone is insufficient to explain speedup.

Phase-class table below sums only explicit completed-kernel print-interval differences, never cumulative snapshots. Every selected field has both endpoints and sums back to final totals (111 CPU checks include endpoint conservation). An interval may contain a response to an earlier kernel's request, so these are print-interval event groups, not guaranteed request-origin attribution. Missing endpoints would remain null; means/gauges/peaks are never differenced.

| Source | Candidate phase | L2 GLOBAL accepted | GLOBAL misses | DRAM reads32B | DRAM writes32B | All-L2 retries | ICNT admission events |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CH-F128 | LocalScan | 14,483,456 | 14,483,456 | 14,483,456 | 15,284,524 | 43,165,193 | 43,702,822 |
| CH-F128 | Partials | 425,984 | 419,492 | 419,492 | 51,442 | 3,219,346 | 3,248,926 |
| CH-F128 | UniformUpdate | 6,964,864 | 6,809,628 | 6,809,628 | 5,642,314 | 21,966,787 | 21,187,720 |
| CH-F256 | LocalScan | 14,483,456 | 14,483,456 | 14,483,456 | 15,289,354 | 39,345,840 | 40,169,134 |
| CH-F256 | Partials | 425,984 | 419,848 | 419,848 | 50,584 | 3,220,429 | 3,242,026 |
| CH-F256 | UniformUpdate | 6,964,680 | 6,809,544 | 6,809,544 | 5,638,602 | 18,889,181 | 18,561,272 |
| CH-P0 | LocalScan | 14,483,456 | 14,483,456 | 14,483,456 | 15,292,252 | 40,817,882 | 39,126,701 |
| CH-P0 | Partials | 425,984 | 419,080 | 419,080 | 50,362 | 3,214,000 | 3,224,847 |
| CH-P0 | UniformUpdate | 6,951,932 | 6,810,156 | 6,810,156 | 5,635,920 | 22,988,525 | 21,405,594 |
| DH-F128 | LocalScan | 14,483,456 | 14,483,456 | 14,483,456 | 15,284,156 | 42,252,625 | 42,109,361 |
| DH-F128 | Partials | 425,856 | 418,824 | 418,824 | 50,634 | 3,213,507 | 2,644,916 |
| DH-F128 | UniformUpdate | 6,962,232 | 6,808,852 | 6,808,852 | 5,643,714 | 20,712,186 | 19,593,910 |
| DH-F256 | LocalScan | 14,483,456 | 14,483,456 | 14,483,456 | 15,292,073 | 43,021,406 | 43,772,251 |
| DH-F256 | Partials | 425,856 | 419,500 | 419,500 | 50,791 | 3,216,473 | 2,692,665 |
| DH-F256 | UniformUpdate | 6,966,032 | 6,809,528 | 6,809,528 | 5,635,620 | 18,801,740 | 18,147,792 |
| DH-P0 | LocalScan | 14,483,456 | 14,483,456 | 14,483,456 | 15,292,611 | 42,269,179 | 39,603,547 |
| DH-P0 | Partials | 425,912 | 419,732 | 419,732 | 49,988 | 3,219,645 | 2,725,762 |
| DH-P0 | UniformUpdate | 6,949,716 | 6,809,512 | 6,809,512 | 5,635,885 | 22,151,334 | 20,117,552 |

| Selected cumulative reason | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MISS_QUEUE_FULL | 62,121,592 | 59,153,658 | 22,100,985 | 62,504,403 | 57,179,002 | 23,821,694 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MSHR_ENRTY_FAIL | 3,094,450 | 7,230,621 | 38,005,512 | 3,084,447 | 6,927,796 | 39,630,061 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MSHR_MERGE_ENRTY_FAIL | 419,193 | 537,826 | 581,510 | 447,850 | 528,065 | 651,518 |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_W:MISS_QUEUE_FULL | 503,360,472 | 353,250,593 | 286,717,006 | 516,481,668 | 392,009,942 | 274,613,644 |

Read MISS_QUEUE_FULL generally falls at F256, while entry-capacity failures rise sharply (CH 3,094,450 ->38,005,512; DH 3,084,447 ->39,630,061). Entry and existing-address merge-list failures are distinct retry causes; neither is a queue occupancy measurement or critical-path time. Missing positive-only reasons remain MISSING, never automatically 0. A change in retries does not establish the cause of the cycle savings or guarantee a benefit from more entries.

## Source and measurement boundaries

Atlas47a097aad4406893a07f8d230e1e0a850609bf39 maps fixed source candidates to local scans (`scan.cu:49-153`), chunk-total scan (`156-181`) and uniform offset updates (`185-201`;launch240-310). These routines have different access/dependency/reuse opportunities. FIXED_SOURCE_PHASE_MAPPING.json retains source commit/report SHA and exact mapping; source-to-capture ELF/numeric linkage remains unresolved. Static address overlap is not a measured cache hit, MSHR merge or exact runtime concurrency.

CH active PAPER_BASE common PIB 256 and DH PAPER_OO PIB 128 remain separate active paths; generic DH PIB 8 is inactive for OO admission. OO PIB-full/Tag-conflict events remain unprinted/null, not CH zeros. Cross-design L1/Tag/physical pool/queue/timing/area differences remain disclosed. Whole-replay finite-service sample/entry ratios are in TYPED_ACTIVE_PATH_COUNTERS.json; they are not critical-path durations and do not erase burst/per-SM bottleneck possibilities.

| Source | Reported mflatency | Reported ICNT-to-memory | Reported ICNT-to-shader | Reported MRQ |
| --- | --- | --- | --- | --- |
| CH-P0 | 1,322 | 4,031 | 51 | 188 |
| CH-F128 | 1,457 | 3,107 | 47 | 346 |
| CH-F256 | 1,456 | 2,700 | 43 | 614 |
| DH-P0 | 1,229 | 4,021 | 64 | 184 |
| DH-F128 | 1,540 | 3,219 | 58 | 337 |
| DH-F256 | 1,269 | 2,668 | 47 | 628 |

The final strict metrics/mean dictionary has mixed scopes; a last printed mean is not automatically the last-kernel mean or exact whole-application mean. Known 500,000 cycle sample/print/update-tail limits remain. MRQ has a distinct cumulative request denominator, not a complete L2-to-DRAM or critical-load service interval. CH MRQ 188 ->346 ->614 and DH 184 ->337 ->628 rise while runtimes improve. No kernel mean is summed/differenced or filled with 0 when missing.

Within each design only FR-FCFS size 64/128/256 changes, with coupled memory-partition shared-credit limits 255/319/447 (return queue 192, two subpartitions, private 1 each). DRAM 850 MHz, Core/ICNT/L2 clocks, 10 MiB L2 capacity/mapping and each design's frontend remain fixed. This is window plus credit expansion, not a pure isolated queue-capacity or equal-area hardware result.

Facts: both designs accelerate, principally in LocalScan/UniformUpdate, with nearly fixed DRAM traffic and only a small F256 relative DH increment. Association: changing scheduling/credits and visible admission/retry mix coincides with faster completion. Mechanism remains a hypothesis: queue/credit occupancy, bank service, request age and dependency-critical paths are not captured by these aggregates. No new experiment, controller action, remaining 48 batch or paper modification is performed.

## Reproduction and source locator

Run `python3 analyze_three_profiles.py`, `python3 validate_and_group.py`, `python3 render_scan_report.py` to regenerate this new packet only. ACTUAL_INPUT_AND_KERNEL_CONTRACT.json and ACTUAL_33_KERNEL_GEOMETRY.json retain each input/member SHA, exact ordered symbol/shape/instruction/CTA. SIX_CLOSED_SOURCE_DATA.json preserves all RESULT/raw/exit SHA, UUIDs/roles/aliases/options, six-field per-kernel additive intervals, explicit retry reasons and separate means/gauges/peaks. PHASE_GROUPS.json sums only legal interval values. Both new CH independent strict/archive/native-restore receipts are retained.

CPU_VALIDATION.json: 111 checks PASS; six closed sources, two newCH archive audits, zero live points consumed, zero model/control actions. Root alone publishes.

| Source | RESULT path | RESULT SHA256 | UUID | Raw gzip SHA256 |
| --- | --- | --- | --- | --- |
| CH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-6df3a84b612086e8-CH-P0-V1.RESULT.json | 2c196ebc1dfcdf41b4cc99600a7afcdda4605c6a9bcc513b3f3e0b587e1cc1de | 6933bc7b-97f3-445b-8bd4-913d57cda378 | 4bf7e5da6bbad9b9ebcbac1c9a464897e760d46856cea302423b43620d85aa74 |
| CH-F128 | /root/data/dtc_stage_iia_first16_20261104_v1/analysis/E2-DTC2A16-6df3a84b612086e8-CH-F128-V1.RESULT.json | 36f3aa10e154a2873befe543f1cf68243c2934d545cd9dd7fc147ccbebc90fd3 | e0f3ab35-8fa7-4cbc-9f7b-92174b5e3f1a | d8300839ba2f9674f15520a74899a5e7396dbeeaf1f21b5b8c5be07f879f83af |
| CH-F256 | /root/data/dtc_stage_iia_first16_20261104_v1/analysis/E2-DTC2A16-6df3a84b612086e8-CH-F256-V1.RESULT.json | ca73b01ce386ba5a13479fbbf03285405580a6940c4c2b30785df63c18c0987d | efb01355-ff22-4ef0-a893-2509dc30cb58 | 31d831aeec509c33adc642e08fd439ad7b52aa3411887c1ffabc1f4e2aed3b92 |
| DH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-6df3a84b612086e8-DH-P0-V1.RESULT.json | 9c4cd8f63cd76198b3f14ca6de444218fe445bf2b3bed0eddfb80a113e28ee85 | 9c9cd180-3f9a-4099-b202-47bcca18135f | b5cd46a4eb433c038d743a5b19a68fe06a6d389bce7da3ea92acc15033693569 |
| DH-F128 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-6df3a84b612086e8-DH-F128-V1.RESULT.json | acf5875d28ce61dbd131d509c237c160d5f5ee5171005748904fcc597696a7ae | 5db8dda8-3314-44fe-a3ff-5e4621904d42 | 57dbf2e88efe85c19faa9473d0991afee5ed8d4fd87dac366e132ca9e257e8ad |
| DH-F256 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-6df3a84b612086e8-DH-F256-V1.RESULT.json | 43e3295cca3481e89b879c531e7248ae449e8726cde99200101eb08c1315f4a4 | 15c1e142-cfa1-490e-834c-a3af0a163c2d | 34f620cfdfac210f5681f53bd1dec5647e50d1f609261fa31cfee43ff686a714 |
