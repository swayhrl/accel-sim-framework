# Lower-issue admission byte/event clarification

Status: **PASS for bounded production-source mapping; no producer bug established.** This additive clarification supersedes timing/classification interpretations of the existing C7E ?successful DRAM read/write bytes? labels in Agent C's original report. Original reports, accepted projections, manifests and numerical results remain unchanged. No new raw data was read, no model/CPU/NI run performed and no Source edited.

## Exact production event

Independent source inspection of accepted Source78 `l2cache.cc`, `memory_partition_unit::dram_cycle`, confirms:

1. Lines793-807 inspect the L2-to-DRAM FIFO head and record C7E issue-attempt, credit/return-pressure and scheduler-full observations.
2. After the issue gates, lines821-825 pop that FIFO head and invoke `l2_char_record_dram_success` and `c7e_record_dram_success` with the payload `get_data_size()`.
3. Lines829-838 then construct and enqueue the fixed DRAM-latency-queue entry, assign its ready deadline and borrow partition credit.
4. Only later, at lines845-854, does the ready head leave that delay queue and call `m_dram->push(mf)`, subject again to scheduler capacity.

Therefore **the byte and issue counters mark successful lower-issue admission / FIFO-to-fixed-delay-queue transfer**, before actual DRAM scheduler entry and before service completion. The `successful` label denotes admission success, not completed DRAM service. The fixed delay's configured value is not measured queue residence, and none of these bytes measures the post-deadline scheduler waiting time.

## Classification is return-required versus WB

The argument named `is_read` at this record site is `requires_dram_to_l2_return(mf)`; `is_wb` is its negation. Source78 lines605-608 define the helper by excluding `L1_WRBK_ACC` and `L2_WRBK_ACC`. Hence the first bucket is **return-required/non-WB requests**, and the second is the two WB access types. This is not an independent physical DRAM RD-versus-WR command classification. Non-WB writes are not excluded merely because the emitted field is called read. Causal comparisons must preserve the actual event/class populations rather than turn names into demand-read or bus-command identities. Detailed per-access classification remains with Main/Agent D's audit.

## Correct interpretation of this delivery's tables

The previously reported GEMM/FWT W-to-WV C7E first-bucket byte changes (-65.8147% and -37.7577%) remain exact arithmetic for the same accepted event population. Describe them as **return-required lower-issue admitted payload bytes**, not demand-read bytes completed at DRAM. Their second-bucket values remain **WB lower-issue admitted payload bytes**, not timed completed physical DRAM writes. Whole-application cycles and the identified W/WV package-level performance effects are unchanged.

The accepted entire-commandlist plus hardware-drain contract ensures admitted transactions are eventually drained within that accepted application scope. It permits whole-application comparison of the admitted workload population, but does not move the counter's recording timestamp to service completion. In particular, per-kernel shared-counter deltas or time-window deltas can include admissions whose service completes after that boundary; they cannot be called that kernel's completed DRAM service. Traffic class, clock/window boundary, source, accepted population and denominator must accompany any such table.

Actual Victim read response/served-sector events are separate production counters and retain their original service-event meanings. They must not be equated one-for-one with avoided first-bucket admitted bytes. All admitted transaction drain also does not force every dirty resident/Victim cache line to memory: the earlier no-forced-L2-flush caveat remains essential. This clarification establishes neither a failure to drain nor a performance-model defect.

## Suggested paper and summary names

| Preserve raw field name | Preferred displayed description | Do not call it |
|---|---|---|
| `c7e_dram_successful_read_bytes` | Return-required lower-issue admitted payload bytes | Completed DRAM reads; physical RD bus bytes; pure demand-read bytes |
| `c7e_dram_successful_write_bytes` | WB lower-issue admitted payload bytes | Forced-flush program store bytes; physical WR command bytes; timestamped completed service |
| Corresponding successful read/write issue counts | Admitted return-required/WB lower-issue requests | DRAM completed response counts |
| C7E issue attempt/full/credit observations | FIFO-head issue-gate observations in their declared sampling domain | Unique requests or exclusive critical-path stalls |

For legacy compatibility keep exact raw keys in machine evidence and append event/class metadata; do not rewrite accepted assets. If independently measured DRAM command/service counters are used in future, cite their own instrumentation site and scope instead of silently substituting the C7E values. Main should apply this naming correction to public summaries; no extra simulation or recapture is needed to make the event boundary accurate.
