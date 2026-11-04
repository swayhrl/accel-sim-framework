# Five completed short programs: matched six-source evidence

This read-only supplement closes the previously uncovered transpose, mri-q, sad, sgemm and particlefilter_float evidence at the source-qualified snapshot observed 2026-11-04 03:06:57 UTC (11:06:57 CST). The complete Remaining48 snapshot had36 accepted and12 awaiting results. Only these five programs and their30 accepted sources were parsed; no live raw was consumed. This is neither final24 consumption nor a CORE32 population/GM conclusion. Original20 reference identities and10 new authorized CH identities remain separate.

## Performance facts

F128 and F256 are exactly equal to each other in every kernel's cycles and every selected additive print interval for both designs in all five programs. The following columns therefore show both variants together. S is P0/variant and R is CH_variant/DH_variant.

| Program | Kernels per source | CH P0 -> F128/F256 | DH P0 -> F128/F256 | S_CH | S_DH | R | I=S_DH/S_CH |
|---|---:|---:|---:|---:|---:|---:|---:|
| transpose |24|241346 ->241346|237820 ->237820|1|1|1.014826|1|
| mri-q |4|362244 ->362244|360174 ->359855|1|1.000886|1.006639|1.000886|
| sad |3|114310 ->114310|114870 ->114870|1|1|0.995125|1|
| sgemm |1|448633 ->448633|409417 ->409417|1|1|1.095785|1|
| particlefilter_float |36|1861126 ->1861126|2100874 ->2100874|1|1|0.885882|1|

Four programs are exact zero-response controls for both CH and DH. MRI-Q has only a small DH improvement:319 fewer cycles (0.08857% fewer; speedup1.000886). No program-level F regression occurs in this subset. Preserve absolute negative cases: DH remains560 cycles slower than CH in sad, and239748 cycles slower in particlefilter_float. This is distinct from an F-induced regression.

## Traffic and queue facts

All counts below are final cumulative replay totals. GLOBAL accepted/miss are32B sectors. DRAM read/write atoms are32B issued data-command atoms; L2 retry counts are events, not waiting time or occupancy. All six sources per program retain these traffic totals within each design.

| Program | L2 GLOBAL accepted CH / DH | L2 GLOBAL read misses CH / DH | DRAM reads CH / DH | DRAM writes CH / DH | L2 retry CH / DH | ICNT admission stall events CH / DH |
|---|---:|---:|---:|---:|---:|---:|
| transpose |1570304 /1520848|0 /0|0 /0|0 /0|0 /0|171469 /165183|
| mri-q |62208 /21248|8192 /8192|8192 /8192|0 /0|3132 /1937|0 /0|
| sad |164316 /161980|405 /405|405 /405|0 /0|0 /0|0 /0|
| sgemm |7444604 /7266512|140804 /140528|140804 /140528|0 /0|9287 /2128|1246 /22|
| particlefilter_float |104648 /1080156|24 /443|24 /443|0 /0|0 /0|0 /0|

transpose has no DRAM read, write or controller n_req in all six sources, while the legacy gpu_stall_dramfull field is nonzero. This independently illustrates why that field means blocked ICNT-to-subpartition admission events rather than DRAM-window waiting cycles. L2 all-type misses32768 are GLOBAL writes, not8192/32768 implied DRAM reads. Under fixed write-back/lazy-fetch-on-read, a counted write miss can allocate a modified sector without an immediate DRAM read.

sad has278443 all-type L2 misses, decomposed into405 GLOBAL reads and278038 GLOBAL writes. Its three kernel DRAM-read intervals are0,5,400. sgemm remains exactly zero-response despite140804/140528 DRAM reads and9287/2128 retries. Nonzero traffic or retry counts alone do not prove FR-FCFS/shared-credit limits are on the performance-critical path. No queue occupancy-time or exact end-to-end critical-path latency was established here.

The changed parameter is the FR-FCFS window with coupled memory-partition shared-credit limit; it is not an isolated pure scheduler-capacity intervention. Fixed Core l2cache.cc:133-149 computes shared-credit limit from the FR-FCFS queue and other queue terms. Clocks remain1410/1410/1410/850MHz and L2 remains S:128:128:16,L:B:m:L:L,A:192:4,32:0,32. CH and DH retain distinct L1 structures, active PIB domains and hardware cost; these are not equal-area claims.

## MRI-Q: small response is localized, not a miss-volume reduction

The four actual launches are PhiMag then three ComputeQ_GPU launches. CH per-kernel cycles are[5719,119403,118370,118752] at all profiles. DH changes from[5694,119028,117726,117726] to[5694,118707,117730,117724]: K2 -321, K3 +4, K4 -2, total -319. The small K3 regression is retained. All8192 DRAM reads and all L2 reservation failures occur in the K2 print interval; K1/K3/K4 DRAM-read differences are zero. This is a read-active interval, not a proven cold/compulsory-miss classification or a request-origin attribution.

CH selected counters are unchanged. DH accepted reads, read misses, DRAM atoms, OO lower-created/new-misses5312, valid hits10240, pending hits0 and tag evictions0 are unchanged. DH service samples23051136 ->23030720, PIB integral3095169 ->3097212, fully-ready-to-complete sum43594 ->45940, WB-wait1738 ->1666 correlate with the changed execution, but do not establish the causal bottleneck. They retain their separate event/integral units and are not converted to an unvalidated mean/critical-path time.

