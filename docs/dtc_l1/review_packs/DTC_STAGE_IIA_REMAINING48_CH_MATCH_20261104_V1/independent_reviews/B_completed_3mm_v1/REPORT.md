# 3MM: current-contract six-source FR control

Only six accepted sources for frozen input977a2f7007cb1f9673fe3a5c17cdbb469335c619c172a0a882eb18410049eb3d are consumed. The qualified snapshot manifeste4da3be193acad427ae0141bbfce6a4fac4af4691103dc2aaba8c051ac57b539 has45 accepted/3 awaiting results; this is not a final CORE32 conclusion. No live source, historical Hash comparison, EP/R2/IR/PQPS result or different experimental contract is substituted.

## Matched facts

CH P0/F128/F256=4191465/4191465/4191465cycles; DH=2402871/2402871/2402871. S_CH=S_DH=I=1; R=CH/DH=1.7443570628635494 for bothF. All three actual kernels are individually identical acrossF within each design, as is every selected additive print interval. The1788594-cycle CH/DH gap is an absolute difference under the existing architectures and common Hash configuration, not a measured FR gain or a newly isolated Hash gain. No program/phase negative F response is present; none is omitted.

| Design | GLOBAL accepted L2 sectors | L2 total accesses | L2 read/all-type misses | DRAM read/write/n_req | L2 retries | ICNT admission blocked events |
|---|---:|---:|---|---|---:|---:|
|CH|14962192|65293840|0/0|0/0/0|0|0|
|DH|5186824|55518472|0/0|0/0/0|0|3265907|

All three profiles retain these totals within each design. L2 GLOBAL accepted reads are32B sectors, whereas all-access counts include other types and must not be interchanged. DH has fewer accepted GLOBAL sectors, but that alone does not identify which mechanism produces the cycle difference. CH common Tag-bank conflicts75571200 and common PIB-full0 cannot be copied into an OO domain or compared as equal-structure pressure. DH OO lower-created/new-misses1296706, valid hits12352287, pending hits11541407 and Tag evictions1263938 remain invariant underF. These actual typed events are retained with finite-service integrals/events; static address reuse is not treated as a measured hit or merge.

No DRAM data command or request is issued in any kernel interval or final20-controller total. Thus the registered initial-state/replay condition does not exercise the timed DRAM scheduler window. It does not establish compute-bound behavior or rule out other memory-system limitations. Nonzero DH gpu_stall_dramfull illustrates its source meaning: blocked ICNT-to-subpartition admission events, not DRAM wait cycles. It is never divided by GPU cycles as a critical-path percentage.

## Three actual kernels and scope

A fixed144f mapping identifies the ordered3 trace kernels as candidate E=A*B,F=C*D,G=E*F phases. Exact fullinput/trace-memberSHA/symbol/instructions were checked across all6 sources, and phase cycles reconcile with strict totals. Source S's first two kernels are mathematically independent but serialized by the host; the third depends on their results. Kernels use row-major scalar-loop matrix accesses, without shared tiling/barriers/atomics in the recovered source. These are source facts, not proof of scheduling or performance cause.

Candidate accel-sim/gpu-app-collection dad09cb0487845edc7524ded814c6cde9f0ef6a1,3mm.cu:109-154,215-254 is byte-pinned here. Source S copies uninitialized E/F/G then uses +=, unlike a corrected alternative. This candidate initialization risk cannot be promoted into a claim about historical captured values or silently repaired. Capture-source/ELF/macros and native numeric correctness remain unbound. A phase label E=A*B is nominal source correspondence, not new numerical certification.

The actual registered command lists contain seven1048576B HtoD copies (7340032B), with perf_sim_memcpy=1 and flush_L2=0. Fixed Core forced-tag-fill semantics populate modeled L2 state without timing these copies as DRAM requests. This helps bound interpretation of zero DRAM exposure; it does not certify which subsequent address hits or the initial state of a real GPU.

Core9eed/Framework02775/binary02a28936,1410/1410/1410/850MHz and10MiB L2 remain fixed. P0/F128/F256 correspond to FR-FCFS windows64/128/256 with coupled memory-partition shared credits. CH PAPER_BASE commonPIB256 and DH PAPER_OO128 retain different L1 mechanisms/resources; no equal-area/Tag/queue/timing claim follows. Generic DH front-end8 is inactive.

## Counter and evidence boundaries

All additive phases use explicit consecutive cumulative endpoints; missing positive-only reason endpoints stay null. Means, gauges and running peaks are never differenced or summed. Printed bank n_access is READ-column atoms only in Core dram.cc:555-628, excluding WRITE/WB; all explicit sums reconcile to zero reads, while null zero-population controllerCV is preserved. Neither missing latency tokens nor a zero bank READ field is treated as a general no-contention proof.

CLOSED_SOURCE_KERNEL_COUNTERS.json.gz contains six RESULT/exit/raw/input/build identities and18 kernel records. ORDERED_KERNEL_SHAPES_AND_CYCLES.json.gz supplies exact trace scope; PRINT_BOUNDARY_COUNTER_ROWS.jsonl.gz is streamable. EXACT_PHASE_MAPPING_AND_COUNTERS/PHASE_COMPARISONS preserve source-phase bounds. All original reference roles remain unchanged alongside the two new authorized CH roles.

23 raw/source +31 derived +175 phase/bank checks=229PASS. No live raw, model, GPU, trace, service, controller, scientific state, budget, frozen file, final24 gate or manuscript was changed. Root alone publishes this independent supplement.
