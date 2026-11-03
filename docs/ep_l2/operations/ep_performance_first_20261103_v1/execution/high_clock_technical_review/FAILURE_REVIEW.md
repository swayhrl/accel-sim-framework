# Vector4M F1275: bounded technical failure review

Decision: HOLD unconsumed EP cells with DRAM>CORE1132 until a newSource qualification proves completion-CAM backpressure. Keep current GEMM1020 models untouched. No retry/refund or source/pipeline edit was performed by this audit.

## Established facts

PROVEN: actual Source78/ELF78d4 Vector4M F1275 aborted at gpu-cache.cc2724, native wait-6 after50.04s. It is a technical negative, not an accepted performance point. Its small compressed raw was decompressed once (162699 logical bytes; actual stored17081 bytes); only a bounded tail was retained. No trace body was read.

PROVEN: failure is the TVD completion-address CAM path for completed L2_WRBK_ACC writebacks. memory_sub_partition::set_done(l2cache.cc2755-2760) invokes ep_l2_wad_complete only for L2_WRBK_ACC, passing GPU core-cycle counter and original requestUID. gpu-cache.cc2721-2731 checks one completionCAM access per core physical cycle, then directory/WB_INFLIGHT/UID identity; the fatal assertion precedes the latter identity checks. This is not an RO fill, Tag detach, or new-request front-end path. F includes TVD, but RO is not required: WV also has this path. S has no TVD directory and skips this particular CAM check; W-only similarly does not require this TVD CAM. L1_WRBK_ACC completion does not call this WAD lookup.

PROVEN code: detailed dram_t::cycle(dram.cc295-318) pops at most one returned DRAM data command per DRAM tick. A completed L1/L2 WB immediately calls partition.set_done, then deletes its mem_fetch. There is no busy result, completion-CAM pending queue, or retry between this callback and the per-core-cycle CAM assertion. partition.set_done(l2cache.cc858-869) returns credit then delegates to the owning subpartition. Read returns instead enter DRAM ReturnQ; they are a different population.

PROVEN clock structure: next_clock_domain(gpu-sim.cc2113-2133) independently advances DRAM/core domain times. DRAM service occurs at2195-2201 before the GPU core counter increments only on CORE at2284. Thus a faster DRAM domain can call the same subpartition completion twice while the core counter is unchanged.

ACTUAL CPU calendar control: copied production clock-selection code,10000 core-counter intervals, no GPU or requests. At850/1020/1132 it produced at most1 DRAM callback per core counter; at1275/1700 it produced2 (first duplicate corecounter8/2). This proves calendar opportunity and assertion predicate, not the exact failing two packet identities or a full DRAM/WB reproduction.

LIKELY dominant causal chain: two legal L2 dirty-WB completions for the same slice arrive on two DRAM ticks sharing a GPU core counter; the first uses the CAM, the second hits the assertion because no backpressure bridges the domains. Dirty evictions use get_modified_size(gpu-cache.cc511-514); sector blocks can be partially dirty, so do not assume every WB requires four32B beats and cannot complete on consecutive DRAM ticks. The raw assertion does not reveal both UIDs/addresses/timestamp, so those exact identities remain UNKNOWN.

## Classification and scope

P1 PROVEN implementation/model limitation: a real finite one-query-per-core-cycle completion resource is asserted but its faster-producer overflow is not queued/backpressured. At newly authorized highDRAM clocks this ends a legal modeled request stream instead of stalling it. The single-port hardware cost itself is P2, and must remain charged. Removing the assertion, permitting unlimited same-cycle completion lookups, or switching its clock unit to DRAM merely to bypass it would be an unproven hardware change.

P0 not demonstrated: this aborted point was closed unaccepted and retained. No evidence shows silently wrong accepted data, missing protection, or contamination of accepted850/1020 results. Newclock production-parser/clock-init/terminalCPU tests passed but did not exercise simultaneous WBs; they were insufficient dynamic qualification for DRAM>CORE. That qualification gap must be recorded rather than treating the crash as a performance slowdown.

850/1020 boundary: for this exact detailed production path and fixedCORE1132, at most one DRAM callback per core counter prevents this specific over-subscription. Each slice belongs to one partition; parallel channels do not share the per-cache CAM counter. This is not a universal proof that all Source78 paths are bug-free. Existing accepted850/1020 data need not be invalidated solely because1275 aborted. Do not stop the healthy GEMM S/WV1020 runs.

1275/1700 risk: any WV/F workload with TVD-backed dirtyWB completion can encounter it, including futureGEMM/FWT. Trigger depends on actual completion spacing/address distribution, so failure of every workload is not asserted. Until qualified, unconsumed EP cells aboveCORE should be technicalHOLD. S may be individually valid (VectorS1275 accepted53910cycles), but avoid spending unmatched S extensions before a viable EP pair exists. Main owns those future admission decisions.

## Minimal next engineering step, not executed here

1. Independent newSource CPU fixture: two distinct same-slice WB_INFLIGHT directory rows, real originalUID bindings and valid payload generations; two32B dirty-sector WBs become complete on adjacentDRAM ticks mapped to one core counter. Exercise the real dram_t->partition->subpartition completion route. Demonstrate the old assertion before any repair; no full application.
2. Design finite completion holding/backpressure across the DRAM/core boundary, with oneCAM query per corecycle. Preserve packet/UID/directory/payload ownership until completion commits; current dram_t deletes the WB immediately after set_done, so simply returning early is unsafe. Define credit-return ordering, bounded queue capacity, saturation, fairness and drain. No protection is relaxed.
3. CPU controls: same/different slices, RO/read versusL2WB populations, back-to-backcore/DRAM clocks850/1020/1275/1700, queuefull, ReturnQ pressure, staleUID, generation reuse, pinnedVictim and complete drain. Compare default850 behavior and measured query accounting. Then newSource Host/native identity and controlled sameELF S/EP application references would require separate explicit Main qualification and launch scope. No automatic retry of the already spent F1275 point.
