# ATAX: complete CH/DH P0, F128, F256 matched evidence

**Conclusion:** F256 improves DH itself by 1.7823% in reciprocal-cycle speed and 1.7511% in cycle reduction. The relative improvement I=1.112797 does not mean DH has passed CH: CH/DH=0.992325, so DH still takes 0.7735% more cycles. A large contribution to I is CH deterioration: CH cycles increase 9.3310% from P0 while DH cycles decrease 1.7511%. F128 remains a negative DH self-response and is retained.

This is six closed sources for one frozen input, not a suite GM or per-program best-parameter selection. All six retain their original accepted scientific roles; two new CH points passed an independent frozen read-only strict/true164/native-restore audit. No remaining live job was read for this analysis, and no simulation, registration, controller/owner/budget/source change or manuscript edit was made.

## Identity, authority and actual capture contract

Frozen input digest: `eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950`; ROI `5ba85e56ae33e604c38407d5d8641078cb0a1b06aaaa9928cc0de4c61d94f442`. This is the full two-kernel declared eededb capture, not the separate ATAX 1of10/trim identity. Actual body qualification, strict proof and bounded headers agree: K1 `_Z12atax_kernel1PfS_S_`,71,380,992 active-thread instructions; K2 `_Z12atax_kernel2PfS_S_`,74,285,056. Each has grid (16,1,1),block (256,1,1),16 CTAs, stream0; total 145,666,048 instructions/32 CTAs. These values are read from this input's own contract, not inferred from workload names.

