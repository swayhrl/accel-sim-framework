# Capacity metrics collector field and unit boundary

Frozen tool: agent_b/collect_capacity_metrics.py
SHA256: f117a1a0e615881b079016b25ae28ca76d605a14e5b54d59af832b7bdcfdec9d

Interface: collect(bundle_path, raw_path, spec_path, point_path) returns a dictionary. CLI accepts --bundle --raw --spec --point and emits JSON to stdout only. It grants no authority and writes no files. Reporting output is capped at16MiB by the CLI.

The point must be the current Goal's EP-MAIN EP_L2_TAG_CAPACITY_APPLICATION_ACCEPTED record. Exact bundle/raw/spec digests, source identity, SourceQ hash, geometry, T, instructions/CTA/slices/kernel/drain and production TagFAIL/detach counts join the supplied artifacts. The LIFE scan rehashes actual bytes to reject changes after the initial raw join. This reports already accepted evidence; it does not reproduce scientific admission.

| Output group | Values and units | Limits |
|---|---|---|
| application | Native cycles;56M instructions;15625 CTAs;drain; aggregate instructions/core-cycle IPC; clocks | IPC is whole-GPU native count per core cycle, not SM/warp issue IPC. Numeric SASS output remains UNKNOWN. |
| R4 | All212 global counters; selected production TagFAIL/relieve/detach/rewrite funnel; denied/early/mask/primary blocks | Names retain original event populations. Production raw_tag_fail_commit differs from diagnostic raw_reservation_fail. Multi-reason counts are not disjoint global stalls. |
| R5 | Global/per-slice target-set reserved-way histograms; actual-head newTag/FAIL with eligible/reuse joints; route joint | Denominator is repeated covered frontend-head exposures. Actual W is used. R5 has no physical set ID: per_physical_set_R5 is UNKNOWN. |
| LIFE.per_physical_set |64*S rows of area[17], counters[55], episode histograms, incarnation/touch and new-head/unique-arrival reserved-count joints | Inactive bins above W must be zero. Mean occupancy is exact weighted Tag-L2-ticks / observed L2 ticks, distinct from R5 head sampling. |
| LIFE.aggregate | Event/tick-end maximum in any single set, area-weighted mean and logical-way fraction, completed new-request waits, episode and incarnation statistics | Peaks are maximized across sets, never summed as concurrent whole-GPU occupancy. Whole-GPU simultaneous peak is UNKNOWN. NEW_AT_k means exact k, not at least k. |
| LIFE episodes | Closed new-allocation and re-reservation count/sum/max/mean;33-bin log2 lifetime intervals; left/right observed overlap | Bin0 is0;bin b1..31 is[2^(b-1),2^b-1];bin32 is>=2^31. Exact quantiles and censored full lifetimes are UNKNOWN. Mean of closed population does not estimate full uncensored lifetime. |
| LIFE arrival joints | Actual reserved Tags at NEW_HEAD and first FIFO NEW_UNIQUE; separate unique-with-pending/eligible | Pending and eligible marginal counters do not establish their conjunction. That conjunction is UNKNOWN. |
| memory_path.DRAM |32 original channel snapshots; sums of disjoint successful read/write bytes/command issues; summed byte numerator/denominator utilization | DRAM-domain ticks differ from core cycles. Service commands are not L2 line requests. Queue maxima are per-channel samples, not simultaneous global peaks. |
| memory_path.cache/L1 | Native L1/L2 accesses, misses and reservation failures; L1 named failure counters; exact miss/access ratios | Retry/miss/failure populations retain original labels. No subtraction into unique demand or global stall time. |
| memory_path.queues_and_resident |64 B0 sampled queue/descriptor/Tag/resident fields, maxima across individual slice maxima; M0 exact Resident occupancy sums/sample denominators | Intratick queue high-water marks are UNKNOWN. Printed averages are rounded/truncated; never reconstruct exact sums from them. Physical Resident capacity remains1024 regardless logical Tag count. |
| memory_path.WB | FT created/lower-accepted/completed packet events; emitted lower_wb_bytes and other local-service counters | DRAM write bytes, WB packets and lower writes are separate populations; no cross-layer subtraction. |
| memory_path.MS_first_waits | Original first-block request/wait histograms and overlapping slice observations | No sum as GPU cycles and no Amdahl fraction. |
| RO | Per-slice shared descriptor/transaction peaks and RO issued-not-returned lower concurrency | Independently timed maxima cannot be added as concurrent pressure. Whole-GPU simultaneous peak is UNKNOWN. |

Pure verification:13 controls PASS, receipt agent_b/metrics_engineering/7fa73d04-31fb-43b3-9966-3f496ee4b311/RESULT.json
SHA256: d5522563f4295f2209283c3cda1470a31391b7ee3aca10401b47f2f5309daccb

Controls include AST/import, explicit ratio denominator, zero-denominator UNKNOWN, unsigned range/type checks, vector/duplicate-field rejection, exact joint counts, real8-way denominator, open-ended lifetime bin, rejection of prior-Goal accepted artifacts and rejection of a one-slice CPU LIFE stream as a full application.

No new full application positive was processed; no ELF, model, native actor, GPU, budget or registry operation ran. Prior11c data supplied structure or negative authority only. Frozen validator/parser files were unchanged.
