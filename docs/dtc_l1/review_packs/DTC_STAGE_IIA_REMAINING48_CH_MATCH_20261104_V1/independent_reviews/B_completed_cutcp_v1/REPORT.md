# cutcp: completed matched six-source control

Source-qualified snapshot observed2026-11-04 03:45:27UTC (11:45:27CST), manifest2502253f489c6b452cf0eaf7766b66f0fa004a8949a38fe6ffe5d62f2b271679, contains40 accepted newCH points and8 awaiting results. This supplement reads only cutcp's six accepted closed sources. No live raw was consumed and final24's all48terminal gate is unchanged. No population/CORE32 GM is inferred.

## Result facts

Fixed input af7320f9d9dc662971b1856cac87f29f9b8e4b2a65a7f9d4223bb7a74803fef8 has11 actual launches per source. CH P0/F128/F256 cycles are4502965/4502965/4502965; DH4490473/4490473/4490473. S_CH=S_DH=I=1, R=CH/DH=1.002781889569317 at bothF profiles. Each of the11 kernel cycles and every selected additive print interval is exactly unchanged within each design. DH is12492 cycles lower thanCH, but this absolute difference is not a benefit caused byF. There is no program or individual-kernel F regression in this input; none was deleted.

| Design | Accepted GLOBAL L2 sectors | GLOBAL read-miss sectors | All-type L2 misses | DRAM read/write atoms | Controller n_req | L2 retries | ICNT admission blocks |
|---|---:|---:|---:|---|---:|---:|---:|
|CH|1722160|0|85184|0/0|0|0|0|
|DH|1605996|0|85184|0/0|0|0|0|

The table applies to all three profiles within each design. L2 sectors and DRAM atoms are32B units; n_req is a separate request-object count. All85184 L2 misses are GLOBAL writes, which under fixed write-back/lazy-fetch-on-read can allocate modified sectors without an immediate DRAM read. No DRAM read, write or request is issued in any kernel print interval or final controller total. The registered replay therefore did not exercise a timed DRAM window. This does not prove compute-bound behavior, absence of L1/ICNT/completion cost, or the behavior of a different real-GPU initial state.

CH common Tag-bank conflict counter939686 and common PIB-full counter0 are unchanged acrossF. DH active OO lower-created/new-misses401499, valid hits88730, pending hits401541 and Tag evictions368731 are likewise invariant. Completion-service integral/events are preserved separately in TYPED_FRONTEND_SERVICE.json. CH common PAPER_BASE PIB256 and DH OO PIB128 are distinct domains; generic DH front-end8 is inactive. A field missing in one domain is not copied from the other or filled with zero. Positive-only failure-reason dictionaries are empty; no per-reason measurement is invented from that omission.

## Kernel and source boundary

All11 actual symbols are cuda_cutoff_potential_lattice6overlap, but active-thread instruction counts vary from430328696 to964225152. They are not eleven identical-cost kernels. Exact ordinal/memberSHA/CTA/instruction and six-cycle rows are in ORDERED_KERNEL_SHAPES_AND_CYCLES.json.gz. A's fixed144f selector covers all11 ordinals once; every matching trace symbol/instruction/memberSHA was independently checked across the six sources. No ordinal is promoted to a recovered scalar z-plane value.

Fixed candidate accel-sim/gpu-app-collection dad09cb0487845edc7524ded814c6cde9f0ef6a1, cutoff6overlap.cu:135-277 describes shared atom-bin loads, input-dependent cutoff/zero-charge tests and four lattice values per thread; :554-666 describes plane launches and CPU/GPU combination. Adjacent regions/planes offer source-level reuse opportunities, while barriers couple CTA progress. Static reuse is not a measured cache-hit or MSHR-merge count.

The whole native program also includes CPU atom binning, overflow-atom contributions, output transposition/addition and exclusion removal. GPU replay timing does not measure all that CPU+GPU work. Candidate source bytes match fixed Atlas47a inventories and are included, but historical capture ELF/compiler/macros, original dataset content/numeric correctness and native full-application completion remain unbound. Current accepted replay identity is preserved without promoting those properties.

## Initial state, units and bank diagnostics

All six actual command lists match the input contract: HtoD628864B,4B and4020B, total632888B. perf_sim_memcpy=1 and flush_L2=0 force L2 tag fill without timed DRAM commands through fixed Core gpu-sim.cc:2670-2691/l2cache.cc:109-120/gpu-cache.h:1413-1421. These source semantics explain how initial cache state can be populated in this model; they do not alone prove subsequent address-level residency or captured real-GPU state.

Core9eed/Framework02775/binary02a28936,1410/1410/1410/850MHz and10MiB L2 are fixed. F64/128/256 changes FR-FCFS queue and the coupled memory-partition shared-credit limit (l2cache.cc:133-149); a pure isolated scheduler-size claim would be inaccurate. L1/capacity/Tag/queues/timing/hardware cost differences remain distinct from this within-design parameter test.

Final20-controller/16-bank views are retained as diagnostics. All explicit READ-atom bank sums are zero and reconcile with strict controller read totals. Fixed dram.cc:555-628 increments printed bk.n_access only on READ-column commands, excluding WRITE/WB. Here controller write totals are independently zero too. A null controller READ-volume CV is correct because mean READ volume is zero; it is not fabricated as0CV or evidence of perfectly balanced useful traffic. Zero printed bank READ counts alone never establish bank inactivity in general. Mean, gauge and running-peak snapshots are never differenced/summed, and missing latency tokens are not zero.

Cumulative counter snapshots are differenced only with explicit endpoints and nondecrease; phase sums include all selected valid intervals or report null with missing counts. Print intervals do not establish request origin. No cold/compulsory-miss or causal bottleneck label is assigned.

## Reproduction and checks

CLOSED_SOURCE_KERNEL_COUNTERS.json.gz contains all6 RESULT/exit/raw/input/build sourceSHAs and66 kernel records. PRINT_BOUNDARY_COUNTER_ROWS.jsonl.gz is streamable. EXACT_PHASE_MAPPING_AND_COUNTERS.json and PHASE_COMPARISONS.json preserve A144f mappings and cumulative endpoint differences. FINAL_CONTROLLER_READ_QUEUE_DIAGNOSTICS.json.gz keeps typed final-only snapshots. Fixed Atlas report, candidate byte inventory and source-definition excerpts are included.

23 raw/source checks +31 derived checks +229 phase/bank checks =283 passing CPU/read-only checks. No model, GPU, trace, daemon, controller, source, budget, historical result, frozen package or v0.23 manuscript was changed. After this supplement, remaining3MM/GESUMMV/myocyte/srad execution stays under the existing owner; this package adds no experimental authority.