Fixed Core `9eedb3131937748f0492fa83aad37d3691118d70`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`, simulator binary SHA `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`. PhaseI authority remains `361fa6fa0700825bb9cda43e25b9fd1f60e0b262`; StageII authorized contract `5001c3f35052f7f91f1ad41eeff83f2947a0878d`. Original CH-P0/DH-P0/DH-F128/DH-F256 are selected by full digest/cell/profile from ORIGINAL_REFERENCE_INDEX.json, not substituted by name from R2/IR/EP/PQPS. Existing reference aliases are disclosed rather than promoted.

The frozen prior F128 four-source packet manifest is `af69366bb4fe44dd919518150f763a248451a4cdd67a4764c25b2494bec47158`; all its member SHA remain unchanged. Its four RESULT identities exactly match the new six-source packet. The new CH-F256 has UUID `3b949083-a0f8-4778-92f1-d940c66acfe6`.

## Whole-replay performance and relative-improvement decomposition

| Design | P0 cycles | F128 cycles | F256 cycles |
| --- | --- | --- | --- |
| CH | 28,428,842 | 29,882,110 | 31,081,550 |
| DH | 31,880,220 | 31,894,637 | 31,321,955 |

| Profile | S_CH=CH0/CH_F | S_DH=DH0/DH_F | CH_F/DH_F | I=S_DH/S_CH | DH extra cycles vs CH_F % |
| --- | --- | --- | --- | --- | --- |
| F128 | 0.951367 | 0.999548 | 0.936901 | 1.050644 | 6.734889 |
| F256 | 0.914653 | 1.017823 | 0.992325 | 1.112797 | 0.773465 |

F256 I factorization: `1.112797 = 1.093310 (CH cycle-regression factor) * 1.017823 (DH self-speedup)`. This prevents relative-benefit improvement from being presented as an 11.28% DH self-speedup. In log-ratio bookkeeping, 83.47% of the increase in log(I) comes from the CH regression factor; that is an arithmetic decomposition, not a fraction of runtime or causal attribution. For F128, CH worsens 5.1119% and DH worsens 0.0452%; its positive I therefore comes from CH worsening more.

## Kernel location

| Design/profile | K1 cycles | K2 cycles | Total | K1 delta vs same-design P0 | K2 delta vs P0 |
| --- | --- | --- | --- | --- | --- |
| CH-P0 | 26,677,630 | 1,751,212 | 28,428,842 | 0 | 0 |
| CH-F128 | 28,130,567 | 1,751,543 | 29,882,110 | 1,452,937 | 331 |
| CH-F256 | 29,329,642 | 1,751,908 | 31,081,550 | 2,652,012 | 696 |
| DH-P0 | 30,226,439 | 1,653,781 | 31,880,220 | 0 | 0 |
| DH-F128 | 30,240,733 | 1,653,904 | 31,894,637 | 14,294 | 123 |
| DH-F256 | 29,667,936 | 1,654,019 | 31,321,955 | -558,503 | 238 |

CH-F256 regression 2,652,708 cycles splits K1+2,652,012 and K2+696. DH-F256 improvement 558,265 cycles splits K1-558,503 and K2+238. Thus almost all net change is localized to K1, while K2 changes are small and adverse. It would be inaccurate to say K2 is exactly unchanged. F128 follows the same localization pattern but has opposite DH sign.

## Read/write traffic and visible admission events

Units: L2 GLOBAL accepted reads and misses are 32-byte sectors; accepted excludes reservation retries and equals HIT+HIT_RESERVED+MISS+SECTOR_MISS. GLOBAL misses=MISS+SECTOR_MISS. DRAM read/write values are issued 32-byte data atoms across 20 controllers, not necessarily the same access population as GLOBAL reads. All-L2 misses include write-related access types; their count must not be relabeled GLOBAL read misses.

| Counter | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- |
| L2 GLOBAL accepted read sectors | 65,889,456 | 65,185,968 | 59,797,416 | 49,155,352 | 50,320,284 | 47,774,604 |
| L2 GLOBAL read misses | 16,720,180 | 18,006,712 | 18,699,980 | 19,387,556 | 19,331,416 | 18,958,508 |
| All-L2 misses | 16,724,596 | 18,011,634 | 18,704,668 | 19,392,856 | 19,336,710 | 18,963,609 |
| DRAM issued read atoms32B | 16,720,180 | 18,006,712 | 18,699,980 | 19,387,556 | 19,331,416 | 18,958,508 |
| DRAM issued write atoms32B | 4,924 | 5,430 | 5,196 | 5,808 | 5,802 | 5,609 |
| All-L2 reservation retries | 39,327,664 | 36,585,050 | 39,180,362 | 158,818,027 | 162,551,103 | 153,895,441 |
| ICNT-to-memory blocked admission events | 31,062,137 | 28,953,175 | 31,852,593 | 158,348,591 | 162,334,002 | 154,961,097 |

F256 vs P0, within-design facts:

### CH

| Counter | P0 | F256 | Delta | Change % |
| --- | --- | --- | --- | --- |
| L2 GLOBAL accepted read sectors | 65,889,456 | 59,797,416 | -6,092,040 | -9.245850 |
| L2 GLOBAL read misses | 16,720,180 | 18,699,980 | 1,979,800 | 11.840782 |
| All-L2 misses | 16,724,596 | 18,704,668 | 1,980,072 | 11.839281 |
| DRAM issued read atoms32B | 16,720,180 | 18,699,980 | 1,979,800 | 11.840782 |
| DRAM issued write atoms32B | 4,924 | 5,196 | 272 | 5.523964 |
| All-L2 reservation retries | 39,327,664 | 39,180,362 | -147,302 | -0.374551 |
| ICNT-to-memory blocked admission events | 31,062,137 | 31,852,593 | 790,456 | 2.544757 |

### DH

| Counter | P0 | F256 | Delta | Change % |
| --- | --- | --- | --- | --- |
| L2 GLOBAL accepted read sectors | 49,155,352 | 47,774,604 | -1,380,748 | -2.808947 |
| L2 GLOBAL read misses | 19,387,556 | 18,958,508 | -429,048 | -2.213007 |
| All-L2 misses | 19,392,856 | 18,963,609 | -429,247 | -2.213428 |
| DRAM issued read atoms32B | 19,387,556 | 18,958,508 | -429,048 | -2.213007 |
| DRAM issued write atoms32B | 5,808 | 5,609 | -199 | -3.426309 |
| All-L2 reservation retries | 158,818,027 | 153,895,441 | -4,922,586 | -3.099513 |
| ICNT-to-memory blocked admission events | 158,348,591 | 154,961,097 | -3,387,494 | -2.139264 |

CH-F256 has fewer accepted read sectors but more read misses/DRAM reads and longer runtime. DH-F256 has fewer OO lower creations, fewer accepted read sectors, fewer read misses/DRAM reads and lower runtime. These are associations, not proof that a particular reduction caused the cycle change. In cross-design F256, DH still issues 18,958,508 read atoms versus CH 18,699,980 (about 1.38% more); do not claim lower DRAM traffic than CH.

Print-boundary kernel intervals below are legitimate differences only where both snapshots explicitly print the cumulative field. They classify events by completion-print interval, not by which kernel originally generated an outstanding request. No means, gauges or peaks are differenced.

| Source | Kernel | L2 GLOBAL accepted | GLOBAL miss / DRAM read atoms | DRAM write atoms | L2 retry events | ICNT admission blocks |
| --- | --- | --- | --- | --- | --- | --- |
| CH-P0 | 1 | 63,783,600 | 14,637,516 | 4,580 | 39,327,664 | 31,062,137 |
| CH-P0 | 2 | 2,105,856 | 2,082,664 | 344 | 0 | 0 |
| CH-F128 | 1 | 63,080,112 | 15,917,012 | 5,094 | 36,585,050 | 28,953,175 |
| CH-F128 | 2 | 2,105,856 | 2,089,700 | 336 | 0 | 0 |
| CH-F256 | 1 | 57,691,560 | 16,605,504 | 4,900 | 39,180,362 | 31,852,593 |
| CH-F256 | 2 | 2,105,856 | 2,094,476 | 296 | 0 | 0 |
| DH-P0 | 1 | 47,049,496 | 17,313,036 | 5,464 | 158,818,027 | 158,348,591 |
| DH-P0 | 2 | 2,105,856 | 2,074,520 | 344 | 0 | 0 |
| DH-F128 | 1 | 48,214,428 | 17,258,976 | 5,526 | 162,551,103 | 162,334,002 |
| DH-F128 | 2 | 2,105,856 | 2,072,440 | 276 | 0 | 0 |
| DH-F256 | 1 | 45,668,748 | 16,873,316 | 5,317 | 153,895,441 | 154,961,097 |
| DH-F256 | 2 | 2,105,856 | 2,085,192 | 292 | 0 | 0 |

Both kernels have explicit read-miss/DRAM-read equality here, retained separately in JSON. K2 contributes 2,105,856 accepted read sectors in every run; its explicit retry/admission differences are 0. This narrows the visible pressure changes to the K1 print interval, without claiming that every L2/DRAM event is intrinsically request-origin attributed to K1.

## Retry reasons, distinct from time or occupancy

| Raw positive-only reason | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:LINE_ALLOC_FAIL | 3,213,805 | 2,934,740 | 3,001,567 | 335,494 | 312,763 | 252,060 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MISS_QUEUE_FULL | 7,111,605 | 12,524 | MISSING | 18,806,950 | 106,080 | 25,877 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MSHR_ENRTY_FAIL | 26,793,345 | 30,902,794 | 33,247,280 | 139,657,561 | 162,115,286 | 153,600,188 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MSHR_MERGE_ENRTY_FAIL | 2,206,900 | 2,730,603 | 2,928,734 | 17,636 | 15,807 | 17,251 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_W:LINE_ALLOC_FAIL | 2,009 | 4,389 | 2,781 | 386 | 1,167 | 65 |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_R:LINE_ALLOC_FAIL | 380,560,543 | 384,229,310 | 379,382,735 | MISSING | MISSING | MISSING |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_R:MISS_QUEUE_FULL | 298 | 228 | 356 | MISSING | MISSING | MISSING |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_W:LINE_ALLOC_FAIL | 12,822,796 | 13,106,222 | 13,120,569 | MISSING | MISSING | MISSING |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_W:MISS_QUEUE_FULL | 139 | 74 | 52 | 1 | MISSING | MISSING |

DH read MISS_QUEUE_FULL drops 18,806,950 ->106,080 ->25,877 across P0/F128/F256, yet F128 is slightly slower and F256 only modestly faster. DH read MSHR-entry failures move 139,657,561 ->162,115,286 ->153,600,188, so F256 is lower than F128 but still above P0. CH read entry/merge-limit failures grow across the profiles while total retries do not track cycles monotonically. MISS_QUEUE_FULL reduction therefore does not establish that downstream pressure disappeared.

MSHR_ENRTY_FAIL means entry-capacity retry events; MSHR_MERGE_ENRTY_FAIL means an existing-address merge-list limit. Neither count is occupancy, a stalled-cycle fraction or critical-path duration, and the two reasons cannot be conflated. Positive-only reason omission is MISSING, not an inserted0: CH-F256 read MISS_QUEUE_FULL is not printed, and this packet does not fill it with 0. No new MSHR/capacity experiment is proposed or launched by this analysis.

## Typed frontend request conservation and service

CH PAPER_BASE uses common PIB 256. DH PAPER_OO uses actual OO PIB 128; generic pib_entries 8 is inactive for OO admission. CH common Tag conflicts/PIB-full values never populate OO fields. OO PIB-full and OO Tag-bank-conflict events are unprinted and stay null. CH finite-service extension disabled is not unlimited ordinary-cache service. Cross-design L1, Tag, physical pool, queues, timing and area differ and are not equal-resource controls.

| Frontend event | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- |
| CH common Tag-bank conflict attempts | 20,972,288 | 20,972,288 | 20,972,288 | MISSING | MISSING | MISSING |
| CH common PIB-full events | 0 | 0 | 0 | MISSING | MISSING | MISSING |
| OO valid-line hits | MISSING | MISSING | MISSING | 5,997,156 | 5,695,060 | 6,333,732 |
| OO pending-line hits | MISSING | MISSING | MISSING | 64,342 | 75,205 | 72,953 |
| OO new-line misses | MISSING | MISSING | MISSING | 12,288,838 | 12,580,071 | 11,943,651 |
| OO 128B lower creations | MISSING | MISSING | MISSING | 12,288,838 | 12,580,071 | 11,943,651 |
| OO tag-map evictions | MISSING | MISSING | MISSING | 12,272,454 | 12,563,687 | 11,927,267 |
| OO ready-but-writeback-blocked events | MISSING | MISSING | MISSING | 553 | 487 | 378 |

DH valid+pending+new classifications conserve 18,350,336 OO line probes in each run. New misses=lower created=issued=responses=acquired/released credits, while accepted L2 GLOBAL sectors=4*128B lower creations. F256 valid hits rise and new misses fall relative to P0, consistent with changed reuse timing/retention; those facts do not prove a specific Tag/MSHR cause. The 128B OO count is not a DRAM 32B atom count, and cannot be compared directly with a CH retry count.

| DH profile | Mean PIB entries (all64SM samples) | Mean physical lines | Ready-to-retire cycles / retired entry | Map-loss-to-free cycles / event |
| --- | --- | --- | --- | --- |
| P0 | 1.675717 | 152.614330 | 4.226082 | 4991.227632 |
| F128 | 1.699331 | 152.769695 | 4.273918 | 4902.379787 |
| F256 | 1.702958 | 152.142801 | 4.297116 | 4982.723806 |

DH finite-service retired denominator stays 2,097,408. Ready-to-complete sums 8,863,818 ->8,964,149 ->9,012,806 and ready-to-collect sums 3,001,940 ->3,101,937 ->3,149,947 increase, while writeback wait 36,683 ->34,839 ->32,781 decreases. F256 speedup therefore cannot be summarized as every service latency decreasing. Low all-SM mean PIB occupancy (~1.7 entries) does not rule out a brief, per-SM, dependency or burst bottleneck. Peaks and terminal gauges remain separate in the source JSON.

## Reported latency diagnostics and configuration coupling

| Source | Reported average mflatency | Reported avg ICNT-to-mem | Reported avg ICNT-to-shader | Reported avg MRQ |
| --- | --- | --- | --- | --- |
| CH-P0 | 620 | 152 | 39 | 412 |
| CH-F128 | 628 | 158 | 40 | 553 |
| CH-F256 | 685 | 172 | 40 | 691 |
| DH-P0 | 2,369 | 428 | 226 | 745 |
| DH-F128 | 2,391 | 413 | 257 | 1,389 |
| DH-F256 | 2,398 | 426 | 230 | 1,873 |

These integer means have known print/update/sample-window limits (500,000 cycle sampling; un-folded tail may be omitted); MRQ is a separate cumulative request mean with its own denominator, measured in global core cycles from DRAM request construction to bank assignment. It is not complete L2-to-DRAM service time or a critical-load latency. DH F256 printed MRQ rises to 1873 from 745 at P0 despite the total cycle improvement. The existing counters therefore do not establish that average DRAM queue waiting fell. Means are never subtracted across kernels, summed, converted from missing to0 or compared as equal-population CH/DH request lifetimes.

Within each design only FR-FCFS queue parameter changes 64/128/256. Fixed Core also couples memory-partition shared-credit limits 255/319/447 through `FR_queue + return_queue 192 - (subpartitions 2-1)`; private credit remains 1/subpartition and separate DRAM write queue is disabled. DRAM 850 MHz, Core/ICNT/L2 clocks, 10 MiB L2 capacity/mapping and each design's frontend mechanism stay fixed. A bigger F changes scheduling/admission/reuse timing, not merely an isolated queue-size scalar with all other structure effects absent.

## Facts, associations, hypotheses and unresolved mechanism

Established: F256 DH improves slightly but remains slower than matched CH; CH regresses substantially; both effects are almost entirely K1. DH lower requests/read traffic and visible lower retries decline while some entry/service metrics do not. CH read misses/DRAM reads rise despite fewer accepted sectors. These are direct closed-run observations with source identity.

Associated but not isolated: downstream-window/shared-credit changes coincide with altered OO reuse classification, lower traffic and admission pressure. Relative closure toward CH is dominated arithmetically by CH deterioration. Static source predicts access-direction and true ATAX tmp dependencies; it does not prove which measured counter is on the critical path.

Hypothesis: request-timing/reordering and lifetime changes redistribute cache residency/overlap in K1, helping DH at F256 but harming CH. Queue/bank/credit occupancy histories and dependency-tagged latency would be required to isolate this. Larger windows do not guarantee monotonic cycles, and existing aggregate retry counts cannot establish capacity additions as a remedy.

Fixed candidate source is Atlas47a097aad4406893a07f8d230e1e0a850609bf39 / app commit dad09cb0487845edc7524ded814c6cde9f0ef6a1, `ATAX/atax.cu:84-110;139-176`, SHA bca826a6e4fbdad67b11400ef2193210f43d8181441a0b9883e19445db049cfb. Candidate tmp/y initialization and capture ELF/numeric linkage limits remain unresolved. The trace full-body contract covers all declared instructions/CTAs and kernel order; it does not newly prove full native application semantics or numerical correctness. No trace, input extent or historical scientific state was promoted.

## Reproduction and evidence

Run `python3 analyze_three_profiles.py`, then `python3 validate_and_derive.py`, then `python3 render_three_profiles.py` solely to regenerate this new analysis directory from closed sources. The two independent CH archive audits are in NEW_CH_F128/F256_INDEPENDENT_QUALIFICATION.json. ACTUAL_INPUT_AND_KERNEL_CONTRACT.json and BOUNDED_ACTUAL_TRACE_HEADERS.json bind the true two-kernel/grid contract. SIX_CLOSED_SOURCE_DATA.json includes raw gzip/uncompressed, NATIVE_EXIT and RESULT SHA, complete options, additive snapshots, exact-endpoint intervals, explicit positive-only reasons, means/gauges/peaks and all source paths. Typed files preserve active-path capacities and nulls. Consumed counter catalog and fixed mechanism/source evidence retain their original byte identity.

CPU_VALIDATION.json records 61 passing checks, including original F128 packet preservation, exact original reference identities, strict traffic reconciliation, additive endpoint conservation, OO request conservation, fixed clocks/cache and no fabricated missing counters. No GM, workload winner selection or new scientific execution was performed.

| Source | RESULT path | RESULT SHA256 | UUID | Raw gzip SHA256 |
| --- | --- | --- | --- | --- |
| CH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-eededb785179fc04-CH-P0-V1.RESULT.json | 5364ea570de11a9929d5107c259a2cdbd9d440ea0b71ed178a75b34a04944be2 | 681b81cd-4add-4802-a5f0-1994b9156847 | 13601558d34af40e02cd99d7016889d8f9d335ed441152ade4f1489c7673fa9d |
| CH-F128 | /root/data/dtc_stage_iia_first16_20261104_v1/analysis/E2-DTC2A16-eededb785179fc04-CH-F128-V1.RESULT.json | e4369993a3944d1545ada90558b8f0cbcdda3b39dc11dd44ff91304c89d39fc3 | 33aad24a-ce6f-43ec-9e1a-50fdaa9e435f | ed48d943dabea7d61c79ac7987ecad5c6651fa364746c483add4a6a6153a587e |
| CH-F256 | /root/data/dtc_stage_iia_first16_20261104_v1/analysis/E2-DTC2A16-eededb785179fc04-CH-F256-V1.RESULT.json | 1bd816a1c585d078942e31a09a38da745c0bad4dc351eb335101bad381937dd1 | 3b949083-a0f8-4778-92f1-d940c66acfe6 | 56703c81f4d2ff29c715ca2a63095331d593e4141115d830a01658a20847247c |
| DH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-eededb785179fc04-DH-P0-V1.RESULT.json | 7a0df4d27305dab8ae9da64a2cbfe51c0c01d6d0c8cf2e91243a7ce471ef3ab2 | 37325f35-2eb7-4a2b-bba9-5dc5d00e497f | 7bd14588f91c972185fd766d203dcd9d71622fb6d998e4b0484fb74b83dd6c29 |
| DH-F128 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-eededb785179fc04-DH-F128-V1.RESULT.json | 4c77fdd4c24f28413f29f3048be661fff672428d62c90d766c9805e2d7201b29 | aa96f79e-b5b2-48ae-894b-5632732dcb99 | 836d5fb2e8c62ce1eff73d4d8d8d0e3dc127f0b3d2bdd382ee3898b232443e83 |
| DH-F256 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-eededb785179fc04-DH-F256-V1.RESULT.json | 01d87ac3c88736f0d5f67437d5c295e8018a41c7f5f20774c9eee0061bfc4f14 | 3a266b8a-a956-4610-90ee-3fddf97b179f | 387285e6bad7ee00e48334ea215936fcc92d7a71d517ea2225843f62746ab62e |
