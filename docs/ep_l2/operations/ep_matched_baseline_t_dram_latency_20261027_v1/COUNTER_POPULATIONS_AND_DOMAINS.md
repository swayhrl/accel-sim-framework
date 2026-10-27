# Counter populations and clock domains

Goal: EP_L2_MATCHED_BASELINE_T_AND_DRAM_LATENCY_CAUSAL_V1.
Read-only source basis: Core c67b332db703f09571ba6628222c77d71440e141 at /root/data/ep_tag_capacity_scaling_20261027_v1/core. All line references are relative to that exact source root. No model was run and no production/frozen source, parser, raw or main document was changed for this note.

**Rule for joint attribution:** add only disjoint owners from the same population, clock and scope. A sum of slice observations is not GPU stall time; an event-peak sum is not simultaneous occupancy; a marginal sum is not a joint. Match actual final native-clock populations before comparing cases.

## 1. RO state exposure: complete RO-transaction population

Source: ep-l2-reservation-lifetime.h207-239,300-309,328,333-349; ep-l2-ro-transactions.h363-367,387-395.

The observer key is the existing physical payload slot plus generation. It follows the real RO transaction through updates and actual retirement, including detached transactions, rather than selecting only long-lived or particular-Tag-failure victims.

| Counter | Exact population/state | Clock and denominator | Valid aggregation |
|---|---|---|---|
| RO_TIME | At retirement, tick-birth for each RO transaction, h239. Sum over all retired RO transactions in the scope. | L2_tick. Divide by RO_RETIRE for mean completed transaction lifetime. | Sum over sets and slices gives transaction-L2-ticks. It is not requester latency or GPU cycles. |
| RO_LOWER_TIME | Each state interval contributes dt iff issued & ~ready is nonzero, h207-212. One pending transaction contributes1 regardless pending-sector count. | L2_tick state exposure of the complete observed RO population, not DRAM busy time. | Sum disjoint transactions/sets/slices. Divide by total slice observation ticks for a time-weighted **per-slice mean pending-RO concurrency**, subject to closed coverage below. |
| RO_RESPONSE_ONLY_TIME | Each live interval with !(required & ~ready) contributes dt, h211: all required data ready but transaction still live. | L2_tick state exposure, not ICNT-exclusive wait attribution. | Sum transaction exposure. It cannot be subtracted from RO_TIME to recover DRAM time. |
| RO_INITIAL_READY / RO_READY_ADD | Initial resident-ready sector bits versus newly ready bits after birth, h225-233. | Sector-bit counts, not time, packets or transactions. | Sum like-named sector events only. |
| RO right count/time | finish closes phases and records still-live transactions and observed elapsed lifetime, h328/347-349. | Right-censored transaction population/L2_tick overlap. | Do not silently combine with completed-lifetime means as full uncensored lifetimes. |

RO lower exposure begins when actual lower-queue acceptance sets issued bits: gpu-cache.cc1630-1635 -> ep-l2-ft-cache.inc629-635 -> ep-l2-ro-transactions.h236-253. It stops only after an actual accepted fill sets ready bits, h255-264. Therefore it spans lower FIFO waiting, fixed latency, DRAM and return/fill acceptance; it does not isolate those components.

RO_TIME, LOWER and RESPONSE_ONLY use the same full observed transaction population but different predicates. They are not a partition of one latency: a required sector can remain unissued, and requester multiplicity/merge differs from transaction population. They must not be relabeled as three disjoint GPU-stall components.

For a complete drained F/F-minus-T epoch, require all64 slices, matching META intervals, no invalid/overflow/output errors, RO_ADMIT=RO_RETIRE and no right-censored survivors. Define SUMLOWER := sum of emitted RO_LOWER_TIME over every set and slice; SUMLOWER is a reporting variable, not another source field. Then:

mean pending RO transactions per slice = SUMLOWER / sum_slice(META.end-META.begin).

This is only a first moment of concurrency. If all64 intervals share the same origin/end, dividing SUMLOWER by the single common duration instead yields time-mean whole-GPU transaction count, not a peak. Neither formula supplies a histogram, temporal alignment of different resource maxima, or independent-line count.

In formal S, T0/M0 means no RO runtime: RO mechanisms are NOT_APPLICABLE, rather than an effective zero-pressure RO experiment. Moreover c67 ro_end_epoch finishes LIFE only inside if(m_ro), ep-l2-ro-runtime.inc390-396. S complete emitted windows may be reviewed as observed windows; missing full LIFE terminal/tail remains NOT_INSTRUMENTED. No full-run RO/lifetime inference is made from that gap.

## 2. No emitted RO-lower concurrency histogram

Actual searches on exact c67:

