# vectorAdd: six-source F128/F256 negative control

**Finding:** F128 speeds up both CH and DH but CH improves more; F256 slows both, especially DH. DH F256 uses 8.7030% more cycles than DH-P0 and 5.9174% more cycles than matched CH. This occurs despite unchanged accepted read/miss/DRAM-read counts and much lower aggregate retry/admission events. It is a counterexample to using fewer retries as a sufficient predictor of faster performance.

One frozen input, six closed accepted sources; both new CH results independently pass frozen read-only strict/true164/native-restore audits. No active scan/MVT result is read, no workload/configuration is dropped, and no per-program best variant is used for a GM. No model, source, registry, owner, controller, budget or paper was changed.

## Identity and real kernel contract

Input digest `e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799`. Canonical spec, full declared-body qualification, strict/raw statistics and bounded header agree: one stream0 kernel `_Z6VecAddPKfS0_Pfi`,84,000,768 active-thread instructions,23,438 CTAs, grid (23438,1,1),block (256,1,1). This is the frozen DTC6M trace identity; the same-name EP4M input remains separate. No ATAX/BICG 145m two-kernel shape is reused. Whole declared trace coverage does not newly prove capture-time ELF/numeric input or full native application identity.

Fixed Core `9eedb3131937748f0492fa83aad37d3691118d70`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`, binary SHA `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`. The four original references are exact original-index rows by full digest/cell/profile; the two new CH points keep STAGEII_AUTHORIZED_CH role. No R2/IR/EP/PQPS substitution or historical negative promotion occurs.

## Performance: all three profiles

| Profile | CH cycles | DH cycles | S_CH | S_DH | CH/DH | I=S_DH/S_CH |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | 220,803 | 217,305 | 1 | 1 | 1.016097 | 1 |
| F128 | 214,503 | 213,053 | 1.029370 | 1.019957 | 1.006806 | 0.990856 |
| F256 | 223,020 | 236,217 | 0.990059 | 0.919938 | 0.944132 | 0.929175 |

F128 reduces CH cycles 2.8532% and DH cycles 1.9567%; I=0.990856 so the relative DTC advantage contracts. F256 increases CH cycles 1.0041% and DH cycles 8.7030%; I=0.929175 and DH now takes 5.9174% more cycles than CH. All behavior is in the single captured kernel. This negative result remains part of the fixed input set.

## Fixed read traffic, changing writes and retry mix

L2 GLOBAL read accepted/miss values use 32-byte sectors; accepted excludes retries and misses=MISS+SECTOR_MISS. DRAM data values are issued 32-byte atoms across 20 controllers. All six raw L2 access totals and all-L2 misses are 2,250,000 with zero pending hits; GLOBAL read accepted/misses and issued DRAM reads are 1,500,000. These units/populations remain distinct, even though some counts coincide here.

| Counter | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- |
| L2 GLOBAL accepted read sectors32B | 1,500,000 | 1,500,000 | 1,500,000 | 1,500,000 | 1,500,000 | 1,500,000 |
| L2 GLOBAL read misses32B | 1,500,000 | 1,500,000 | 1,500,000 | 1,500,000 | 1,500,000 | 1,500,000 |
| DRAM read atoms32B | 1,500,000 | 1,500,000 | 1,500,000 | 1,500,000 | 1,500,000 | 1,500,000 |
| DRAM write atoms32B | 632,946 | 633,276 | 634,236 | 633,008 | 633,669 | 634,352 |
| All-L2 reservation retry events | 5,098,612 | 5,346,628 | 2,937,120 | 5,068,832 | 5,382,152 | 2,472,990 |
| ICNT-to-memory blocked admission events | 4,905,178 | 5,263,792 | 2,987,121 | 4,943,384 | 5,192,847 | 2,374,608 |

DH F256 vs P0: all-L2 retry events fall 5,068,832 to 2,472,990 (-51.21%), ICNT admission blocks fall 4,943,384 to 2,374,608 (-51.96%), yet cycles increase 8.70%. DRAM writes rise 633,008 to 634,352 (+1,344 atoms, about 0.212%). Issued writes are measured during the replay, not proof of complete end-of-run dirty-cache drainage or a changed application store count. The small traffic change alone does not establish the cause of the much larger cycle regression.

| Positive-only retry reason | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
| --- | --- | --- | --- | --- | --- | --- |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MISS_QUEUE_FULL | 4,993,723 | 4,145,043 | 296,544 | 4,980,069 | 4,142,175 | 311,125 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MSHR_ENRTY_FAIL | 89,242 | 1,193,294 | 2,640,269 | 73,050 | 1,231,551 | 2,161,234 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_W:MISS_QUEUE_FULL | 15,647 | 8,291 | 307 | 15,713 | 8,426 | 631 |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_W:MISS_QUEUE_FULL | MISSING | MISSING | MISSING | 21 | 36 | 294 |

DH read MISS_QUEUE_FULL falls 4,980,069 ->4,142,175 ->311,125, while entry-capacity failures rise 73,050 ->1,231,551 ->2,161,234. CH has the same qualitative substitution of fewer miss-queue retries and more entry-capacity failures. These are retry event counts, not occupancy or stall-cycle durations. MSHR entry capacity is distinct from an existing-address merge-list limit; unprinted merge reasons remain MISSING rather than inserted 0. A lower sum of retries does not imply lower critical-path wait, and does not justify a capacity remedy by itself.

## Typed frontend and finite service

CH PAPER_BASE common PIB 256 and DH PAPER_OO PIB 128 remain distinct. DH generic PIB 8 is inactive for OO admission. CH common Tag/PIB counters are not OO fields; unprinted OO PIB-full/Tag-conflict counters stay null. Cross-design differences in L1/Tag/pool/queues/finite service/timing/area remain disclosed, so these are not equal-resource designs.

All three DH runs explicitly print 375,000 OO new misses,0 valid hits and0 pending hits;375,000 lower128B creations/issued/responses/acquired/released credits and 1,500,000 accepted read sectors conserve exactly. These explicit zeros are actual observations in the OO classification domain; they do not license filling missing fields with zero. The workload offers no observed OO read-line hit/merge benefit in this frozen replay. Static two-read/one-write source structure is not used as a substitute for these counters.

| DH profile | Mean PIB entries, all64SM samples | Mean physical lines | Ready-to-retire cycles / retired read entry | Map-loss-to-free cycles / event | Writeback wait events |
| --- | --- | --- | --- | --- | --- |
| P0 | 59.434765 | 483.290823 | 2.161637 | 0.559296 | 26,947 |
| F128 | 64.824821 | 483.587843 | 2.161541 | 1.002311 | 26,012 |
| F256 | 56.316115 | 486.644097 | 2.250936 | 8.729043 | 40,069 |

Finite-service retired denominator is 375,000 read entries for each profile. F256 ready-to-complete sum 844,101 exceeds P0 810,614 and F128 810,578; writeback wait 40,069 exceeds 26,947/26,012. Map-loss-to-free sum 2,987,358 is much larger than 191,409/343,023 for an equal 342,232 event denominator. These service-lifetime associations motivate examining tail/order behavior; their sums and per-entry ratios are not critical-path time or causal fractions. Means are sample/entry-specific; gauges/peaks are kept separate.

## Missing means and available extrema

All six strict mean latency dictionaries are empty, while explicit DRAM reads are nonzero. Each single-kernel replay ends before 500,000 cycles; fixed print-before-stat-fold ordering can leave num_mfs=0 at printing and suppress mean lines. Missing mean latency therefore remains MISSING, never zero, and does not indicate failed integer parsing or no DRAM delay.

| Source | Printed max mflatency | Printed max MRQ | Printed max ICNT-to-memory | Printed max ICNT-to-shader |
| --- | --- | --- | --- | --- |
| CH-P0 | 7,281 | 1,202 | 6,825 | 186 |
| CH-F128 | 4,971 | 1,828 | 4,300 | 176 |
| CH-F256 | 31,777 | 4,524 | 31,333 | 221 |
| DH-P0 | 6,386 | 1,111 | 5,827 | 209 |
| DH-F128 | 4,741 | 1,781 | 4,402 | 234 |
| DH-F256 | 46,970 | 4,503 | 44,545 | 284 |

F256 has much larger printed maxima, especially DH mflatency 46,970 versus P0 6,386/F128 4,741 and ICNT-to-memory 44,545 versus 5,827/4,402. These are extrema over their recorded event scope, not mean service time, exact queue residence or known critical loads. Their increase is a tail-behavior clue consistent with worsened ordering/response timing; it does not prove which request determined completion or isolate DRAM scheduling from shared credits, ICNT and finite service. No lifetime distribution or request-to-dependency map is available in these accepted logs.

## Configuration and evidence limits

Within each design only FR-FCFS size 64/128/256 changes, with coupled memory-partition shared-credit limits 255/319/447 (return queue 192, two subpartitions, private 1 each). DRAM 850 MHz and Core/ICNT/L2 clocks, 10 MiB L2 capacity/mapping and each design's frontend are fixed. F256 is not a pure isolated queue-capacity change and does not offer free/equal-area hardware.

Atlas47a097aad4406893a07f8d230e1e0a850609bf39 maps the candidate source at CUDA application commit b059fdae25c2aabf737486aada743fca114469ce (`vectorAdd.cu:78-83;launch86-133`) to two coalesced FP32 read streams and one store, with no required cross-CTA reuse. FIXED_SOURCE_PHASE_MAPPING.json retains the exact prior source/report SHA references. Capture-time source/ELF/numeric binding remains unresolved; full-body qualification certifies this declared trace scope, not arbitrary CUDA Samples builds.

Facts: matched F256 is negative despite unchanged reads/fewer visible retries, and certain printed service sums/extrema increase. Association: larger coupled window/credits changes timing and finite-service lifetimes. Hypothesis only: increased tail/ordering delays may outweigh reduced repeated admission attempts. Existing closed counters do not prove that mechanism or warrant a new experiment automatically. No new simulation or next 48 batch is scheduled.

## Reproduction and source locators

Run `python3 analyze_three_profiles.py`, `python3 validate_vector_control.py`, `python3 render_vector_control.py` to regenerate this new analysis directory only. SIX_CLOSED_SOURCE_DATA.json preserves all original/new identity roles, RESULT/raw/exit SHA, exact options, cumulative additive fields and separate means/gauges/peaks. Both new CH strict/archive/native-restore audits are retained. ACTUAL_INPUT_AND_KERNEL_CONTRACT.json and BOUNDED_ACTUAL_TRACE_HEADER.json pin the actual one-kernel contract; LATENCY_MISSINGNESS.json preserves empty means and explicit extrema; typed records preserve CHcommon/DHOO separation.

CPU_VALIDATION.json: 71 checks PASS; six closed sources, two independent newCH archive audits, zero live points consumed and zero runtime actions. Root alone publishes this packet.

| Source | RESULT path | RESULT SHA256 | UUID | Raw gzip SHA256 |
| --- | --- | --- | --- | --- |
| CH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-e7bb67e63e3c3847-CH-P0-V1.RESULT.json | 6e715695589e952eb9ae13c81ddefa0c31877fe29fbffa1ec780d397a3d98851 | d5cf2efe-f92d-4134-8369-9082dca173c5 | c16e40f80fcddc21090a294ea0dd94675bddcf510b5e53321a0cf53c07e5d39f |
| CH-F128 | /root/data/dtc_stage_iia_first16_20261104_v1/analysis/E2-DTC2A16-e7bb67e63e3c3847-CH-F128-V1.RESULT.json | 293ead6b9b3ec6a606cade4c0ccba88595ee5fee3b1a5cafcfbb54bb1d6e2eb3 | d7f59b7e-28e4-469b-ae15-ae93a913134b | f240826e6b2ffed8383cbf3e2a7546f645bbd9a61b863d2b811bb73db2fcf70a |
| CH-F256 | /root/data/dtc_stage_iia_first16_20261104_v1/analysis/E2-DTC2A16-e7bb67e63e3c3847-CH-F256-V1.RESULT.json | 88b7d4c3e93102ddb301e6c7eb4679abd371ded7e4a1c91360bd13a613ad5b14 | 296e83f8-7ee5-4181-8685-53d8f591b684 | 16b01b3604b42bb8985ec94199d14cd8d73b54682c79049e3497b79d3039843b |
| DH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-e7bb67e63e3c3847-DH-P0-V1.RESULT.json | 72b2d9257ae45e2d369a5583fd669d4b50e8f38d978be86bbc79e9a75278a8c9 | 16e5f3a0-4323-4715-a8bf-2716ab52d3ed | 9ce185c0432a207bf2694164db5fe9d9ea1a616916a7c6485e74e3edcdcc5200 |
| DH-F128 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-e7bb67e63e3c3847-DH-F128-V1.RESULT.json | 8814fa57c1904612c67b4e51ae2326320191d0f821eb0ceb9746c57b885d7c67 | 5f2af272-ea56-4782-8754-d29eeee17897 | d72d9d1c976475f35f39bf3ce2809be5af368d82901166ec9555a17378e05cd4 |
| DH-F256 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-e7bb67e63e3c3847-DH-F256-V1.RESULT.json | 57ffc0ee22572140e2ef47792c95e0d74f0ed7c57c8da1b90494183a427c0733 | cb4d2d90-e928-44da-8c62-187a3f7cb960 | 1825536f6664f074b29cea0e27b4d8bf07fa5d587295ae0ae5e789dcf4340ef7 |