The positive-only MISS_QUEUE_FULL cumulative reason is visible3132(CH)/1937(DH); its K2 interval remains null because the earlier print omitted the zero-valued reason. The aggregate L2-reservation-fail counter has explicit endpoints and a valid K2 difference. Missing positive-only endpoints are never filled as zero. Raw avg_mrq_latency tokens at K2 are CH44, DH62 ->63, with corresponding sampled diagnostics retained. These rounded/sampling-window means cannot demonstrate a whole-application mean or absence of a tail. sgemm has no printed latency tokens despite DRAM reads, which means missing, not zero.

Candidate source computeQ.cu:38-46 describes PhiMag, :48-97 Q accumulation, :111-135 CPU/symbol-copy-separated K tiles. Constant broadcast and register accumulation are source-proven opportunities; ordinary-global/cache-hit or actual MSHR-merge outcomes require runtime evidence. Exact numK and capture executable identity remain unbound.

## Other kernel-level controls

transpose has eight actual symbol groups, each with three launches: copy, shared copy, naive transpose, coalesced transpose, padded transpose, coarse-grained, fine-grained and diagonal. All24 kernel cycles and selected additive intervals remain identical across F profiles within each design. Candidate transpose.cu:197-409,614-671 explains the eight implementations and warmup/timing sequence; fine/coarse are partial transformations and must not be described as equivalent full transposes. Observed DRAM zero bounds the registered replay's DRAM-window exposure; it does not establish compute-bound behavior or generalize to a real GPU.

sad has three dependent actual kernels: elementary4x4 SAD, larger8-shaped aggregation and larger16-shaped aggregation. Candidate sad4.cu:62-218/largerBlocks.cu and main.cu:263-352 distinguish texture reference samples, shared storage and packed global outputs. Trace memory instruction paths and widths are retained, but texture behavior is not invented as ordinary-global traffic. All three kernel cycles and selected additive intervals are invariant under F.

sgemm is the Parboil register-tiled implementation, not PolyBench GEMM. Its one actual kernel has1658916864 active-thread instructions and528 CTAs. Candidate sgemm_kernel.cu:46-99 stages B in shared memory, keeps16 accumulators per thread and synchronizes per K tile. These facts suggest overlap/reuse hypotheses; they do not explain the zero F response by themselves. Read traffic and retries are nonzero; no compute-bound label or queue-pressure claim follows.

particlefilter_float has36 actual launches with four symbols each appearing9 times. Source's likelihood ->sum ->normalize ->find sequence is consistent, but accepted frame IDs/full application completeness are not newly certified. Despite its name, candidate state arithmetic is double; actual trace contains64-bit global operations, double arithmetic and local stores. Candidate correctness risks at cross-CTA normalization/CDF dependencies are preserved as source-audit risks, not changed accepted status.

At P0, phase-cycle sums CH/DH are likelihood789546/1163937, sum50679/50209, normalize476916/445776, find543985/440952. Thus likelihood contributes+374391 DH cycles, offset by-134643 across the other phases, yielding+239748 overall. The likelihood phase also has greater GLOBAL accepted reads95128 ->1069592 and DRAM reads14 ->182, an association rather than proven causal attribution. Across all36 kernels DRAM reads occur only in the first four print intervals (CH14,4,4,2; DH182,4,255,2); the remaining32 intervals issue no additional DRAM reads. All F profiles preserve this pattern, and zero L2 retries/admission stalls do not prove absence of other latency or concurrency constraints.

## Initial state, scope and reproducibility

All30 sources show perf_sim_memcpy=1 and flush_L2=0; actual declared commands exactly match canonical input bindings. Declared HtoD copies directly force L2 tag filling through fixed Core gpu-sim.cc:2670-2691 ->l2cache.cc:109-120 ->gpu-cache.h:1413-1421. This changes modeled initial cache state without timed DRAM commands. It does not certify which subsequent accesses hit or the state of a captured real GPU. Complete commands, byte counts and source-file hashes are in MEMCPY_AND_INITIAL_STATE.json and CONSUMED_MEMCPY_SOURCE_EVIDENCE.json.

The fixed Atlas47a097aa reports and candidate implementation byte copies are included with path/commit/SHA. CUDA transpose uses candidate b059fdae25c2aabf737486aada743fca114469ce; Parboil/particlefilter use candidate dad09cb0487845edc7524ded814c6cde9f0ef6a1. Exact source bytes match Atlas inventories. Candidate correspondence does not bind historical compiler, macro overrides or capture ELF. Registered input SHA binds the trace; it is not a new original dataset-content/capture-completeness/numerical correctness certificate. MRI-Q's historical prior asset/status context remains unchanged. No R2/EP/IR/PQPS performance is substituted.

CLOSED_SOURCE_KERNEL_COUNTERS.json.gz contains all30 RESULT/exit/raw/input/build hashes and all408 kernel print records. ORDERED_KERNEL_SHAPES_AND_CYCLES.json.gz links exact trace member SHAs, CTA/instruction scope and six-cell cycles. PRINT_BOUNDARY_COUNTER_ROWS.jsonl.gz is independently streamable. CANDIDATE_SYMBOL_PHASE_SUMMARIES.json sums only explicitly listed additive kernel intervals; cumulative snapshots are never summed, missing endpoints yield null, and means/gauges/peaks are excluded. CH/common PAPER_BASE PIB256 and DH/OO PIB128 are typed separately; generic DH8 is inactive.

103 raw/source/contract checks and143 derived checks pass. No model, controller, daemon, native scientific state, historical result, frozen package, budget or v0.23 manuscript was changed. Publish only this package's MANIFEST members. No new experiment is proposed or authorized by this supplement.