- rg -n RO_LOWER_CONCURRENCY src/gpgpu-sim -> rc1, no matches.
- rg for lower.*hist / hist.*lower / concurrency.*hist / hist.*concurrency in the RO transaction/runtime and LIFE header -> rc1, no matches.

The closest actual output is **EPL2ROC1|LOWER_CONCURRENCY**, ep-l2-ro-runtime.inc443-447. It contains peak_lower_transactions, peak_independent_lower_lines and epoch/last-response CORE-cycle anchors; it is not a histogram.

Its source observer scans currently live slots satisfying issued & ~ready, counts transactions, sorts the existing line scratch to count distinct lines, then retains only maxima: ep-l2-ro-transactions.h323-335. It is called on real lower acceptance at253; fills/retirements cannot increase the pending-lower peak. This is an event-peak observer, not a per-tick occupancy distribution or response-requester histogram.

Consequently **RO_LOWER_CONCURRENCY histogram = NOT_INSTRUMENTED**. The emitted peaks plus SUMLOWER/total slice ticks do not determine histogram shape or quantiles. LIFE reserved-Tag area[17] is a different Tag population, not an equivalent RO-lower histogram. Do not invent bins from those marginals or sum independently timed slice peaks.

## 3. L2-tick samples, head exposures and lower drain

| Field/family | Exact c67 source | Population/clock/denominator | Addition limit |
|---|---|---|---|
| LIFE LOWER_QUEUE_BLOCK | l2cache.cc1303-1312 | Once per participating L2 cache_cycle when actual miss queue is nonempty **and** L2-to-DRAM FIFO is full. L2-tick demand+full exposure, even without a frontend head. | Sum over slices gives blocked lower-drain slice-ticks. Conditional failure fraction needs matching lower-drain-eligible observations; denominator is not R4 observed_heads. |
| LIFE L2_MISSQ_BLOCK | l2cache.cc1469-1476 | Actual frontend plan needs new_missq_entries and miss_queue_has_slots is false. Frontend decision exposure in L2 clock. | Not identical to occupancy being at capacity on every tick. |
| c7d_missq_full_block / c7d_l2_to_dram_full_block | l2cache.cc1497-1501 | Denied frontend plan needs missq capacity / will_send_lower_read sees lower FIFO full. | These are producer-head predicates, not the preceding queued lower-drain predicate. Same field words do not establish the same population. |
| B0 samples, missq_avg/max, lowerq_avg/max, descriptor etc. | l2cache.cc1757-1759,1885-1905,2182-2203 | Actual once-per-L2-tick sample, including ticks without a head. sample() increments samples; missq/lowerq sums and sampled maxima update there. Printed means divide by samples, e.g2224-2227. | Queue entries/slots per slice. Rounded integer means do not reconstruct exact sums; max across individual maxima is not simultaneous whole-GPU occupancy or intratick high-water. |
| R4 observed_heads/raw outcomes/eligible and R5 capture | gpu-cache.cc3071-3086; ep-l2-detach-diag.h250 | Existing head (cycle,UID) dedup per slice; a stalled UID reappears on later cycles. Skips versus covered probes are explicit. Head absent uses another population. | Repeated frontend exposures, not unique requests, whole-time occupancy or every B0 sample. R5 preserves actual same-head joints; do not multiply independent eligible/reuse marginals. |

The L2 callback is selected by the L2 clock, gpu-sim.cc2201-2221; LIFE tick_end advances an L2-tick counter, header306-309. Actual matched cases keep core/L2 at1132MHz, but that does not make DRAM-domain counters or different event populations interchangeable.

## 4. C7d issue-candidate events versus C7E channel ticks

**C7d counters contained in a B0 row do not all share the B0 sample denominator.**

l2cache.cc785-805 scans up to two subpartition lower heads per channel/DRAM call. Empty heads are skipped; a successful admission breaks the loop at837. A failed first candidate can be followed by the second candidate in the **same** DRAM tick.

- c7d_dram_issue_eligible / c7e_dram_issue_attempt increment once per evaluated nonempty candidate,1790-1791.
- credit/scheduler/return block counters use that candidate's booleans,1794-1800.
- scheduler_causal_block means scheduler_full && !return_block && !credit_block,1799-1800. It is local gate-isolation among inspected heads, not proof of unique end-to-end causal stall time.
- Candidate scheduler_occ_sum/samples update1801-1807 and the printed c7d average divides by dram_scheduler_occ_samples,2461-2462. It is **head-attempt-weighted**, not all-DRAM-tick-weighted.
- A meaningful conditional block frequency divides matching block counts by matching issue_eligible counts from the same slices/window. Reasons can overlap or be masked by earlier conditions; do not add them as disjoint causes.
- Summing candidate counts across64 slices is valid for total evaluated candidates. Dividing that sum by32-channel DRAM ticks can exceed1 because of the two-candidate scan. It is not a utilization or GPU-stall fraction.

