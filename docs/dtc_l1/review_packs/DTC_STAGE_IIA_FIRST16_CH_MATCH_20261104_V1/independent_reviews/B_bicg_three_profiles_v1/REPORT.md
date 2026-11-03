# BICG: closed P0/F128/F256 six-source comparison

**Finding:** F256 recovers part of DH's F128 regression, but does not recover its own P0 performance or catch CH. DH P0/F128/F256 cycles are 28,685,812 / 29,210,480 / 28,883,488. CH cycles are 26,298,698 / 24,464,891 / 24,651,923. Relative to F128, F256 saves DH 326,992 cycles but costs CH 187,032 cycles; all these cycle changes occur in K2, with exactly unchanged K1 in each design.

This packet is one input with six matched closed sources. It does not select per-program best configurations for a GM, modify old results, or consume the currently active scan/MVT runs. Both new CH points independently passed the frozen read-only strict/archive/native-restore audit. Original F128 packet bytes remain unchanged; its historical OO-prefixed CH diagnostic naming error is not reused. The typed mapping here follows the forward clarification: CH common and DH OO are separate domains.

## Exact identity and actual trace contract

Input `ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef`. The canonical input binding, full declared-body qualification, actual strict proof/raw kernel boundaries and bounded 4096-byte headers agree: K1 `_Z12bicg_kernel1PfS_S_` has 74,285,056 active-thread instructions; K2 `_Z12bicg_kernel2PfS_S_` has 71,380,992. Both grid (16,1,1),block (256,1,1),16 CTAs, stream0; total 145,666,048 instructions and 32 CTAs. The order/instruction split is BICG's own, not copied from ATAX/MVT.

