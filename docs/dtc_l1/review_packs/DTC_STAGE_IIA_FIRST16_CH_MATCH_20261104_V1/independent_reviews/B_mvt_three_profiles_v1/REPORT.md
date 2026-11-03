# MVT: closed P0/F128/F256 six-source comparison

**Finding:** F256 accelerates CH more strongly than F128, while DH remains slower than its own P0. CH P0/F128/F256 cycles are 26,581,175 / 25,573,002 / 24,342,928; DH 34,687,540 / 35,332,620 / 35,093,446. F256 DH reciprocal-cycle speedup is 0.988434 (1.1702% more cycles than P0), while CH speedup is 1.091946. Same-F CH/DH is 0.693660: DH still takes 44.1628% more cycles. I=0.905203 is worse than P0 and F128; do not describe it as a relative DTC improvement.

This is six closed matched sources for one frozen input, including both newly authorized CH runs after natural strict/true164/native-restore acceptance. It does not use current scan observations as performance, select per-program best variants for a GM, alter historical scientific identities, modify original results, or start any model. The previous MVT F128 packet and all members remain byte-identical.

## Identity and actual kernel contract

Full input `f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079`; actual fixed contract/strict proof/full declared-body qualification: K1 `_Z11mvt_kernel1PfS_S_`,71,380,992 active-thread instructions; K2 `_Z11mvt_kernel2PfS_S_`,74,285,056. Both stream0, grid (16,1,1),block (256,1,1),16 CTAs; total 145,666,048 instructions/32 CTAs. Bounded 4096-byte headers corroborate the actual input's own geometry, not an assumption from the other matrix-vector programs.

