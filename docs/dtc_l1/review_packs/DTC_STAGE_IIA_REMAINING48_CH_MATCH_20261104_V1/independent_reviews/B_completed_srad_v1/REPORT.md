# srad_v1:502-kernel matched six-source FR control

Qualified snapshotd6ebc31c6dc1a23484e57c775bc1f373cd3330e6ec3d78a29c4e5386390b5a8d observed2026-11-04 07:00:01UTC has46 accepted and2 awaiting results/common31. Only the six strictly accepted srad_v1 sources for frozen input0e62c67daa020853cf8a90b9f20a42d7e960e4d6c6e1db09173de1a58af199c4 are consumed. No live source or unarchived postprocessing output was read; final24/waiter/pins remain unchanged. This is not a final CORE32GM.

## Exact parameter response

CH P0/F128/F256 cycles=8043823/8043823/8043823; DH=7324411/7324411/7324411. S_CH=S_DH=I=1, R=CH/DH=1.0982211402391264. All502 kernel cycles and every selected additive print interval are exactly unchanged acrossF within each design. Thus there is no per-kernel or whole-replay F regression or benefit to discard. The719412-cycle absolute DH advantage is a separate current-architecture result; no FR causality, isolated Hash benefit or equal-area claim is made.

## Seven candidate phases, with two different reduce launches

A's immutable144f mapping separates extract, prepare, first-level reduce, second-level reduce, coefficient stencil, image update and compress. All source symbols/instructions/memberSHAs match the frozen mapping at every source. The two reduce phases share the exact symbol _Z6reduceliiPfS_ but remain different ordinal selectors and execution shapes. Generic symbol-grouped diagnostics are not used to collapse them into one phase.

The actual first reduce has450 CTAs, ordinals3,8,...,498,100 launches. The second has1 CTA, ordinals4,9,...,499,100 launches. Explicit raw cumulative-CTA differences for all502 kernels at each of6 sources match the frozen trace-body CTA contract; the450/1 distinction is measured metadata, not inferred from performance. Candidate source parameters no229916/mul1 then no450/mul512 are source correspondence, not independently extracted scalar arguments.

| Candidate phase | Launch count | CH cycles | DH cycles | DH-CH cycles |
|---|---:|---:|---:|---:|
|extract|1|8199|8221|+22|
|prepare|100|849940|839422|-10518|
|reduce450CTA|100|1392821|1367368|-25453|
|reduce1CTA|100|1597231|1572518|-24713|
|coefficient stencil|100|2318654|2021637|-297017|
|image update|100|1869200|1507526|-361674|
|compress|1|7778|7719|-59|

These sums apply to all three profiles within each design. The coefficient/update phases account for most of the absolute gap, while extract is slightly slower inDH. No per-stage causality or critical-path decomposition is inferred from those sums alone. Source-level shared reductions, barriers and neighbor accesses suggest dependencies but do not establish measured stalls or hits.

The registered502-launch sequence is consistent with candidate1+100x5+1; registered trace completeness is not native full-application/numerical certification. Source's full-image statistical ROI for mean/variance is distinct from the trace-capture ROI and whole CPU+GPU application. CPU q0 calculation/statistic copies and output handling are outside a pure GPU-kernel cycle total. Original image content, actual capture executable/compiler/scalars and numeric correctness remain unresolved.

## Cumulative traffic and typed pressure

AllF profiles preserve the following counts within each design. L2 GLOBAL reads are32B sectors and DRAM data-command atoms are32B; controller n_req is a separate request-object count.

| Field | CH | DH |
|---|---:|---:|
|GLOBAL accepted L2 reads|39539252|38734616|
|GLOBAL L2 read misses|13|13|
|All-type L2 misses|201193|201193|
|DRAM read/write atoms|13/0|13/0|
|DRAM controller n_req|13|13|
|L2 retry events|93|91|
|ICNT admission block events|13016|3370711|

