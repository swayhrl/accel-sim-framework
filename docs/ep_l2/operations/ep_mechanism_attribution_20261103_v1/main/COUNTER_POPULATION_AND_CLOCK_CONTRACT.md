# Counter population and clock contract

|Field/population|Actual event unit|Valid denominator/join|Invalid interpretation|
|---|---|---|---|
|TP raw-full with R8|Same request/set/stamp head observation, repeated across blocked ticks|Own arm/phase joint head population|Independent ingress NEW or marginal R8 times marginal RO|
|Operational pressure_eligible|T-gated pre-preview structural predicate; A passive TP remains separately measured|Own raw-full head population|724/13012 shared-UID survival probability|
|eligible_capacity_consulted|RO descriptor/address/LineMSHR predicate evaluation|Same RO preview/capacity population|General metadata/set query or all requester classes|
|ordinary consulted/CONSULTED_MISS|Mature paid relief preview route and allow decision|Same joint requester/phase/route|Direct backend class or later UID completion|
|Backend PHASE counters|Actual commit/retire events during active kernel interval|PHASE->SLICE->GLOBAL under same catalog|Old transaction owner-kernel or unrecorded requester class|
|P1 issued/paid_wait_gpu_cycles|Per-slice query issues and physical-GPU-cycle exposure, shared port1/slice/cycle|Same query population; per-kernel split absent|Subtract2954fromGPU total or declare PPA closure|
|RO admit/merge/response/retire|Distinct transaction, waiter and response populations|Verified admit=retire and admit+merge=response|Per-trigger UID chain or direct boundary census|
|First-block wait|Per-reason resolved requests and accumulated waits; reasons overlap|Own resolved_first_waits|Exclusive disjoint GPU stall budget|
|B0 bank/full/occupancy|Own callback/service/sample/hist population|Same interval/sample; maxima not sums|Sum maxima or treat peak as saturation duration|
|C7E issue attempt/full|FIFO-head probes during DRAM arbitration; multiple candidates can be probed per tick|Own issue_attempt population|GPUcycles, channel-cycle count or unique requests|
|C7E successful bytes/issues|Successful FIFO dequeue into pre-MC fixed-delay queue|Return-required or no-return-WB class, same interval|Physical DRAM commands, pure demand reads or completion bytes|
|B0/M0 kernel_shared_delta|Explicit interval baseline differences, maxima from delta histograms|Own64slice/kernel interval; selected counters sum to application|Origin-kernel attribution for all inflight work|
|V read/dirtyforward response|Service responses/sectors, not lower requests|Own service population|Vresponses equal avoidedDRAMrequests|
|Retention clean/extra/total|State area in slots times producer ticks; extra includes in-flight/completed WB|clean+extra=total|extra=total footprint or totalarea=marginalreclaimvalue|
|EPL2DRAMV1 bandwidth_util|Nominal admitted-payload load ratio|Declared admitted bytes and nominal capacity/time denominator|Direct physical DRAM bus utilization|

Actual clock option:1132.0:1132.0:1132.0:850.0. Equal current Core/ICNT/L2 rates do not make different event populations interchangeable. Diagnostic/query stamps use gpu_sim_cycle+gpu_tot_sim_cycle. Fixed dram_latency100 is added to that physicalGPUstamp inside dram_cycle, whose execution opportunities occur on DRAMticks; deadline is not measured queue residence or pure DRAM latency.

Production l2cache.cc:748-854 and1797-1818 locate head probes, fixed-delay admission and MCpush. The successful-byte flag named read is requires_dram_to_l2_return; no-return L1/L2 WRBK is the other class, not general mf->is_write. Current write-back/lazy-fetch behavior does not justify relabeling arbitrary configs. Hardware drain does not force dirty resident flush. Credit/scheduler/return/lower waits are not an additive critical-path decomposition. Per-kernel and PHASE are active time intervals, not automatically source ownership.

Source anchors and independently verified identical relevant code in Source78/1e07 are recorded in agent_d/CLOCK_AND_LOWER_ISSUE_BOUNDARY_ADDENDUM. Missing strict unique NEW, first-head UID cohort, backend requester class, per-trigger later completion and per-kernel P1 cost remain NOT_INSTRUMENTED/UNKNOWN. Never fill them with zero.
