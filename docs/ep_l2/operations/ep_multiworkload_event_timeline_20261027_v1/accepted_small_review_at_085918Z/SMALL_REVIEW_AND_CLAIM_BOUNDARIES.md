# Seven accepted endpoint review

Scope:7accepted endpoints/6distinct programs, including the Vector OFF/ON pair. Only Main-indexed METRICS, MEMORY_PATH_COUNTERS, accepted point/DONE/limits receipts and stored ET decoder results were read; no fullraw or tracebody was parsed. The7 current registry accepted-point SHA joins are preserved. DWT is excluded: its preserved protocol point was invalidated after the96MiB result-cap violation. This metadata engineering review neither clears that violation nor grants run/archive authority.

All seven have actual naturalDONE rc0/no stop reason and C3 hardware drain true. Original application capture completeness and numerical SASS output remain UNKNOWN. S results have T/RO NOT_APPLICABLE, not measured detach zero. Only the exact certified VectorF domain measures T under this source/input.

|Endpoint|Core cycles|Peak RSS GiB(sampled tree)|Host seconds|Event/tick peak|Preview RF / actualft TagFAIL|T|
|---|---:|---:|---:|---|---|---|
|VECTOR_F_ET0|77237|0.523438|559.641|7/6|0/0|certifiedF|
|VECTOR_F_ET1|77237|0.531250|565.747|7/6|0/0|certifiedF|
|CONV_S_ET1|331234|0.957031|2421.045|8/8|42717/0|N_A|
|CFD_S_ET1|84851|1.023438|340.622|8/8|11/0|N_A|
|GAUSSIAN_S_ET1|33800|0.363281|33.838|0/0|0/0|N_A|
|SGEMM_S_ET1|353921|7.855469|1675.377|5/5|0/0|N_A|
|GESUMMV_S_ET1|3299323|1.953125|6437.277|4/4|0/0|N_A|

SGEMM: captured actualmodel AS soft=hard9GiB(9,663,676,416B); sampled process-tree peak8,434,745,344B=7.85546875GiB; rc0, stopNONE, full1,658,916,864instructions/528CTA/onekernel and C3drain pass. No incomplete, cap-abort or truncation evidence is present. Postexit currentRSS0 must not replace the recorded peak. RSS samples are not a continuous exactpeak or the same quantity as virtual AS; this one completion doesnot prove every workload fits9GiB.

Conv previewRF42717 and CFD11 coexist with actualft TagFAIL0; uniqueNEW at R8 is289/1. Preserve those exact populations. In both S cases, R4pressure route labels report prod_probe_reached for the previewpressure population, while actual raw_tag_fail_commit iszero; those field names must not be substituted for oneanother. No marginal multiplication or eligibility/benefit claim is made. GES peak4 doesnotmean a NEW arrived at R4: its uniqueNEW is confined to R0/1/2.

Queue denominators: B0/M0 occupancies use their own64slice sampler counts; DRAM queue/full samples use32channel DRAM ticks. Current clocks are1132core/L2 vs850DRAM. For SGEMM these are22,650,944 slice samples and8,504,096 channel DRAM ticks; DRAM scheduler-full197/8,504,096, returnq-full0. For GES they are211,156,672 slice samples and79,277,024 channel DRAM ticks; scheduler/returnq-full0. Mean occupancy printed as integer floors is retained as weighted lower-inclusive/upper-exclusive bounds. Perentity peaks usemax, not sums as simultaneous GPU occupancy. Repeated head/denial counts are not exclusive GPUstallcycles. Lowerpop payload bytes split by requiresreturn/noreturn are not physicalDRAM RD/WR command bytes or bus utilization; those actual columns remain separately sourced from C3.

SGEMM L1 missq-full342482 access failures and GES L1 line-allocation-fail26968411/missq-full65828 are observed upstream attempt counts, not causal cycle shares. Static GES one-kernel16CTA and ATAX two kernels each16CTA imply each individual kernel can occupy at most16 of configured80SM simultaneously; this is a PROVEN grid upper bound, not a measured causal bottleneck or new ATAX result.

Gaussian:11454instructions/6CTA/6kernels, each1CTA; LIFE peaks0/uniqueNEW0 doesnotmean no memory access. Its actual L1 is50accesses/21misses/15pendinghits; L2 is31accesses/0misses,17globalread HIT+14globalwrite HIT; ICNT is31request/31reply packets. Effective perf_sim_memcpy=1, perfect_mem=0, gmem_skip_L1D=0; declared prefix hasHtoD64+64+16B. Source labels this option Fill the L2 cache on memcpy(gpu-sim.cc:238,2436). Results are compatible with that initialized small L2 working set, but no prefillOFF counterfactual was run and neither highL1hitrate nor causal prefilling is inferred fromR0.

ET table: all six ETON fixed-object+declared-aux values are3,868,584B. Compressed payload and complete applicationwire bytes are distinct16MiB limits, each from stored decoder/wire closure. Across these six points compressed bytes range0..139594 and wire1195..210368. GES/Gaussian havezero selected events but valid nonempty META/END wire; selected windows are not a globalpacket population bound. The offlineviewer engineering16MiB output-size cap is a separate expanded JSON/CSV/HTML/VCD artifact budget, not the application compressedpayload or base64wire cap. The broad newobserver memory/RSS limitations and extraELF readonlydata already reported remain unchanged.

Files: ACCEPTED_ENDPOINTS_SMALL_REVIEW.csv; QUEUE_DENOMINATORS_AND_BOUNDS.csv; ETON_STATE_AND_WIRE_BYTES.csv; REVIEW_EVIDENCE.json; GAUSSIAN_AND_STATIC_GRID_CLARIFICATIONS.json. DWT/FWT/BICG and unstarted ATAX are not added to this accepted performance table. No new scientific starts, acceptance or asset writes were performed.
