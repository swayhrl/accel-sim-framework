# PQ/PS Independent Review — Agent E

Cutoff: 2026-10-27T07:32:45+00:00; accepted 10/18, pending 8/18. Periodic observations are a fixed 2026-10-27T07:18:10.392918+00:00 snapshot.

## Accepted results

| Input | Cell | Perturbation | P0 cycles | Perturbed cycles | P0/perturbed | Cycles change |
|---|---|---|---:|---:|---:|---:|
| ATAX | CH | PQ | 28,428,842 | 30,737,948 | 0.924878 | +8.122% |
| ATAX | CH | PS | 28,428,842 | 20,724,681 | 1.371738 | -27.100% |
| MVT | CH | PQ | 26,581,175 | 23,576,996 | 1.127420 | -11.302% |
| MVT | CH | PS | 26,581,175 | 18,407,388 | 1.444049 | -30.750% |
| BICG | CH | PQ | 26,298,698 | 24,356,422 | 1.079744 | -7.385% |
| BICG | CH | PS | 26,298,698 | 22,474,128 | 1.170177 | -14.543% |

These are strict accepted whole declared-input results, backed by successful natural DONE, matching NATIVE_EXIT, strict resolved-option/population checks, archive verification and independent native restore. They are separate from original288 and correctness repair data. They do not newly prove full-application numerical correctness.

PQ is not uniformly beneficial: ATAX CH regresses despite zero FIFO-full events in the observed PQ intervals. MVT CH and BICG CH improve. This supersedes the early first5% “approximately unchanged” observation for whole-input reporting; that early statement remains valid only for its sampled work frontier.

All K_PQ/K_PS values remain PENDING until the matching CH_P0,DH_P0,CH_perturbation,DH_perturbation cells all close. A completed BICG CHPS/DHPS pair alone cannot establish relative recovery from P0. Missing DH baselines are never filled with historical original-build data.

## Configuration qualification

All18 frozen specs and24 profile config files match SHA pins. Within each CH or DH family, PQ changes only `-gpgpu_dram_partition_queues`64:64:64:64→64:256:64:64; PS changes only `-gpgpu_clock_domains`1410:1410:1410:850→1410:1410:1410:1700. Closed accepted resolved option dumps match their frozen expected options exactly. Pending cases receive static qualification only, without reading active raw. FRFCFS64, DRAM return192, L2 configuration, geometry, timing-count parameters, mapping and core/ICNT/L2 clocks remain identical within the relevant matched family.

The second partition-queue field is the L2→DRAM FIFO. Enlarging it does not enlarge the FRFCFS scheduler or return queues. PS reduces DRAM tick time from1.17647ns to0.588235ns; e.g. unchanged RCD12 becomes14.1176ns→7.05882ns, RAS28 becomes32.9412ns→16.4706ns. Fixed `dram_latency=100` is scheduled in core-cycle units and remains about70.922ns. Therefore PS is not a pure bandwidth2x test.

## Kernel and sampled-work audit

| Input/cell/profile | Kernel1 speedup | Kernel2 speedup |
|---|---:|---:|
| ATAX/CH/PQ | 0.920202 (PROFILE_SLOWER) | 1.002477 (PROFILE_FASTER) |
| ATAX/CH/PS | 1.394435 (PROFILE_FASTER) | 1.099193 (PROFILE_FASTER) |
| MVT/CH/PQ | 1.137512 (PROFILE_FASTER) | 1.001546 (PROFILE_FASTER) |
| MVT/CH/PS | 1.476896 (PROFILE_FASTER) | 1.098097 (PROFILE_FASTER) |
| BICG/CH/PQ | 1.000000 (EXACT_EQUAL) | 1.085915 (PROFILE_FASTER) |
| BICG/CH/PS | 1.095249 (PROFILE_FASTER) | 1.175909 (PROFILE_FASTER) |

The first5% PS comparisons use the same per-kernel active-thread-instruction frontier (3,569,049.6 for the slow strided kernel), and GPU core cycles, not elapsed host time. Sampling interpolates aggregate retirement, not an exact per-warp loop j. Enclosing sample brackets and bounds are retained in JSON. An approximately2x early result does not establish2x kernel or application acceleration. Exact equal complete-kernel cycles are labelled `EXACT_EQUAL`, not unresolved sampling precision. Completed kernels inside still-live inputs remain provisional and are not promoted here.

