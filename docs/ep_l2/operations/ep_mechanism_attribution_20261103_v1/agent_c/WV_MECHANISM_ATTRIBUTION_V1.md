# W/V mechanism attribution V1

Status: **PASS** for offline accepted-evidence arithmetic and Source/config population checks. **PARTIAL** for request-level causal timing. No new application start, CPU protocol test, NI run, source edit or performance-policy change. Main alone owns publication and scientific admission.

## Exact scope and the comparison that is identified

Six accepted Source78 endpoints form two matched triples. Core `78f4b59e865b136eede74df74c44c210f5b4ca04`, Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`, vendor `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`, ELF `78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a`, library `e5a743a2bb796d82f58109251f43d5c1997d5c1f7fdeac61213416da3835b697`. Exact point/spec/validation SHA and all actual options are in `WV_ACCEPTED_EVIDENCE_AND_DERIVATION.json`.

Both triples retain 64 slices, 32 sets, 8 ways, 128 B lines, 1,168 physical Payload slots/slice, D512, WAD128, ordinary MSHR128, bank P1, `dram_latency=100` and the original clocks/queues. All 282 actual options equal their frozen expected options. S/W/WV have identical observer environments: SUMMARY_STAGE, MS/B0/M0 as accepted; heavy LIFE/Tag-pressure/detach/timeline OFF. M/T are OFF in all six. FWT is WV_ZERO_RO, never replaced with RO-F. Numeric SASS output remains UNKNOWN under the accepted contract; full declared commandlist and hardware drain are established. The immutable ACCEPTED_POINT's original archive_status=PENDING is chronological; later archive closure receipts in review a67 are the acceptance/restore evidence, not a reason to reinterpret that field as a current failure.

Actual hardware-option deltas are exactly:

- S to W_ONLY: `-gpgpu_ep_l2_ft_mode` 1 to 2.
- W_ONLY to WV_ZERO_RO: `-gpgpu_ep_l2_tvd_clean` and `-gpgpu_ep_l2_tvd_dirty`, each 0 to 1.

**PROVEN:** these are accepted within-input, within-ELF comparisons of complete mechanism packages. **Not identified:** a free-copy oracle or the marginal effect of a single Victim hit. W changes shared Payload organization/in-place WB, allocation, arbitration and resulting order as a package. V adds retention, directory query, reclamation, promotion and service; both clean and dirty V are enabled together.

| Exact input | S cycles | W-only cycles | WV cycles | W cycles vs S | WV cycles vs W |
|---|---:|---:|---:|---:|---:|
| GEMM `140f6ed3a5cdb1d7183cd4d2acc37b086224a054893ef12d990fdb2d5ea3659b` | 558,588 | 558,957 | 550,642 | +0.0661% | -1.4876% |
| FWT `fc3a90622744ba1f63bec264284983747a372e3a34543249c3977d4bd285fe2e` | 181,827 | 181,635 | 178,951 | -0.1056% | -1.4777% |

These deterministic point estimates are not replicated-population confidence intervals or evidence of general speedup across 35/96 inputs.

## Why fewer copies/bank operations give little W-only speedup

**PROVEN, GEMM:** physical bank grants fall only 18,553,495 to 18,542,850 (-0.0574%), while 16,809,984 resident-write bank events remain in W. S COPY_PIPELINE has 3,241 first-block requests and 3,241 accumulated wait cycles; W has zero. S/W lower read bytes remain essentially unchanged (3,160,704/3,160,192) and writes exactly 414,848. Credit, ReturnQ, scheduler-causal, lowerFIFO-full and MissQ-full counters are zero in both. W's bank_wait exposure rises 97,601 to 98,219 and DATA_SERVICE resolved first-wait sum rises 44,352 to 44,783. These small changes coexist with +369 application cycles. The result directly rejects an assumption that this small copy component is a large performance lever. **UNKNOWN:** whether core issue, dependence or another uninstrumented critical path dominates; low DRAM traffic alone does not prove a compute-only bottleneck.

**PROVEN, FWT:** bank grants fall 2,531,489 to 2,440,075 (-3.6111%), bank_wait exposure falls 76,155 to 57,192, COPY_PIPELINE 45,703 to zero, and WB_DATA_SPACE first-block sum 193,143 to zero. Yet cycles improve only 192. The accepted W run has 199,465 lowerFIFO-full and 201,212 MissQ-full observations versus 1/1 in S. SAME_ADDRESS_WB request-wait sum rises 209,836 to 214,139, with max 1,339 to 1,471. Scheduler causal-block observations remain similar (143,490/141,603). Successful lower read/write demand is nearly unchanged. **LIKELY:** freeing one admission/storage constraint changes the timing and location of pressure rather than eliminating lower service work. **UNKNOWN:** the exclusive contribution of that redistribution to the small net cycle delta.

Accumulated slice waits, bank operations, queue denials and DRAM channel cycles overlap, have different event populations, and cannot be added or subtracted to reconstruct GPU cycles. The counter changes demonstrate real local effects even when the application effect is near neutral. They do not establish a bug, nor do they justify queue expansion.

## What the V-enabled package demonstrably changes

| Measurement, W to WV | GEMM | FWT |
|---|---:|---:|
| Successful lower read bytes | 3,160,192 to 1,080,320 (-65.81%) | 7,412,992 to 4,614,016 (-37.76%) |
| Successful lower write bytes | 414,848 to 1,152 | 5,853,568 to 7,611,424 (+30.03%) |
| Actual Victim read responses in WV | 609,858 | 88,069 |
| Actual dirty-forward responses in WV | 0 | 3,312 |
| Victim directory queries / lookup-wait exposure | 619,160 / 619,160 | 150,462 / 150,462 |
| Victim read served bytes | 19,515,456 | 2,818,208 |
| Physical bank grants | 18,542,850 to 18,511,195 | 2,440,075 to 2,366,408 |
| Scheduler-causal block observations | 0 to 0 | 141,603 to 107,749 |
| LowerFIFO-full / MissQ-full observations | 0/0 to 0/0 | 199,465/201,212 to 188,426/190,082 |
| SAME_ADDRESS_WB accumulated first-wait sum | 0 to 0 | 214,139 to 89,726 |

**PROVEN:** enabling V in the W background improves cycles in both exact inputs and serves real retained data while reducing completed lower reads. GEMM gains 8,315 cycles, FWT 2,684. This is more than a count of hypothetical reuse opportunities. FWT also reduces the existing W-only downstream-block exposures, even though completed writes increase; total successful byte reduction is only 7.85%.

**LIKELY:** retained-data service avoids some demand and changes dependency/service order, offsetting its own lookup and allocation costs. GEMM's broad lower-traffic reduction with only 1.49% cycle improvement implies limited aggregate performance leverage for further traffic reduction. **UNKNOWN:** which response was on the critical path, the independent effect of dirty versus clean retention, and how much of FWT's gain comes from dirty-forward, shorter same-address waits, less read traffic or changed scheduling.

Victim served bytes are not avoided DRAM bytes: their populations include repeated local service and different sector/new-line behavior. Query events are not demand-read attempts alone, so read_responses/directory_queries is an event ratio rather than an accepted Victim demand hit probability. Completed lower write bytes are not all logical stores or forced-flush traffic. `-gpgpu_flush_l2_cache=0`; terminal TVD and resident dirty data need not be forced to DRAM. GEMM's 99.72% completed-write reduction cannot be described as eliminating 99.72% of writes permanently. FWT's write increase is retained, not normalized away.

## Retention field mapping: checked ambiguity, not a manufactured bug

The earlier Main primary projection uses its same-named `victim_sums.retention_slot_cycles` from the production field. Source78 `ep-l2-tvd-cache.inc:250-261` maps it to `tvd_extra_retention_slot_cycles`. `ep-l2-tvd-directory.h:372-381` separately accumulates CLEAN time and WB_INFLIGHT/WB_COMPLETE time. Thus this same-named field is **extra-only**, whereas `total_retention_slot_cycles=clean+extra` includes both counted state groups. WB_STAGED mandatory staging is a different counter, not silently part of either optional-retention denominator.

| Accepted treatment | CLEAN slot-ticks | WB_INFLIGHT/COMPLETE extra slot-ticks | Total counted TVD slot-ticks |
|---|---:|---:|---:|
| GEMM WV | 2,375,975,574 | 218,208 | 2,376,193,782 |
| FWT WV | 6,543,794 | 858,885,334 | 865,429,128 |
| Historical Stencil F | 2,554,982,110 | 36,170,889,964 | 38,725,872,074 |
| Historical Scan F | 1,922,397,992 | 14,394,526,444 | 16,316,924,436 |

All sums come from the 64 final slice records; the per-slice clean+extra=total identity passes. A suspiciously small GEMM extra value prompted this audit. The suspected mismatch is resolved by the explicit source mapping: **no producer defect or previous Agent A error is established.** Prior Agent A's Stencil/Scan service density used total, giving approximately 372.04 times greater Stencil read-response events per total counted TVD slot-tick. That arithmetic remains valid. Comparing prior total to current extra-only would be invalid; this new table prevents that misuse.

This density is a retrospective state-area/service descriptor. It is not a cache hit rate, an average entry lifetime, proof of useless individual entries, a critical-path speedup, or an independent prediction for unseen inputs. Large final live counts alone do not reveal how many entries were useful before reclamation or how much dirty state remains.

## Mechanism opportunity and what could predict it

**PROVEN retrospective observations:** Stencil F serves 4,930,616 Victim reads with lower completed reads down 46.94% and no lowerFIFO/MissQ/scheduler full observations. Scan F serves only 5,584 Victim reads despite substantial retained-state area; completed read/write demand barely changes, and lowerFIFO/MissQ pressure increases. Both remove many copy operations, yet only Stencil strongly speeds up. GEMM and FWT's new W-to-WV comparisons now independently identify an actual V-package benefit in their W background. These facts support separating useful retained service from mere copy volume.

**HYPOTHESIS for future independent prediction:** post-eviction reuse within a realistic retention horizon, attainable service latency relative to lower miss service, actual optional-space contention, and query traffic from negative probes should jointly matter. A high count of evicted lines or optional occupancy alone is inadequate. Exact-input historical locality identity is not closed, so existing Motivation/Streaming statistics cannot be joined merely by names, paths or sizes. Current V-service/retention and traffic reductions are post-treatment descriptors, not a pre-run classifier. Validate any future feature/cutoff on an independently frozen input set and retain negative cases.

## Minimal next action and limits

Use the already-running Stencil W/WV results only after CLOSED_ACCEPTED, complete 100-kernel/CTA/instruction/drain checks and real164 archive/restore closure; see the conditional matrix. Do not add Scan or new application points in this task. No source policy should be changed simply because a density looks low. If a structure choice remains unresolved after Stencil, the smallest decision-changing observations are per-kind entry served-before-reclaim and first/last-service timing, mandatory-versus-optional state, and query outcome population, with active terminal entries marked censored. No full-cycle dump, giant Trace rescan, additional latency/geometry scan or ideal/free-service experiment is required now.

Verification actually executed here: one bounded Python arithmetic/identity derivation over named static JSONs, checking six point/spec/validation hashes, exact Source5/input and 282 option echoes, mode-only option deltas, completion invariants and 64-slice retention/byte identities. These are offline evidence checks, not new CPU protocol/NI or GPU application validation. Both Stencil points were pending at the sole observed status snapshot; this report neither waits for nor predicts their outcome.