Core `9eedb3131937748f0492fa83aad37d3691118d70`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`, binary SHA `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`. Original CH-P0/DH-P0/DH-F128/DH-F256 are selected by exact full digest/cell/profile from ORIGINAL_REFERENCE_INDEX.json; reference aliases remain disclosed. New CH points remain STAGEII_AUTHORIZED_CH. No R2/IR/EP/PQPS result is substituted.

Prior MVT F128 manifest `062f7262459e8bac45adeee494038a85b63b73319fe19db7b1dbde3150a440ae` and all its members were rechecked unchanged; its four RESULT identities exactly match this six-source package. Both new CH results were independently requalified with the frozen read-only strict/archive/native-restore adapter.

## Performance: relative versus own-design changes

| Profile | CH cycles | DH cycles | S_CH | S_DH | CH_F/DH_F | I=S_DH/S_CH | DH extra cycles vs CH % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P0 | 26,581,175 | 34,687,540 | 1 | 1 | 0.766303 | 1 | 30.496639 |
| F128 | 25,573,002 | 35,332,620 | 1.039423 | 0.981743 | 0.723779 | 0.944507 | 38.163756 |
| F256 | 24,342,928 | 35,093,446 | 1.091946 | 0.988434 | 0.693660 | 0.905203 | 44.162798 |

CH F256 reduces cycles 8.4204% relative to CH-P0; DH F256 increases cycles 1.1702% relative to DH-P0. Compared with F128, F256 saves 1,230,074 CH cycles and 239,174 DH cycles, yet CH improves more, so same-F DTC relative performance deteriorates further. The recovery in DH relative to F128 must not be mislabeled a positive DH result versus P0.

| Source | K1 cycles | K2 cycles | K1 delta vs own P0 | K2 delta vs P0 |
| --- | --- | --- | --- | --- |
| CH-P0 | 24,828,424 | 1,752,751 | 0 | 0 |
| CH-F128 | 23,819,947 | 1,753,055 | -1,008,477 | 304 |
| CH-F256 | 22,592,365 | 1,750,563 | -2,236,059 | -2,188 |
| DH-P0 | 33,032,429 | 1,655,111 | 0 | 0 |
| DH-F128 | 33,678,264 | 1,654,356 | 645,835 | -755 |
| DH-F256 | 33,440,529 | 1,652,917 | 408,100 | -2,194 |

F256 vs P0: CH total -2,238,247 cycles =K1-2,236,059 plusK2-2,188; DH total +405,906 =K1+408,100 plusK2-2,194. F256 vs F128: CH K1-1,227,582/K2-2,492 and DH K1-237,735/K2-1,439. Most change is K1; K2 is small but not exactly unchanged.

The fixed source candidate maps K1 to x1+=A*y1 (matrix row stride across lanes) and K2 to x2+=A^T*y2 (lane-contiguous matrix elements), with separate input/output vectors (`mvt.cu:109-136;launch149-177`). It does not make the second kernel consume the first kernel's vector as ATAX does. This conditional source mapping is consistent with an access-direction contrast, but no source-derived recurrence or address overlap is treated as a measured hit/merge or proven bottleneck. Capture-time ELF/numeric binding remains unresolved.

## Cumulative traffic and visible retries

L2 GLOBAL accepted read/miss units are 32-byte sectors: accepted excludes reservation retries, GLOBAL misses=MISS+SECTOR_MISS. All-L2 misses include other access types. DRAM read/write values are issued 32-byte atoms summed across 20 controllers. Keep these populations separate even when GLOBAL misses and DRAM read atoms coincide in these runs. Cumulative last stream0 snapshots span both replay kernels; do not sum snapshots.

| Counter | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- |
| L2 GLOBAL accepted read sectors | 65,311,172 | 67,381,220 | 69,715,768 | 48,510,772 | 43,887,104 | 49,317,888 |
| L2 GLOBAL read miss sectors | 15,617,216 | 15,559,856 | 14,344,068 | 20,574,896 | 21,306,908 | 20,779,732 |
| All-L2 miss sectors | 15,621,534 | 15,564,037 | 14,347,942 | 20,580,720 | 21,312,792 | 20,785,476 |
| DRAM read atoms32B | 15,617,216 | 15,559,856 | 14,344,068 | 20,574,896 | 21,306,908 | 20,779,732 |
| DRAM write atoms32B | 4,826 | 4,689 | 4,382 | 6,332 | 6,392 | 6,252 |
| All-L2 reservation retries | 38,829,217 | 41,003,118 | 41,112,385 | 161,531,923 | 173,604,363 | 157,377,128 |
| ICNT-to-memory blocked admission events | 32,670,735 | 34,946,868 | 33,973,696 | 152,064,800 | 161,662,150 | 150,463,159 |

Direct F256 versus F128 differences:

| Design | Counter | F128 | F256 | Delta | Change % |
| --- | --- | --- | --- | --- | --- |
| CH | L2 GLOBAL accepted read sectors | 67,381,220 | 69,715,768 | 2,334,548 | 3.464686 |
| CH | L2 GLOBAL read miss sectors | 15,559,856 | 14,344,068 | -1,215,788 | -7.813620 |
| CH | All-L2 miss sectors | 15,564,037 | 14,347,942 | -1,216,095 | -7.813493 |
| CH | DRAM read atoms32B | 15,559,856 | 14,344,068 | -1,215,788 | -7.813620 |
| CH | DRAM write atoms32B | 4,689 | 4,382 | -307 | -6.547238 |
| CH | All-L2 reservation retries | 41,003,118 | 41,112,385 | 109,267 | 0.266485 |
| CH | ICNT-to-memory blocked admission events | 34,946,868 | 33,973,696 | -973,172 | -2.784719 |
| DH | L2 GLOBAL accepted read sectors | 43,887,104 | 49,317,888 | 5,430,784 | 12.374441 |
| DH | L2 GLOBAL read miss sectors | 21,306,908 | 20,779,732 | -527,176 | -2.474202 |
| DH | All-L2 miss sectors | 21,312,792 | 20,785,476 | -527,316 | -2.474176 |
| DH | DRAM read atoms32B | 21,306,908 | 20,779,732 | -527,176 | -2.474202 |
| DH | DRAM write atoms32B | 6,392 | 6,252 | -140 | -2.190238 |
| DH | All-L2 reservation retries | 173,604,363 | 157,377,128 | -16,227,235 | -9.347251 |
| DH | ICNT-to-memory blocked admission events | 161,662,150 | 150,463,159 | -11,198,991 | -6.927404 |

CH becomes faster than F128 despite more accepted reads and slightly more retry events; its DRAM read misses fall. DH F256 recovers some performance relative to F128 while accepted reads/OO lower creations rise and DRAM reads/retries fall. These are design-specific associations, not proof that one count determines completion. Compared with P0, DH F256 still has more DRAM reads and slower cycles, while CH has fewer DRAM reads and faster cycles.

Print-boundary kernel intervals, requiring explicit additive endpoints, are below. These are event intervals, not a request-origin attribution. Means, gauges and peaks are never differenced.

| Source | Kernel interval | L2 GLOBAL accepted | GLOBAL misses | DRAM reads32B | DRAM writes32B | All-L2 retries | ICNT admission blocks |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CH-P0 | 1 | 63,205,316 | 13,538,536 | 13,538,536 | 4,486 | 38,828,810 | 32,670,735 |
| CH-P0 | 2 | 2,105,856 | 2,078,680 | 2,078,680 | 340 | 407 | 0 |
| CH-F128 | 1 | 65,275,364 | 13,469,892 | 13,469,892 | 4,309 | 41,002,783 | 34,946,868 |
| CH-F128 | 2 | 2,105,856 | 2,089,964 | 2,089,964 | 380 | 335 | 0 |
| CH-F256 | 1 | 67,609,912 | 12,247,084 | 12,247,084 | 3,958 | 41,111,949 | 33,973,696 |
| CH-F256 | 2 | 2,105,856 | 2,096,984 | 2,096,984 | 424 | 436 | 0 |
| DH-P0 | 1 | 46,404,916 | 18,567,980 | 18,567,980 | 6,084 | 161,530,659 | 152,064,800 |
| DH-P0 | 2 | 2,105,856 | 2,006,916 | 2,006,916 | 248 | 1,264 | 0 |
| DH-F128 | 1 | 41,781,248 | 19,226,272 | 19,226,272 | 6,128 | 173,604,032 | 161,662,150 |
| DH-F128 | 2 | 2,105,856 | 2,080,636 | 2,080,636 | 264 | 331 | 0 |
| DH-F256 | 1 | 47,212,032 | 18,783,516 | 18,783,516 | 6,004 | 157,375,626 | 150,463,159 |
| DH-F256 | 2 | 2,105,856 | 1,996,216 | 1,996,216 | 248 | 1,502 | 0 |

## Entry/merge/miss-queue reason distinction

| Positive-only raw reason | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:LINE_ALLOC_FAIL | 3,262,847 | 3,822,607 | 4,303,389 | 529,671 | 595,326 | 624,685 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MISS_QUEUE_FULL | 5,560,281 | 30,644 | MISSING | 52,360,071 | 56,276 | 16,583 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MSHR_ENRTY_FAIL | 29,115,010 | 35,964,383 | 35,470,845 | 108,621,212 | 172,934,579 | 156,716,928 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MSHR_MERGE_ENRTY_FAIL | 880,332 | 1,175,494 | 1,323,703 | 18,837 | 17,853 | 18,351 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_W:LINE_ALLOC_FAIL | 10,747 | 9,990 | 14,448 | 2,132 | 329 | 581 |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_R:LINE_ALLOC_FAIL | 353,557,349 | 354,477,147 | 348,966,311 | MISSING | MISSING | MISSING |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_R:MISS_QUEUE_FULL | 580 | 196 | 170 | MISSING | MISSING | MISSING |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_W:LINE_ALLOC_FAIL | 12,277,148 | 12,506,083 | 13,737,017 | MISSING | MISSING | MISSING |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_W:MISS_QUEUE_FULL | 114 | 71 | 145 | 4,249 | 1 | 1 |

DH read MISS_QUEUE_FULL falls 52,360,071 ->56,276 ->16,583. Read MSHR entry-capacity failures move 108,621,212 ->172,934,579 ->156,716,928: F256 partly recovers from F128 but remains well above P0. Merge-list limit failures 18,837 ->17,853 ->18,351 are a distinct check on an already-present address. Dominant entry retries are not occupancy measurements, durations or proof that entry expansion will improve performance.

CH entry failures 29,115,010 ->35,964,383 ->35,470,845 and merge-limit failures 880,332 ->1,175,494 ->1,323,703 can rise while cycles improve. A falling MISS_QUEUE_FULL count cannot establish that downstream pressure was eliminated or that total critical-path delay fell. CH-F256 read MISS_QUEUE_FULL is unprinted and remains MISSING, not silently 0. Positive-only reason absence and absent counters never become observed zero.

## Typed active frontend and finite-service evidence

CH PAPER_BASE active common PIB 256 and DH PAPER_OO PIB 128 are not equivalent queues. DH generic pib_entries 8 is inactive for OO admission. CH common Tag conflicts/PIB-full values are not OO statistics; OO PIB-full/Tag-conflict event fields remain unprinted/null. CH disabled DTC finite-service extension does not mean unlimited ordinary-cache service. L1/Tag/physical pool/queues/timing/area differences remain disclosed.

| Typed event | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- |
| CH common Tag-bank conflict attempts | 20,972,288 | 20,972,288 | 20,972,288 | MISSING | MISSING | MISSING |
| CH common PIB-full events | 0 | 0 | 0 | MISSING | MISSING | MISSING |
| DH OO valid-line hits | MISSING | MISSING | MISSING | 6,155,579 | 7,321,884 | 5,953,581 |
| DH OO pending-line hits | MISSING | MISSING | MISSING | 67,064 | 56,676 | 67,283 |
| DH OO new-line misses | MISSING | MISSING | MISSING | 12,127,693 | 10,971,776 | 12,329,472 |
| DH OO 128B lower creations | MISSING | MISSING | MISSING | 12,127,693 | 10,971,776 | 12,329,472 |
| DH OO tag-map evictions | MISSING | MISSING | MISSING | 12,111,309 | 10,955,392 | 12,313,088 |

For each DH profile, valid+pending+new classifications conserve 18,350,336 OO line probes. New misses=lower created=issued=responses=credits acquired/released, and L2 GLOBAL accepted sectors=4*128B lower creations. F256 versus F128 has fewer valid hits and more OO misses/evictions, but fewer DRAM read misses and faster cycles: OO Tag classifications are not DRAM traffic or a sufficient speed prediction.

| DH profile | Mean PIB entries, all64SM samples | Mean physical lines | Ready-to-retire cycles / retired entry | Map-loss-to-free cycles / event | Writeback wait |
| --- | --- | --- | --- | --- | --- |
| P0 | 1.587601 | 152.643995 | 4.282801 | 5432.222318 | 45,586 |
| F128 | 1.578909 | 152.354166 | 4.358845 | 6038.992934 | 30,953 |
| F256 | 1.591745 | 152.536466 | 4.280366 | 5377.039664 | 40,257 |

Retired finite-service denominator stays 2,097,408. F256 ready-to-complete sum 8,977,674 is below F128 9,142,276 and just below P0 8,982,782, while writeback wait 40,257 is above F128 30,953 but below P0 45,586. Mixed service movement does not identify a single completion-service cause. Means use their own sample/entry denominators and are not critical-path time; low all-SM mean PIB occupancy (~1.6 entries) does not rule out brief/per-SM/burst/dependency pressure. Gauges/peaks remain separate.

## Reported latency windows and physical resource coupling

| Source | Reported mflatency | Reported ICNT-to-memory | Reported ICNT-to-shader | Reported MRQ |
| --- | --- | --- | --- | --- |
| CH-P0 | 620 | 153 | 44 | 455 |
| CH-F128 | 614 | 140 | 46 | 696 |
| CH-F256 | 589 | 124 | 52 | 913 |
| DH-P0 | 2,230 | 349 | 220 | 738 |
| DH-F128 | 2,463 | 391 | 166 | 1,366 |
| DH-F256 | 2,244 | 346 | 227 | 1,798 |

Integer printed means have known 500,000 cycle sample/print/update tail limits. MRQ is a distinct cumulative request-denominator mean, in global core cycles from DRAM request construction to bank assignment; it is not complete L2-to-DRAM service time or critical dependency latency. DH MRQ 738 ->1366 ->1798 increases even though F256 recovers from F128; other means move differently. Existing diagnostics do not prove a fall in average DRAM queue wait or permit summing/differencing mean snapshots. Cross-design request populations also differ. Missing means would remain missing, never 0.

Only FR-FCFS parameter 64/128/256 changes within each design, with coupled memory-partition shared-credit limits 255/319/447 (return queue 192, subpartitions 2, private 1 each). DRAM 850 MHz, Core/ICNT/L2 clocks, 10 MiB L2 capacity/mapping and each design's frontend remain fixed. These are scheduling-window plus credit changes, not isolated pure queue-capacity or equal-area hardware comparisons.

## Scientific conclusion boundary

Fact: F256 CH improves substantially, DH remains worse than its own P0, and same-F DTC relative disadvantage increases. Almost all cycle change is K1. Correlation: miss/traffic/retry mix and OO reuse/service lifetimes change together under a coupled downstream intervention. Hypothesis only: altered scheduling/credits change residency, overlap and dependent-request lifetimes in strided K1. Existing aggregate counters do not isolate banks, credit occupancy, queue residence or critical-load service causality.

Candidate source is fixed Atlas47a097aad4406893a07f8d230e1e0a850609bf39 / app commit dad09cb0487845edc7524ded814c6cde9f0ef6a1, `MVT/mvt.cu:109-136;149-177`, SHA 83764e6633f3a0976423e0ba7ab351ac42b0eeb249bf59a9e3531c639d4923d6. MVT_FIXED_SOURCE_PHASE_MAPPING.json retains exact excerpts/report/source SHA. Candidate source capture-time ELF/numeric binding remains unresolved. Full declared-body qualification does not upgrade native full-application/numerical correctness or infer cache hits from static address repeats.

No new simulation, capture, remaining 48 batch, runtime change, source change or paper edit is started or authorized by this analysis. Causal instrumentation would require a separate authorized observation experiment; this packet only consumes closed assets.

## Reproduction and source locators

Run `python3 analyze_three_profiles.py`, `python3 validate_and_derive.py`, `python3 render_three_profiles.py` only to regenerate this new analysis packet. SIX_CLOSED_SOURCE_DATA.json preserves exact RESULT/raw gzip/raw plain/NATIVE_EXIT SHA, source roles/UUID/aliases, options, all cumulative/explicit-endpoint intervals, reasons, means/gauges/peaks. Both CH independent strict/archive/restore receipts and actual input/header contract are included. F256_VS_F128_COUNTERS.json reproduces direct profile differences. F128_PIN_CONSUMPTION.json proves old packet preservation.

CPU_VALIDATION.json: 61 checks PASS; all 6 closed sources, 2 independent newCH strict/archive/native-restore audits, no live source consumed, no model/control actions. Root alone publishes.

| Source | RESULT path | RESULT SHA256 | UUID | Raw gzip SHA256 |
| --- | --- | --- | --- | --- |
| CH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-f437190767aaed49-CH-P0-V1.RESULT.json | 12718f4e83f007d846e10bcb0778b29f62cbe5af2797b932024945601f3860a8 | bde2fff3-0d42-4920-a97c-1ed7a5be1df1 | 4126e55ada011b5438fd482857c26544fd6e7b5aab188fa9c704de537e451140 |
| CH-F128 | /root/data/dtc_stage_iia_first16_20261104_v1/analysis/E2-DTC2A16-f437190767aaed49-CH-F128-V1.RESULT.json | 56fba6ac0dfe9ef4f1b0294d30865d1b3d58bffc761c519a12e16b50c88f6ff1 | ce67bc90-9dd4-4c70-a1a8-135d22dd136a | ad6b0297012a60a6b316dfa7af43ad8974056d5da8340f6341206a9a725da867 |
| CH-F256 | /root/data/dtc_stage_iia_first16_20261104_v1/analysis/E2-DTC2A16-f437190767aaed49-CH-F256-V1.RESULT.json | 5c3497283682ec33bb8dc702e4a420bb930fb5584aaffbe08db6b5c8877bb19f | f842ff4d-6835-4d83-9122-5feb3f4d12fd | 4aaf05e2c0a5e5b97732fcd653f62972d81e4de14b9f9ac1e5281b7797a8b801 |
| DH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-f437190767aaed49-DH-P0-V1.RESULT.json | 198efde39a9f29222f80e6bda521aa1a28dd281a6e649999505af60cbe06d162 | 93cd6c4f-02cf-4e47-9a73-cba755167f47 | e05444affe960e9860586698ed7a0c56d6e4e593c44fe5c9c5ee85c9eca112cd |
| DH-F128 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-f437190767aaed49-DH-F128-V1.RESULT.json | 4ec3e2aee1163900ac98d2ad1a31455b641f6754f47c8a44e9315c6e39401406 | 4b2fdd92-6b0f-4880-afc1-c12113099931 | 3891ba95794a90dddb0bceedde515c2f23721e58343342175a35ed09275a8e68 |
| DH-F256 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-f437190767aaed49-DH-F256-V1.RESULT.json | 8c0c7c629ff7bf8cfe4357bc6b2ad8ddf71c6af616d41cc1b4ecb0c68ca923c9 | 2eb2507b-42f5-4ffe-8e1b-b4e5cde0f7d2 | 1ca0064cc60f3f94502214dedb92415d7e466cb393bcdc14e20f3feb0d90bd83 |