Core `9eedb3131937748f0492fa83aad37d3691118d70`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`, binary SHA `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`. Original references are exact full-digest/cell/profile rows from ORIGINAL_REFERENCE_INDEX.json; no same-name R2/IR/EP/PQPS result is substituted. Any inherited P0 reference alias remains disclosed. New CH has its authorized StageII role. The prior F128 manifest `f2b1dfc69e860b56e96ec70f50490458d843a8808f5f7d598852571790401cba` and every member SHA were rechecked unchanged; all four former RESULT identities remain exact.

## Performance, including unfavorable outcomes

| Profile | CH cycles | DH cycles | S_CH=CH0/CH_F | S_DH=DH0/DH_F | CH_F/DH_F | I=S_DH/S_CH | DH extra cycles vs same-F CH % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P0 | 26,298,698 | 28,685,812 | 1 | 1 | 0.916784 | 1 | 9.076928 |
| F128 | 24,464,891 | 29,210,480 | 1.074957 | 0.982038 | 0.837538 | 0.913561 | 19.397548 |
| F256 | 24,651,923 | 28,883,488 | 1.066801 | 0.993156 | 0.853495 | 0.930967 | 17.165253 |

F256 vs P0: CH gains 1.066801x in reciprocal cycles, DH has 0.993156x (0.6891% more cycles). F256 DH still needs 17.1653% more cycles than matched CH. F128 DH is 1.8290% slower than its P0 and 19.3975% slower than CH. I is below 1 for both F profiles, so the coupled downstream expansion worsens DTC's relative position to CH compared with P0, even though F256 improves that position relative to F128.

| Source | K1 cycles | K2 cycles | K1 delta vs P0 | K2 delta vs P0 |
| --- | --- | --- | --- | --- |
| CH-P0 | 1,749,396 | 24,549,302 | 0 | 0 |
| CH-F128 | 1,749,396 | 22,715,495 | 0 | -1,833,807 |
| CH-F256 | 1,749,396 | 22,902,527 | 0 | -1,646,775 |
| DH-P0 | 1,655,347 | 27,030,465 | 0 | 0 |
| DH-F128 | 1,655,347 | 27,555,133 | 0 | 524,668 |
| DH-F256 | 1,655,347 | 27,228,141 | 0 | 197,676 |

Fixed candidate BICG source maps K1 to s=A^T*r with lane-contiguous A and broadcast r, and K2 to q=A*p with row-strided A across lanes and broadcast p (`bicg.cu:99-113;117-131;launch166-196`). This explains the access-direction contrast to test; it does not certify capture ELF/numeric semantics or establish the causal bottleneck. Unlike ATAX, these source operations use separate vectors and do not make q consume s. Current runtime cycle evidence locates F sensitivity in K2.

## Legal cumulative traffic and retry counters

L2 GLOBAL accepted/miss units are 32-byte sectors. Accepted excludes retry events; misses=MISS+SECTOR_MISS. DRAM reads/writes are issued 32-byte data atoms summed over 20 controllers; these are not generally one-to-one with every L2 access type. All-L2 misses include non-GLOBAL-read types. All values are explicit cumulative final stream0 snapshots; they are never summed over kernels.

| Counter | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- |
| L2 GLOBAL accepted read sectors | 64,586,544 | 63,678,800 | 64,770,332 | 44,804,596 | 42,483,856 | 44,720,036 |
| L2 GLOBAL read miss sectors | 15,513,224 | 14,425,788 | 14,523,200 | 17,688,864 | 17,956,084 | 17,459,384 |
| All-L2 miss sectors | 15,517,880 | 14,429,928 | 14,527,298 | 17,694,564 | 17,961,664 | 17,465,336 |
| DRAM read atoms32B | 15,513,224 | 14,425,788 | 14,523,200 | 17,688,864 | 17,956,084 | 17,459,384 |
| DRAM write atoms32B | 4,772 | 4,316 | 4,238 | 5,892 | 5,836 | 6,224 |
| All-L2 retry events | 57,034,297 | 46,315,523 | 47,932,143 | 158,410,296 | 159,762,760 | 159,914,089 |
| ICNT-to-memory blocked-admission events | 42,823,201 | 34,414,850 | 35,903,195 | 157,588,835 | 159,723,396 | 160,683,541 |

F256 relative to F128, same-design differences:

| Design | Counter | F128 | F256 | Delta | Change % |
| --- | --- | --- | --- | --- | --- |
| CH | L2 GLOBAL accepted read sectors | 63,678,800 | 64,770,332 | 1,091,532 | 1.714121 |
| CH | L2 GLOBAL read miss sectors | 14,425,788 | 14,523,200 | 97,412 | 0.675263 |
| CH | All-L2 miss sectors | 14,429,928 | 14,527,298 | 97,370 | 0.674778 |
| CH | DRAM read atoms32B | 14,425,788 | 14,523,200 | 97,412 | 0.675263 |
| CH | DRAM write atoms32B | 4,316 | 4,238 | -78 | -1.807229 |
| CH | All-L2 retry events | 46,315,523 | 47,932,143 | 1,616,620 | 3.490450 |
| CH | ICNT-to-memory blocked-admission events | 34,414,850 | 35,903,195 | 1,488,345 | 4.324717 |
| DH | L2 GLOBAL accepted read sectors | 42,483,856 | 44,720,036 | 2,236,180 | 5.263599 |
| DH | L2 GLOBAL read miss sectors | 17,956,084 | 17,459,384 | -496,700 | -2.766193 |
| DH | All-L2 miss sectors | 17,961,664 | 17,465,336 | -496,328 | -2.763263 |
| DH | DRAM read atoms32B | 17,956,084 | 17,459,384 | -496,700 | -2.766193 |
| DH | DRAM write atoms32B | 5,836 | 6,224 | 388 | 6.648389 |
| DH | All-L2 retry events | 159,762,760 | 159,914,089 | 151,329 | 0.094721 |
| DH | ICNT-to-memory blocked-admission events | 159,723,396 | 160,683,541 | 960,145 | 0.601130 |

DH-F256 becomes faster than F128 while OO lower creations and accepted L2 reads increase 5.26%, issued DRAM reads fall 2.77%, writes rise 6.65%, and aggregate retry/admission events rise 0.095%/0.60%. Hence fewer lower requests, fewer retries or universally lower traffic cannot serve as a single explanation. CH-F256 becomes slower than F128 while accepted reads, read misses, retries and admission blocks rise, but its writes decline. These are observed associations, not isolated causes.

Print-boundary kernel interval differences require both cumulative endpoints explicitly present. They are not automatically request-origin labels; means/gauges/peaks are never differenced. The raw-derived interval table preserves all six sources:

| Source | Interval | L2 GLOBAL accepted | GLOBAL misses | DRAM reads32B | DRAM writes32B | All-L2 retries | ICNT admission blocks |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CH-P0 | 1 | 2,105,344 | 2,097,584 | 2,097,584 | 0 | 0 | 0 |
| CH-P0 | 2 | 62,481,200 | 13,415,640 | 13,415,640 | 4,772 | 57,034,297 | 42,823,201 |
| CH-F128 | 1 | 2,105,344 | 2,097,584 | 2,097,584 | 0 | 0 | 0 |
| CH-F128 | 2 | 61,573,456 | 12,328,204 | 12,328,204 | 4,316 | 46,315,523 | 34,414,850 |
| CH-F256 | 1 | 2,105,344 | 2,097,584 | 2,097,584 | 0 | 0 | 0 |
| CH-F256 | 2 | 62,664,988 | 12,425,616 | 12,425,616 | 4,238 | 47,932,143 | 35,903,195 |
| DH-P0 | 1 | 2,105,344 | 2,097,584 | 2,097,584 | 0 | 892 | 0 |
| DH-P0 | 2 | 42,699,252 | 15,591,280 | 15,591,280 | 5,892 | 158,409,404 | 157,588,835 |
| DH-F128 | 1 | 2,105,344 | 2,097,584 | 2,097,584 | 0 | 892 | 0 |
| DH-F128 | 2 | 40,378,512 | 15,858,500 | 15,858,500 | 5,836 | 159,761,868 | 159,723,396 |
| DH-F256 | 1 | 2,105,344 | 2,097,584 | 2,097,584 | 0 | 892 | 0 |
| DH-F256 | 2 | 42,614,692 | 15,361,800 | 15,361,800 | 6,224 | 159,913,197 | 160,683,541 |

## Entry and merge retries: remain distinct

| Explicit positive-only reason | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:LINE_ALLOC_FAIL | 6,064,345 | 5,007,714 | 4,799,623 | 347,238 | 405,108 | 488,381 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MISS_QUEUE_FULL | 10,086,344 | 6,746 | 64 | 15,514,452 | 137,002 | 37,513 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MSHR_ENRTY_FAIL | 39,160,496 | 39,747,955 | 41,521,806 | 142,533,205 | 159,204,818 | 159,372,674 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MSHR_MERGE_ENRTY_FAIL | 1,717,571 | 1,547,340 | 1,605,237 | 15,401 | 15,832 | 15,401 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_W:LINE_ALLOC_FAIL | 5,541 | 5,768 | 5,413 | MISSING | MISSING | 120 |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_R:LINE_ALLOC_FAIL | 352,835,614 | 333,537,709 | 332,743,302 | MISSING | MISSING | MISSING |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_R:MISS_QUEUE_FULL | 496 | 405 | 368 | MISSING | MISSING | MISSING |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_W:LINE_ALLOC_FAIL | 12,537,878 | 12,053,953 | 11,904,877 | MISSING | MISSING | MISSING |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_W:MISS_QUEUE_FULL | 163 | 59 | 169 | 3,369 | 16,408 | 289 |

DH read MISS_QUEUE_FULL drops 15,514,452 ->137,002 ->37,513 across P0/F128/F256. Yet MSHR entry-capacity failures remain 142,533,205 ->159,204,818 ->159,372,674; F256 is slightly higher than F128 and materially higher than P0. Its entry failures account for most of the aggregate retries, but the count is neither occupancy nor critical-path time. Merge-list failures 15,401 ->15,832 ->15,401 belong to an existing-address merge-limit check and must not be conflated with entry exhaustion.

CH read MISS_QUEUE_FULL drops 10,086,344 ->6,746 ->64, while entry failures rise 39,160,496 ->39,747,955 ->41,521,806. Thus ?miss queue pressure fell? does not establish that a different bottleneck was removed or that increasing entries would improve performance. Retry reasons are positive-only prints; missing entries stay MISSING, never imputed 0. They are not stalled-cycle durations or a decomposition of total cycles.

## Active frontend and finite service

CH PAPER_BASE uses active common PIB 256; DH PAPER_OO uses active OO PIB 128. DH generic PIB 8 does not set OO admission capacity. Common CH Tag/PIB values are never assigned to OO fields. OO PIB-full and OO Tag-conflict events remain unprinted/null, not copied CH zeros. CH's disabled DTC finite-service extension does not mean unlimited ordinary-cache service. These modes differ in L1 structure, Tag, queues, timing and area; all matched-F comparisons preserve that disclosure.

| Typed event | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- |
| CH common Tag-bank conflict attempts | 20,972,288 | 20,972,288 | 20,972,288 | MISSING | MISSING | MISSING |
| CH common PIB-full events | 0 | 0 | 0 | MISSING | MISSING | MISSING |
| DH OO valid-line hits | MISSING | MISSING | MISSING | 7,087,138 | 7,667,198 | 7,107,464 |
| DH OO pending-line hits | MISSING | MISSING | MISSING | 61,793 | 61,918 | 62,607 |
| DH OO new-line misses | MISSING | MISSING | MISSING | 11,201,149 | 10,620,964 | 11,180,009 |
| DH OO 128B lower creations | MISSING | MISSING | MISSING | 11,201,149 | 10,620,964 | 11,180,009 |
| DH OO tag-map evictions | MISSING | MISSING | MISSING | 11,184,765 | 10,604,580 | 11,163,625 |

DH valid+pending+new classifications conserve 18,350,080 line probes for all three profiles. New misses=lower created=issued=responses=lower credits acquired/released; L2 GLOBAL accepted sectors=4*128B lower creations. F256 relative to F128 has fewer valid hits and more new misses/evictions, yet fewer DRAM reads and faster cycles. OO Tag classification is therefore not interchangeable with DRAM misses or a direct performance prediction.

| DH profile | Mean PIB entries, all64SM samples | Mean physical lines | Ready-to-retire cycles / retired entry | Map-loss-to-free cycles / event |
| --- | --- | --- | --- | --- |
| P0 | 1.647670 | 264.982222 | 4.324533 | 4919.549654 |
| F128 | 1.581222 | 264.346069 | 4.351305 | 5104.997132 |
| F256 | 1.576827 | 263.908402 | 4.339775 | 4761.234874 |

Finite-service retired denominator is 2,097,152 in all profiles. F256 ready-to-complete sum 9,101,167 remains above P0 9,069,203 but slightly below F128 9,125,347; writeback waits 32,826 /34,394 /32,432 are not monotonic. Each ratio uses its own additive numerator/denominator; these sample/entry means are not critical-path durations or proofs that bursts/per-SM bottlenecks are absent. Terminal gauges and running peaks remain separate in the source data.

## Latency windows and F coupling

| Source | Reported mflatency | Reported ICNT-to-memory | Reported ICNT-to-shader | Reported MRQ |
| --- | --- | --- | --- | --- |
| CH-P0 | 736 | 153 | 72 | 526 |
| CH-F128 | 684 | 137 | 84 | 807 |
| CH-F256 | 691 | 141 | 82 | 1,008 |
| DH-P0 | 2,548 | 462 | 221 | 791 |
| DH-F128 | 2,649 | 484 | 202 | 1,477 |
| DH-F256 | 2,565 | 474 | 210 | 2,074 |

These are integer printed diagnostics with 500,000 cycle sample/print/update-tail limitations; never sum/difference them over kernels or reinterpret missing as 0. MRQ is a separate cumulative request-denominator mean from DRAM-request construction to bank assignment in global core cycles, not complete L2-to-DRAM latency or critical dependency wait. DH MRQ 791 ->1477 ->2074 increases even as F256 improves over F128. Existing means do not establish that a larger F reduced average DRAM queue wait. CH/DH means need not cover equal request populations.

Within each design only FR-FCFS size 64/128/256 changes. Fixed Core simultaneously changes memory-partition shared-credit limits 255/319/447 (`FR_queue+return_queue 192-(subpartitions 2-1)`), not a pure isolated queue capacity. DRAM 850 MHz, Core/ICNT/L2 clocks, 10 MiB L2 capacity/mapping and each design's frontend remain fixed. High resources are not free/equal-area hardware.

## Evidence levels and unresolved cause

Fact: all F sensitivity in BICG total cycles is K2, with CH helped by both F variants and DH still worse than P0. F256 vs F128 improves DH despite higher lower-request and retry populations. Association: coupled scheduling/credits alter reuse, miss/service and arrival patterns. Hypothesis only: those timing/lifetime changes redistribute residency/overlap in the strided K2; current aggregates do not isolate banks, credits, queue occupancy or critical dependent requests. Do not infer entry expansion as a guaranteed remedy from a dominant retry count.

The fixed candidate source is Atlas47a097aad4406893a07f8d230e1e0a850609bf39 / app commit dad09cb0487845edc7524ded814c6cde9f0ef6a1, `BICG/bicg.cu` SHA c38c3b0bb1a543ce37ee6d4d7abe433a36574f05b49574e6bf1004c45b68f6fe, kernel 99-131/launch 166-196. This is exact recovered source, not a certified capture-time ELF/numeric linkage. Current full declared-body coverage does not newly certify full native application semantics or numerical correctness. Source-derived address repeats are not measured cache hits or MSHR merges.

No new experiment, remaining 48 batch, trace, source modification, controller action or paper change is authorized by this analysis. A causal time-resolved attribution would need separately authorized observation; this packet only consumes existing closed evidence.

## Reproduction and source locators

Run `python3 analyze_three_profiles.py`, `python3 validate_and_derive.py`, then `python3 render_three_profiles.py` only to regenerate this new packet. SIX_CLOSED_SOURCE_DATA.json retains all exact RESULT, raw gzip/uncompressed and NATIVE_EXIT SHA, UUIDs, original roles/aliases, complete options, cumulative counters, explicit-endpoint intervals, raw reasons, means/gauges/peaks. F256_VS_F128_COUNTERS.json makes the direct F comparison reproducible. BICG_FIXED_SOURCE_PHASE_MAPPING.json pins source/header/trace boundaries. The typed-domain and input-contract files preserve active capacities/nulls. F128_PIN_CONSUMPTION.json preserves the old package manifest and exact unmodified members; its historical named diagnostic error is documented, not silently overwritten.

CPU_VALIDATION.json: 61 checks PASS; two new CH archive/strict/native-restore independent audits PASS; no live points consumed or model actions. MANIFEST.json freezes every public member.

| Source | RESULT path | RESULT SHA256 | UUID | Raw gzip SHA256 |
| --- | --- | --- | --- | --- |
| CH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-ae34174fbbdf83b2-CH-P0-V1.RESULT.json | dded01863187729a3a7d98f74418f2602eedd0490c11c3faeeef9adfaa8f47a8 | f93c0c73-fc16-496b-9021-87ba236f60c2 | 0adc63f182c7facbb4d0a60fcdbbe4ece7a00b5ec3158afb66bb43038ba2926e |
| CH-F128 | /root/data/dtc_stage_iia_first16_20261104_v1/analysis/E2-DTC2A16-ae34174fbbdf83b2-CH-F128-V1.RESULT.json | d99402054d4635732ec3df217c354809ea3737622b34e453e135ccbbf1abd743 | e6617bdb-dda5-4142-8952-37da47ec7847 | 9813a08ec6449d8f748ca855ba3e0ab242956c5a18c483096ee4b0240f5cde58 |
| CH-F256 | /root/data/dtc_stage_iia_first16_20261104_v1/analysis/E2-DTC2A16-ae34174fbbdf83b2-CH-F256-V1.RESULT.json | d714e77bee7277e000d0749253dbf511266a9bb8c2cb7e36b66a5272a50af738 | a68e72e0-dc7b-47be-90b4-1689271c3dcf | 33f5e6f27cc142ab69dd3c2965b709ef2a67b26981c7cdf25349dd82eac1865c |
| DH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-ae34174fbbdf83b2-DH-P0-V1.RESULT.json | 78f79fa1898c45e4769ee10e0043bf2840507023da46882bd168d914b6584216 | fbb45ea4-716d-46f5-abfb-2842f03a8e99 | 4ffe6cbc56a31f0782f03bf26c67081b192d81f2aa997525c9732d2bb7488ce0 |
| DH-F128 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-ae34174fbbdf83b2-DH-F128-V1.RESULT.json | 772a1c13fe38bfbfbcda161b2cbd7bf5b07b03f7874c541cbcb4b8eeb6437301 | 1a9da968-f307-4a73-8c69-77b1b9eb8211 | 1c3e686d13b192bc8c2f2480a16c8070977c44096bcdf919592b06d93911bce9 |
| DH-F256 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-ae34174fbbdf83b2-DH-F256-V1.RESULT.json | fdabb0d2deb361270b2f05d013fb73285ae241704bd0a79db005e7887293a260 | 6ceeda27-593f-4a62-a0b2-58a694c38394 | a37feb636bae150c203a45ba9bb5faab3575635d6e6f95c1fd6861a46cae5d5a |
