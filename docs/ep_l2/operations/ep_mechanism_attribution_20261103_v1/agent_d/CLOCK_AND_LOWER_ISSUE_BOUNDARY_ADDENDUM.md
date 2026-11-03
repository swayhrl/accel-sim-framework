# Clock and Lower-Issue Measurement Boundary Addendum

**PROVEN source-semantic clarification; no newly demonstrated producer bug.** This addendum narrows timing/unit labels in prior reports without changing any accepted counter, cycle, identity, arithmetic or negative result. It supersedes uses of `DRAM completed read/write bytes` or physical `bandwidth utilization` when those labels refer specifically to C7E/EPL2DRAMV1 successful-byte counters. No raw/Trace, model, fixture, Source or scientific-accounting change was made.

## Actual event boundary

Core1e07 `l2cache.cc:748-749` enters memory_partition_unit::dram_cycle and samples a DRAM-domain cycle. In its subpartition arbitration loop, each considered nonempty L2-to-DRAM FIFO head calls l2_char_record_dram_issue at793-807. These are **head arbitration/probe opportunity events on DRAM callbacks**, potentially repeated for the same waiting head and potentially considering more than one subpartition before one succeeds. They are not global GPU cycles, unique requests, DRAM commands completed or bus cycles occupied by this request.

At814-815 the current head must pass credit/return rules and the scheduler-full probe. At821 the L2-to-DRAM FIFO is popped. At822-825 its successful issue counter and mf->get_data_size() payload bytes are charged. The fixed-delay record is then created at829-833. This is the exact `successful_*` boundary: **successful lower admission into the pre-MC fixed-delay queue**, not DRAM scheduling completion, bank service completion, return completion or a successful MC push.

At831-832 ready_cycle is physical GPU/core stamp gpu_sim_cycle+gpu_tot_sim_cycle plus dram_latency. Thus the configured fixed-delay deadline is expressed in GPU-cycle stamps even though the queue is processed from the DRAM-domain callback. At845-854 the mature front can enter m_dram->push only if the scheduler is not full then. Deadline waiting plus subsequent scheduler blocking and DRAM-callback discretization can extend actual residency; the configuration value is not a measurement of actual queue residence. The later FR-FCFS/bank/return service is a separate stage.

The relevant non-simple path functions are byte-identical between accepted Source78 and new Core1e07: dram_cycle, requires_dram_to_l2_return/can_issue_to_dram and the success-recording routine. This clarification therefore also applies to the Source78 W/S/WV metrics read by this study. The Source1e07 exact config has simple_dram_model=0, clocks1132:1132:1132:850 and dram_latency100.

## Producer classes are return-required versus no-return writeback

`requires_dram_to_l2_return`, lines605-608, is exactly `access_type != L1_WRBK_ACC && access_type != L2_WRBK_ACC`. The caller supplies this as is_read and its negation as is_wb. It does not test mf->is_write() to classify the successful-byte bucket. Therefore the source-grounded field descriptions are:

| Preserved raw field name | Precise producer unit and class |
|---|---|
| c7e_dram_issue_attempt | considered nonempty lower-FIFO head on DRAM arbitration opportunity |
| c7e_dram_scheduler_full_observed | such head probes observing scheduler full, including probes with other blockers |
| c7e_dram_scheduler_causal_block | such probes with scheduler full and neither measured return nor credit block; locally filtered event, not exclusive global stall time |
| c7e_dram_successful_read_issues / successful_read_issues | successfully admitted return-requiring lower requests |
| c7e_dram_successful_read_bytes / successful_read_bytes | admitted mf payload bytes for return-requiring requests |
| c7e_dram_successful_write_issues / successful_write_issues | successfully admitted no-return L1/L2 writeback requests |
| c7e_dram_successful_write_bytes / successful_write_bytes | admitted mf payload bytes for no-return L1/L2 writebacks |

Actual MC scheduler-full checking still uses mf->is_write at804/815/849; this is a distinct predicate from the measurement class. In a general write-through/no-write-allocate configuration, a non-writeback write can require a return and therefore appear under the raw field named read. Do not generalize that name into a pure load-versus-store census.

In these exact accepted cache configurations, B maps WRITE_BACK (gpu-cache.h:685-686) and L maps LAZY_FETCH_ON_READ (:775-776). Write hits mark modified locally (gpu-cache.cc:1916-1932); lazy-fetch write misses forward the demand write only under WRITE_THROUGH (:2221-2249), which is not enabled. This supports the usual reads-versus-WB interpretation for the ordinary configured path. Nevertheless the strict aggregate packet-class census is not a new measurement here. Use the explicit return-required/no-return-WB labels when reporting the producer counters, rather than silently claiming all possible request categories have been independently audited as pure reads/stores.

## Application and kernel interpretation

Complete hardware drain is strong population-level completion evidence: the requests already admitted by the measured application must make progress through the modeled path before final closure. It does **not** move the original accounting event to service completion, identify physical bus transfers, impose forced dirty-L2 flush, or assign a later transaction completion to its issuing kernel.

For the B0/M0 kernel_shared_delta tables, C7E bytes are assigned to the kernel **time interval in which lower queue admission occurred**. Work may originate before an interval boundary, or finish service after it. The per-kernel Columns read/write differences must be described as differences in admitted lower payload demand, not DRAM completed bytes in Columns. The observed C-B Columns increase in admitted bytes still rules out describing this table as evidence of a lower admitted-traffic reduction; it does not quantify MC service or end-to-end bandwidth bottleneck.

The equality of64-slice B0 successful-byte totals with32-channel EPL2DRAMV1 totals is expected from l2cache.cc:822-825, where both are charged at the same event. It is useful accounting conservation but not two independent measurements of request completion.

EPL2DRAMV1's printed bandwidth_util numerator is precisely the sum of these admitted bytes, and the denominator is dram_cycles*dram_atom_size (l2cache.cc:900-920). Label the result a **nominal admitted-payload load ratio over the declared DRAM-cycle budget**. It is not a direct data-bus utilization or completed-service bandwidth measurement. Request payload size can differ from physical burst/command traffic; a physical bandwidth claim requires actual DRAM service/bus counters with their matching denominator. Do not add the ratio to Bank/queue stalls or use it as an exclusive bottleneck share.

## Disposition

Main should relabel current and new result tables while preserving original raw field names, exact data and earlier report history. For older retained prose, cite this superseding interpretation. All controlled cycle contrasts, actual detach PHASE proofs, identity checks, NI scope and counter arithmetic remain unchanged. No positive/negative performance result is withdrawn and no new simulator correctness defect is established by this naming issue. Actual fixed-queue residency, completion timing by kernel and physical memory-bus utilization remain UNKNOWN where not separately instrumented. No new collection or simulation is authorized or needed to correct these labels.