All201193 L2 misses decompose into13 GLOBAL reads and201180 GLOBAL writes. Under fixed write-back/lazy-fetch-on-read, counted write misses do not automatically issue DRAM reads. Actual DRAM reads occur only inK3=2,K5=6,K6=5 at every source; all later intervals add zero reads. These tiny initial read-active intervals do not demonstrate sustained DRAM-window pressure, cold/compulsory classification, request-origin attribution or compute-bound behavior.

The visible L2 failures are merge-limit retries93(CH)/91(DH), not MSHR-entry failures or occupancy time. Positive-only missing reasons remain missing; lower-level L2 counters must not be mixed with large L1-core reason counts. gpu_stall_dramfull measures ICNT-to-subpartition admission blocks, not DRAM waiting cycles: largeDH admission counts coexist with just13 DRAM-read atoms.

CH common Tag-bank conflict60122920/commonPIB-full0 are typed common events. DH active OO lower-created/new-misses9683654, valid hits8082153, pending hits5262263 and Tag evictions9650886 are separate OO events. DH service samples468762304, PIB integral9925472844, retire16584070, fully-ready-to-complete sum117166205 and WB-wait4563728 retain their original units. They are not converted into an unvalidated latency/occupancy or cross-design equal-mechanism conclusion. Active capacities remain CHcommon256/DHOO128; genericDHfront-end8 is inactive.

## Initial state, units and bank limitations

Exactly five actual initial HtoD commands are bound:2008,2008,1832,1832 and919664B, total927344B. These correspond to candidate clamped neighbor-index arrays and image upload, but neither original image bytes nor scalar values are newly recovered. perf_sim_memcpy=1/flush_L2=0 forces L2 tag fill without timed DRAM commands. Modeled initial state must therefore be disclosed; it does not prove all later accesses hit or that source reuse is numerically valid in a historical capture.

Core9eed/Framework02775/binary02a28936,1410/1410/1410/850MHz and10MiB L2 are fixed. P0/F128/F256 FR-FCFS windows64/128/256 also change memory-partition shared-credit limit. This is not an isolated queue-only change or a new architecture/budget authorization.

Final controller/bank diagnostics retain explicit cumulative READ-only scope. Core dram.cc:555-628 increments printed bk.n_access only on READ-column commands, including allocation reads, not WR/WB. Precisely6sourcesx20controllersx16banks are checked and reconcile to13 totalread atoms per source. Banks0..3 have the only nonzero printed READ counts; zeros for other banks do not prove generic inactivity. READ-volume controllerCV=1.901416476 is the same for all6sources but rests on only13 atoms, so it cannot explain throughput or temporal bank contention. Queue means/peaks and rounded latency tokens are diagnostics, never differenced/summed or promoted to exact phase request lifetimes.

Every additive phase total requires explicit cumulative endpoints and reconciles to strict whole-replay totals. Missing intervals produce null with counts. Means/gauges/running peaks are excluded from additive phase sums. Fixed Atlas47a candidate dad09c source bytes/paths/SHAs are included; source formulas and static reuse remain distinct from runtime counter facts and unconfirmed causes.

## Artifact scope and checks

CLOSED_SOURCE_KERNEL_COUNTERS.json.gz holds6 RESULT/exit/raw/input/build identities and3012 kernel records. ORDERED_KERNEL_SHAPES_AND_CYCLES.json.gz links502 exact ordinals to6cycles and trace-body scope. PRINT_BOUNDARY_COUNTER_ROWS.jsonl.gz is streamable. EXACT_PHASE_MAPPING_AND_COUNTERS/PHASE_COMPARISONS are the authoritative seven-phase summaries; REDUCE_PASS_SHAPE_VALIDATION.json explicitly preserves450-vs1 CTA. FINAL_CONTROLLER_READ_QUEUE_DIAGNOSTICS.json.gz retains final-only bank/queue diagnostics.

23 raw/source +31 derived +3672 phase/bank +8 reduce-shape checks =3734PASS. No live raw/model/GPU/trace/service/controller/source/budget/final-chain/manuscript operation occurred. Publish only MANIFEST-listed members, each below8MiB. Original reference and newCH source identities remain separate; no historical EP/R2/IR/PQPS performance is substituted.