By contrast, memory_partition_unit::c7e_sample_dram_cycle at l2cache.cc308-318 is called once at the start of each detailed dram_cycle,747. It samples one FRFCFS scheduler/DRAM returnq occupancy per **channel DRAM tick**, before m_dram->cycle. EPL2DRAMV1 at896-915 prints averages using m_c7e_dram_cycles.

There are32 distinct channel rows and64 subpartition rows. Mapping channel=floor(slice/2) is useful for time-context joins, but attaching the same channel row to both subpartitions must not double its DRAM-tick denominator. Aggregate C7E once over32 unique channels, never by summing a64-row joined copy. Candidate-weighted c7d scheduler occupancy and channel-tick-weighted C7E scheduler occupancy are different measures.

## 5. Accepted payload bytes versus true RD/WR columns

- Lower-pop admission: l2cache.cc819-835 pops actual L2-to-DRAM FIFO, records acceptance bytes, creates fixed-delay element and borrows credit.
- Classification uses requires_dram_to_l2_return at604-607: every access except L1/L2_WRBK is return-bearing. Both success callbacks receive (requires_return,!requires_return),820-823.
- c7e_record_dram_success399-409 and subpartition success1810-1822 count those accepted packet payload bytes. Thus successful_read_* means return-bearing population, successful_write_* means no-return WB population; generic ACK-bearing writes can fall under the former label.
- LIFE DRAM_ACCEPT is the same lower pop,1087-1093/1777-1780. LIFE DRAM_SERVICE is recorded in the success callback at1813, not at actual column service. DRAM_RETURN at1841-1843 is another acceptance point, into the destination FIFO.
- EPL2DRAMV1 bandwidth_util numerator is those lower-pop payload bytes; denominator is channel DRAM ticks*dram_atom_size,896-915. It is an ingress proxy, not a direct bus-service counter.

True column commands are dram_t::issue_col_command at dram.cc559-636: reads increment n_rd or n_rd_L2_A at581-584; writes increment n_write's source n_wr or WB n_wr_WB at617-620. One column transfers dram_atom_size=BL*busW*chips, gpu-sim.h295-296. Commands/payload packets/sector-ready bits remain distinct even where their fully drained endpoint byte totals happen to match.

Use the pure pinned agent_b/dram_terminal_extract.py SHA93d6140bc630f6e61f6e625b0613f926946bede4244102a9fca8640536d0617a. It selects complete final-clock DRAM[0..31] rows from dram.cc699-711, preserves alloc-read/WB splits, rejects conflicting repeats/missing final populations, and never adds repeated cumulative snapshots. n_cmd is DRAM calls/ticks, not read+write commands; n_req is MC push packets. Uninitialized n_ref_event is excluded. Optional absent helper scalars remain UNKNOWN.

## 6. Fixed-latency queue residence: not instrumented in application outputs

m_dram_latency_queue is a distinct list, l2cache.h287-292. Admission sets ready=current cumulative CORE counter+configured L, l2cache.cc827-835. Only its FIFO head can transfer to MC when now>=ready and scheduler is not full,842-850. DRAM-domain invocation is gpu-sim.cc2178-2184; CORE counter increments separately at2267.

Configured L100/200 is a **CORE-counter threshold**, not actual residence. Residence also includes DRAM-edge quantization, FIFO head blocking and post-deadline scheduler-full waiting. C7d lowerq is the preceding L2-to-DRAM FIFO; C7E scheduler occupancy excludes the delay list. Neither reveals its residence distribution. A final empty queue/status overwrite does not reconstruct per-packet enqueue/dequeue history. **Actual application delay-list residence sum/histogram/queue-time area = NOT_INSTRUMENTED.**

Passive future candidate, **not implemented or executed**: observe existing enqueue/pop only, maintain bounded per-channel occupancy area/event peak and completed-residence sum/log2 histogram, plus explicit right censoring and invalid/overflow markers. For immutable per-run L, enqueue core timestamp can be derived as ready_cycle-L at pop; otherwise store passive enqueue metadata. No extra lookup/CAM, admission probe, resource or timing decision is needed. Declare CORE-tick residence versus DRAM-tick sampled occupancy separately; preserve default OFF, output/state bounds and observer NI checks. Such instrumentation would need its own reviewed source qualification; this note does not authorize a patch or a new run.

A similarly passive RO-lower histogram candidate would update a transaction-count exposure accumulator from existing ro_update pending-state edges, without an address CAM. It would measure transaction concurrency only; distinct-line concurrency needs a separately justified design. No such histogram has been retroactively manufactured for c67.
