# Counter semantics for final Stage II-A analysis

The strict `metrics` object is the **last printed numeric dictionary with mixed scopes**. It is neither uniformly an isolated last-kernel table nor uniformly an application total. Top-level cycles and proof.kernels remain correctly scoped performance evidence; no simulator, parser, consumer, raw result or accepted identity was modified.

The main audit reads 32 frozen original references plus the first accepted vectorAdd CH-F128: 33 closed, SHA-verified raw files and 177 kernel print blocks. All use stream 0. Source authority is fixed Core 9eedb313 / Framework 02775fd7, with actual runtime parser bytes separately recorded. The newly accepted convolutionSeparable CH-F256 is a separate34th-source addendum; the original33-source audit stays unchanged.

## Cumulative totals and print intervals

Framework cleanup prints finished-kernel stats before calling update_stats. Core update_stats folds/resets gpu_sim_cycle and gpu_sim_insn into gpu_tot_*; therefore metrics.gpu_sim_* is the last interval, while gpu_tot_* and top-level strict cycles cover the replay. The strict helper explicitly returns numeric(last block) and traffic(last block).

Live L2 caches, DRAM controller counters, gpu_stall_icnt2mem and persistent DTC frontend/service counters are not reset by that cycle fold. The `l2_stats.clear()` beside printing initializes a temporary aggregate; it does not clear the live L2s. Named L2 buckets filter by finished stream; global L2 substats aggregate all streams. For this audited single-stream set, the final L2 bucket snapshot is a cumulative replay total. For any later multistream input, it is not automatically an all-stream total.

Empirical examples: scan DH-P0's final GLOBAL_ACC_R accepted count is21,859,084 sectors; summing its33 cumulative snapshots would incorrectly yield399,626,632. Its DRAM reads are21,712,700atoms, not397,929,992from summing snapshots. convolutionSeparable DH-P0 final accepted reads4,645,512 likewise include the earlier first-phase1,730,616. All33 final strict traffic and selected numeric values match the final raw block exactly; audited additive counters are nondecreasing.

PRINT_BOUNDARY_ADDITIVE_DELTAS.json provides lawful differences of an explicit additive subset. These are **intervals between printed boundaries**, not automatic origin-kernel attribution: pending memory/write tails and inter-kernel copies need consideration. It never differences means, gauges or running peaks. Peak_per_SM can be a maximum across SMs; occupancy/outstanding0 at drain does not mean no pressure. Do not sum cumulative snapshots or interpret retry/SM-cycle sums as disjoint wall-clock time.

## Latency missingness: no decimal-regex loss in these data

Across all33 closed sources, zero tokens for avg_mrq_latency, averagemflatency, avg_icnt2mem_latency or avg_icnt2sh_latency contain decimals; fixed Core prints these with `%lld`. Eight sources print none of these mean fields. Thus the current empty latency_counters object is not evidence of a decimal being discarded by stage2_strict's integer regex. A future floating format would require an independent parser review; no pinned parser is changed here.

The concrete accepted vectorAdd CH-F128 records maxmflatency=4971 and maxmrqlatency=1828 but no mean lines. Its 214503 cycles are below the configured 500000-cycle sample period. memlatstat_done collects pending per-window sums; memlatstat_lat_pw folds them into num_mfs/mf_total_lat at periodic sampling or update_stats. cleanup prints first, update_stats folds afterward. num_mfs can therefore still be 0 when the single short kernel prints, suppressing all four means despite positive measured latency maxima.

For short multikernel convolution, the second print can have prior-kernel num_mfs/mf_total_lat but an un-folded current-kernel tail. ICNT cumulative numerators can have a different tail boundary from num_mfs. These three printed response/ICNT means are not certified exact final application means. The separate new CH-F256 addendum corroborates this: kernels 288224 and 313876cycles each below 500000; first print has no means, second contains averagemflatency=112 and avg_icnt2mem_latency=5369. Do not interpret that pair as a physically additive end-to-end latency decomposition.

MRQ is distinct: its numerator/denominator are updated together at DRAM bank assignment and, when printed, yield a cumulative request-conditioned queue-age mean in global core cycles. The outer num_mfs guard may still suppress it. It starts at dram_req creation and stops at bank assignment, so it is not total L2→DRAM time or DRAM service time. MRQ request counts are not necessarily DRAM32B atom counts. Never add/difference unweighted means or infer critical-path delay solely from them.

## Released comparison rules

For same-input, same-design P0/F128/F256, compare top-level cycles, cumulative GLOBAL_ACC_R32B accepted/miss sectors, typed all-L2 access/miss/retry totals, issued DRAM read/write32B atoms and explicitly defined DTC additive events/integrals. Report units and source domain. GLOBAL_ACC_R only differs from DRAM reads that also include L2 write-allocation. MSHR_HIT supplements SECTOR_MISS and WRITE_ALLOCATED supplements MISS, so neither is added a second time.

gpu_stall_dramfull is actually cumulative ICNT→subpartition admission blockage: one increment per L2 tick per full subpartition with a waiting packet. It can greatly exceed GPU cycles; it is not isolated FR-FCFS queue-full time. MSHR failures are retry-event reasons, not PIB occupancy, tag allocation loss or waiting latency. Raw bracketed fail reasons are absent from numeric-only strict metrics and positive-only printing can omit reasons; absent remains unavailable. DTC tag-bank arbitration conflicts and mapping evictions must be kept distinct. Within-design F comparisons do not imply identical CH/DH L1 mechanism/area conditions.

The machine-readable COUNTER_SCOPE_CATALOG.json specifies 14 families, units, exact scope, lawful use and exclusions. SOURCE_RESET_PRINT_EVIDENCE.json binds 13 source files and relevant line excerpts by SHA. CLOSED_RAW_SCOPE_AUDIT.json binds every accepted result/native exit/raw SHA; CPU_READONLY_VALIDATION.json records 9 passing checks. Existing memcpy-to-L2 preload and flush policy remain fixed and must accompany zero-DRAM interpretation. All results remain trace-defined replay evidence, not complete CPU+GPU application timing or real-GPU traffic claims.
