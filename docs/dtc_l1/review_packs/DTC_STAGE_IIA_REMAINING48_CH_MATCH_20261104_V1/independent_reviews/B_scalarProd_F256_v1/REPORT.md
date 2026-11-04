# scalarProd-F256: closed four-source negative-CH response

**Fixed as-of:** source-qualified provider 2026-11-04 10:16:09 Asia/Shanghai (02:16:09UTC), snapshot 20261104T021610149488Z_429a0980. Only CH-P0/CH-F256/DH-P0/DH-F256 are analyzed. CH-F128 is AWAIT_ROOT_RESULT in this captured context; no six-cell or F128 performance is fabricated. The upstream context may show a legitimate old DH-F128 reference, but it is not consumed for this comparison.

**Finding:** CH regresses 1,535 cycles (+0.3651%) while DH improves 1,828 cycles (-0.4448%). Both designs have unchanged read request/miss/DRAM-read volume and lower L2 retry/admission events. Nevertheless, direct existing raw observations show higher FR-FCFS pending-queue occupancy and a heavier MRQ request-latency tail in both designs. This is a useful negative-CH case, not proof the tail caused its regression: DH becomes slightly faster despite the same tail direction.

## Exact identity, scale and kernel scope

Frozen input `2b93f70cd0666c5112f5550aae7b3a8d0565de1de40604d494bdc36c503f6954`. Actual declared-body qualification and strict/raw/header evidence: one `_Z13scalarProdGPUPfS_S_ii` kernel, grid (128,1,1),block (256,1,1),128 CTAs, shared 4096 bytes,23-register header,730,610,912 active-thread instructions, stream0. All four sources match this exact order/extent and build. Actual HtoD commands copy 57,016,320 bytes for each input array, total 114,032,640 bytes.

Fixed Atlas 47a097aad4406893a07f8d230e1e0a850609bf39 maps the candidate at app commit b059fdae25c2aabf737486aada743fca114469ce: scalarProd.cu parses 13920 as VECTOR_N and fixes ELEMENT_N 1024; therefore candidate scale is 13,920 dot products of 1024 elements. This agrees with copy sizes and header but does not newly certify original numeric bytes/ELF.128 CTAs must not be mistaken for 128 output vectors: the candidate CTA loops vec=blockIdx+128*r, handling 108 or 109 vectors.

Candidate `kernel.cu:34-79` loads four accumulator positions per thread then performs a 1024-element shared reduction for each vector; read/accumulate/reduction phases repeat across vectors/CTAs and overlap across CTAs. No separate reduction kernel exists. Existing perf CSV has exactly one terminal row in each run, with no intermediate source-phase timestamp. GPU sim_cycle+tot_cycle and sim_insn+tot_insn sums reconcile; the perf row precedes cumulative folding (tot fields 0), so tot_cycle=0 is not zero execution. Consequently only the whole single kernel is measured; source-level read/reduction phases cannot be assigned separate measured cycles or queues.

## Cycles and relative-benefit interpretation

| Source | Kernel cycles = whole replay | Delta vs same-design P0 |
| --- | --- | --- |
| CH-P0 | 420,477 | 0 |
| CH-F256 | 422,012 | 1,535 |
| DH-P0 | 411,009 | 0 |
| DH-F256 | 409,181 | -1,828 |

| Metric | Value |
| --- | --- |
| S_CH | 0.996363 |
| S_DH | 1.004467 |
| R_P0 | 1.023036 |
| R | 1.031358 |
| I | 1.008134 |

I factorization = 1.003650616 (CH cycle-regression factor) * 1.004467461 (DH own speedup) = 1.008134385. Relative improvement 0.8134% includes both CH deterioration and DH small gain; it is not 0.8134% DH self-speedup. Same-F CH/DH 1.031358 favors DH in this one input/configuration, with architecture/cost differences preserved. No partial-suite GM or unified configuration choice is made.

## Read/write traffic and L2/admission events

L2 GLOBAL accepted/miss quantities are 32-byte sectors; DRAM read/write quantities are issued 32-byte atoms. DRAM n_req/MRQ histogram counts are request objects: a 128-byte writeback may issue 4 atoms. Do not equate these populations.