## Queue/traffic interpretation

L2 FIFO-full counts are full-admission observations aggregated across subpartitions, not exclusive core stalled cycles and not latency. Fixed-snapshot observed PQ intervals have zero FIFO-full events. An unobserved tail is not presumed zero. There is no exported periodic FRFCFS/return-queue wait sum/count or causal UID stage ledger, so bottleneck transfer is UNPROVEN. Full accepted L2/DRAM read sectors/bytes, latencies and traffic changes are supplied in JSON. `avg_mrq_latency` measures dram_req construction to FRFCFS bank assignment in core cycles; it excludes earlier L2 FIFO residence and later full completion. Different request populations prevent a latency-only causal explanation.

## Designed follow-ups — not executed

- **PS_NS_MATCH — NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED:** Separate faster command/data opportunity from reductions in absolute DRAM timing delay. Keep DRAM=1700MHz; double each elapsed-time DRAM-clock parameter from the 850MHz P0 (RCD/RAS/RP/RC/CL/WL/RRD/WR/CDLR/RTPL, bank-group CCDL where applicable), after auditing derived expressions and constraints. Keep core-clock fixed delays such as dram_latency=100 and L2 ROP unchanged. Keep geometry, mapping, request/return queues, scheduler and input fixed.
- **PQ_X_PS — NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED:** Test interaction between FIFO capacity and DRAM time-domain speed. 2x2 of FIFO64/256 and850/1700MHz; existing P0/PQ/PS are three corners. Only after they close strict accepted, add joint corner for matched CH/DH using identical existing binary/config contract.
- **INSTRUMENT_STAGE_WAIT — NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED:** Distinguish FIFO backpressure removal, scheduler waiting, return congestion, L2 replacement/reissue and DTC completion service. Instrumentation-only build with counters for queue occupancy-cycle sums/high-water marks/full events; request UID+stage enqueue/dequeue timestamps for L2 miss/FIFO, dram-delay, FRFCFS, bank issue/data ready, return FIFO, DTC completion/retirement; per-kernel sums/counts/histograms. Bounded event sampling keyed by stable UID. Never change allocation/arbitration/admission.

## Accepted traffic and latency associations

| Input / CH change | L2 accepted read traffic | DRAM issued reads | avg_mrq_latency (core cycles) |
|---|---:|---:|---:|
| ATAX / PQ | +0.293% | +9.524% | 412 → 375 |
| ATAX / PS | +5.438% | +42.665% | 412 → 204 |
| MVT / PQ | +3.200% | -13.303% | 455 → 478 |
| MVT / PS | +7.570% | +31.590% | 455 → 187 |
| BICG / PQ | +0.733% | -7.147% | 526 → 510 |
| BICG / PS | +7.442% | +66.010% | 526 → 257 |

PQ ATAX CH exhibits more DRAM traffic and longer total execution despite lower mean scheduler waiting; MVT CH improves with fewer DRAM reads despite a higher scheduler-wait mean. These facts rule out interpreting avg_mrq_latency alone as an application bottleneck measure. PS improves all three completed CH inputs while issuing substantially more DRAM reads (+31.6% to +66.0%), and mean scheduler wait decreases. Timing, reuse and request population interact; the new traffic totals are observed facts, not proof of a particular L2 eviction/reissue mechanism.

The accepted BICG PS pair is CH 22,474,128 / DH 18,363,200 = 1.223868. It establishes DH faster than CH within this PS contract only; relative restoration K_PS remains PENDING without DH P0.

## Reproducibility

Core `9eedb3131937748f0492fa83aad37d3691118d70`; Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`; binary SHA256 `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`; core library SHA256 `694f05ce97fe3e1552d94803c2202d8d037769c61624cde5f6a832622ed60c56`.

Use `ACCEPTED_CELL_EVIDENCE.json` for every input SHA, cohort/UUID, config SHA, RESULT/DONE SHA, raw path/hash, strict metrics and verified164 archive receipt; `COUNTER_SOURCE_DEFINITIONS.json` for exact source SHA/line ranges; `CONFIGURATION_QUALIFICATION.json` for complete resolved-option contracts; `PENDING_CONSUMPTION.json` for missing cells. Analysis code: `build_review.py`. No raw or trace was opened, no model started, no controller/lease/Goal changed, no original registry altered.

Validation: 153 assertions passed. Historical English v0.23 remains unchanged.