| Counter | CH-P0 | CH-F256 | DH-P0 | DH-F256 |
| --- | --- | --- | --- | --- |
| GLOBAL accepted read sectors | 3,563,520 | 3,563,520 | 3,563,520 | 3,563,520 |
| GLOBAL read misses | 3,563,520 | 3,563,520 | 3,563,520 | 3,563,520 |
| All-L2 misses, incl writes | 3,565,260 | 3,565,260 | 3,565,260 | 3,565,260 |
| DRAM read atoms32B | 3,563,520 | 3,563,520 | 3,563,520 | 3,563,520 |
| DRAM write atoms32B | 1,532 | 1,536 | 1,536 | 1,536 |
| DRAM request objects | 3,563,903 | 3,563,904 | 3,563,904 | 3,563,904 |
| L2 reservation retry events | 48,623 | 31,340 | 52,397 | 34,126 |
| ICNT-to-memory blocked admission events | 13,069 | 8,393 | 15,765 | 8,554 |

All GLOBAL accepted reads are misses in these observations, with 3,563,520 read sectors/DRAM read atoms = 114,032,640 bytes, equal to the two input-copy sizes. This is observed access behavior under the fixed replay, not a compulsory/capacity/conflict or cold-miss classification. The write miss count is 1,740 sectors for all four runs. CH adds 4 issued write atoms at F256; DH write count is unchanged. Issued writes are not proof of complete final dirty-cache drain.

| L2 GLOBAL-read retry reason | CH-P0 | CH-F256 | DH-P0 | DH-F256 |
| --- | --- | --- | --- | --- |
| MISS_QUEUE_FULL | 9,726 | 509 | 14,587 | 480 |
| MSHR_ENRTY_FAIL | 38,897 | 30,831 | 37,810 | 33,646 |
| MSHR_MERGE_ENRTY_FAIL | MISSING | MISSING | MISSING | MISSING |

Entry-capacity retries and miss-queue retries fall in both designs; unprinted merge-list reasons remain MISSING, not imputed 0. Events do not measure stalled cycles, queue occupancy or critical-path time. The legacy gpu_stall_dramfull is ICNT admission, not isolated DRAM-queue wait. No time-average/peak L2 miss-queue occupancy is available in these logs; each of the 40 L2 miss-queue terminal dumps is explicitly empty, a terminal gauge only.

## Existing raw DRAM queue observations: occupancy, not latency

Fixed Core dram.cc:323-346 samples FR-FCFS num_pending after scheduling once per dram_t::cycle; ave_mrqs/n_cmd is the cumulative per-controller pending-request mean over all DRAM ticks (including idle/launch ticks). The peak is sampled at that same after-scheduler point. It excludes active bank service and is not L2 MSHR occupancy or a request-duration mean. Raw queue_avg is printed with decimals; mrqq:max/avg is a second view. Both were parsed and crosschecked without modifying strict metrics/reader.

| Source | Mean pending / controller / DRAM tick | Controller mean range | Highest sampled peak over 20 controllers | DRAM ACT/PRE counts |
| --- | --- | --- | --- | --- |
| CH-P0 | 37.853456 | [35.72274, 39.552471] | 64 | 145424/145344 |
| CH-F256 | 41.238297 | [38.332279, 44.23243] | 237 | 140919/140839 |
| DH-P0 | 39.638757 | [38.595219, 40.990555] | 64 | 139332/139252 |
| DH-F256 | 43.726849 | [41.587612, 46.293053] | 243 | 135152/135072 |

The pooled mean weights each printed controller mean by its n_cmd; all 20 controllers share equal n_cmd within a run, so this also equals the simple controller mean up to printed precision. Occupancy rises from 37.8535 to 41.2383 in CH and 39.6388 to 43.7268 in DH. Peaks rise 64 to 237/243. The accumulator's maximum-sample*n_cmd bound is below 2^32 for every controller here, so unsigned ave_mrqs overflow cannot explain these particular values. Larger occupancy does not establish a corresponding critical-load delay or explain the opposite total-cycle signs.

Read atom totals are exactly balanced across 20 controllers (read-volume CV 0). Each controller has 4 of 16 nonzero printed bank-read-command counters. The fixed source increments this field on RD only; it does not imply the other banks had no write activity, prove a bank bottleneck, or identify mapping as the cause. Dirty writeback/order, bank service and credit occupancy are not causally separated.

## Latency histogram and extrema, with exact units/windows

All four strict mean latency dictionaries are {} and raw means are suppressed. Single-kernel cycles are below 500,000; fixed print-before-stat-fold ordering can leave num_mfs=0 and suppress the mean block even though other counters are populated. Missing means remain MISSING, never 0. Decimal queue_avg is an occupancy metric, not an unparsed average latency.

Existing mrq_lat_table contains 32 explicit floor-log2 bins. Fixed dram_req_t timestamps request construction in global core cycles; dram_sched.cc records elapsed time when the request is assigned to a bank. Thus this spans staging/FR-FCFS scheduling to bank assignment, not complete L2-to-DRAM service or a known critical load. The histogram sums exactly to controller n_req in every run, about 3.564 million request objects; all terminal DRAM latency queues are empty. It is independent of the num_mfs print gate.

| Source | MRQ request samples | Fraction>=512 core cycles % | Fraction>=1024 cycles % | Median bucket bounds | p99.9 bucket bounds | Mean bounds only |
| --- | --- | --- | --- | --- | --- | --- |
| CH-P0 | 3,563,903 | 0.060299 | 0.000000 | [32, 63] | [256, 511] | [66.05528208820498, 131.05483678989017] |
| CH-F256 | 3,563,904 | 0.614242 | 0.018435 | [32, 63] | [512, 1023] | [71.98694970459361, 142.98602291195274] |
| DH-P0 | 3,563,904 | 0.044867 | 0.000000 | [32, 63] | [256, 511] | [67.56857816596631, 134.10907224212548] |
| DH-F256 | 3,563,904 | 0.623530 | 0.018996 | [64, 127] | [512, 1023] | [73.85954447706784, 146.67717620901124] |

P99.9 moves from the 256-511 bucket to 512-1023 in both designs. The>=512 cycle share grows CH 0.0603% to 0.6142% and DH 0.0449% to 0.6235%. These are request-tail facts, not a claim the median doubled or the tail lies on the critical path. P0/F256 derived mean intervals overlap; the bins do not yield an exact mean or prove its increase. No midpoint is substituted for an observed average.

| Source | maxMRQ | maxMF | maxICNT-to-memory | maxICNT-to-shader |
| --- | --- | --- | --- | --- |
| CH-P0 | 856 | 1,496 | 478 | 54 |
| CH-F256 | 1,878 | 2,261 | 393 | 63 |
| DH-P0 | 874 | 1,558 | 458 | 56 |
| DH-F256 | 1,632 | 1,981 | 368 | 60 |

MRQ/MF extrema rise while max ICNT-to-memory falls. These are different event populations/segments; they must not be subtracted into DRAM service time or treated as average delay. Longer request tails are consistent with the larger window/credit behavior, but DH's slight speedup despite that direction prevents a simple tail-to-total-cycle causal story.

## Typed frontend/finite service and source limits

CH PAPER_BASE uses common PIB 256; DH PAPER_OO uses its active PIB 128, while generic PIB 8 is inactive for OO admission. CH common Tag-conflict attempts remain 2,672,640, PIB-full events 0 and per-SM PIB peak 32; ordinary L1 entry/merge-full events are 0. They are not OO measurements. DH OO PIB-full/Tag-conflict event counters remain unprinted/null.

DH has 890,880 new read-line misses/lower 128B creations and 0 valid/0 pending line hits in both profiles; accepted L2 read sectors equal 4*890,880. Hence no measured OO read-line reuse or request-count reduction explains the small DH gain here. The candidate has no inter-vector input overlap, but static source addresses are not substituted for runtime classifications.

| DH profile | Mean PIB entries, all64SM samples | Mean physical lines | Ready-to-retire cycles / retired entry | Writeback wait sum |
| --- | --- | --- | --- | --- |
| P0 | 16.339544 | 250.179349 | 2.247672 | 110,739 |
| F256 | 16.179844 | 250.401694 | 2.256546 | 112,900 |

Ready-to-complete and writeback sums slightly rise even as DH cycles fall; these all-entry/sample sums and means are not critical-path timing or per-SM peaks. Low mean PIB usage does not exclude bursts or dependency pressure. Cross-design L1/Tag/physical pool/queue/timing/area remain unequal.

Within each design only FR-FCFS 64 to 256 changes, and the fixed Core couples shared-credit 255 to 447 with it (return queue 192, two subpartitions). DRAM 850 MHz, Core/ICNT/L2 clocks, 10 MiB L2/mapping and frontend mechanism remain fixed. This is queue-window plus credit expansion, not an isolated queue-capacity intervention or equal-area claim.

## Facts, association and unconfirmed cause

- Fact: one measured kernel; CH negative/DH small positive; fixed read volume, fewer retries/ICNT admission events, higher FR pending occupancy and heavier MRQ tail. No F128 result is fabricated.
- Source deduction: repeated per-vector global reads plus shared reduction/barriers; fixed active window/credit and sampling/print semantics. Original capture ELF/numeric linkage remains unconfirmed.
- Association: the larger coupled window changes queue occupancy and request tails while total cycles move differently across designs.
- Unconfirmed: critical-request identity, bank/credit/return-path occupancy histories, and whether memory-stage versus shared-reduction/issue/finite-service timing determines the 1535/-1828 cycle changes. Existing one-terminal-row perf data cannot split those phases. No new instrumentation, rerun, additional model or configuration is launched.

## Evidence

SOURCE_SNAPSHOT_RECEIPT.json and CAPTURED_SOURCE_QUALIFIED_PROVIDER.json pin the actual qualified snapshot 7bd245cec0b447aa73461676078c08afb4fd633e3db3c0e681f9f03b5fbb695a/provider b2ccd243963c7a355b11f93cdcaef6e0b9028ca9e89fe01edbb2247661007626. Old source roles and actual profiles are retained. V1_PARSER_CONSUMPTION.json proves all 28 V1 members unchanged and records the exact reused parser SHA; current child adapts only scalarProd/P0/F256 filtering. FORWARD_EVIDENCE_BOUNDARIES.md preserves reviewer terminology: read-active, no unproved cold/miss class or request-origin attribution.

CLOSED_SOURCE_KERNEL_COUNTERS.json.gz contains four RESULT/raw/exit/input SHA and whole-kernel explicit endpoints; RAW_QUEUE_AND_LATENCY_HISTOGRAM.json contains all 20 controller values/bins/derived bounds/quantiles; QUEUE_LATENCY_FIXED_SOURCE_SEMANTICS.json pins Core 9eed paths/SHA/line excerpts. ACTUAL_INPUT_CONTRACT.json and EXISTING_WITHIN_KERNEL_OBSERVABILITY.json retain actual geometry/body count and each closed terminal CSV SHA. FIXED_ATLAS_SCALARPROD.md is exact Atlas 47a source candidate documentation.16 parser/identity checks plus 352 queue/hist checks pass (368 counted checks); additional typed/header/perf assertions are recorded by their evidence. No live raw, reader/native/owner/registry/Git/paper change.

| Source | Role | RESULT path | RESULT SHA256 | Raw gzip SHA256 |
| --- | --- | --- | --- | --- |
| CH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-2b93f70cd0666c51-CH-P0-V1.RESULT.json | 00f7ea785001d570cfdcdb529300ae6691e04fd59e174aadd3323d599e5097d0 | 097062178f9f6e8a1cb485701d2bbc049e0d29d2f9aea4f057e49ee3f75fb4e2 |
| CH-F256 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-2b93f70cd0666c51-CH-F256-V1.RESULT.json | d42da18677f36bc926ff29897a065f002bd2b1fbe958515cb7641ae32937386e | a2dd45fa99f9b7c9bd9070f9b74b9cc164c8824d700dbaf97870c5d7f7d5986e |
| DH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-2b93f70cd0666c51-DH-P0-V1.RESULT.json | fd553c2c1bf01b772e8b7a6ffef3f7cc1ae97f61e2feec6d2e7768b5f0a3e3b5 | 840adc10e108539e115766d5cc3066ebb4ddccbadce81848ef23141a0eddb367 |
| DH-F256 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-2b93f70cd0666c51-DH-F256-V1.RESULT.json | d23123a56ac51b652d05179fdfb4ad4e1da4a6b551f45eddc831899653b77b50 | 39627267fbb8ba47a6e4d717615cbf77e38340e164d148e3088ce3f53117adce |
