# Live phase progress and conditional ETA — read-only observation

Snapshot: 2026-11-04T03:51:28.054989+08:00 (Asia/Shanghai). This is a point-in-time running-state observation, not accepted cycles/speedup or a substitute for an unfinished result. PID/start/UUID/input/ROI records are checked; progress is decoded only as a valid prefix of a still-open gzip stream. No running raw.log is read. No model/owner/registration/watcher change occurs.

## Main finding

ATAX and MVT are in their row-strided first kernel; BICG is in its row-strided second kernel. Those are the historically slow phases. Fresh advancing retirement and substantial native-process CPU time show ongoing model work; this observation gives no hang/deadlock evidence. It does not prove a particular runtime cache or queue bottleneck.

Original accepted CH-P0 has a large instruction/time skew: ATAX first kernel 49.0% instructions but 93.9% wall time (9301/9902s); MVT first kernel 49.0% instructions but 93.9% wall time (9106/9696s); BICG first kernel 51.0% instructions but only 6.5% wall time (554/8552s), while its second 49.0% instructions takes 93.5% wall time. Therefore 14% whole-program retirement in ATAX is not 14% of the remaining wall-time work; equally BICG 76% retirement does not imply only 24% wall time remains.

## Current phase and ETA

Intervals below are remaining model-host hours from this snapshot. They exclude archive/copy time and assume current resource/phase behavior is sufficiently comparable. They are broad planning scenarios, not statistical confidence intervals, deadlines or simulated hardware results. No uniform 8–12-hour estimate is used.

| Program / F | Elapsed h | Whole retired | Current kernel / within kernel | Remaining model-host h | Confidence / limitation |
|---|---:|---:|---|---|---|
| scan / F128 | 1.68 | 28.9% | K7 / 28.8% | 2.7–7.5 | Matched original CH-P0 ordered phase wall times plus current same-phase pace; future memory-stage/host assumptions remain broad |
| scan / F256 | 1.47 | 35.4% | K8 / 51.7% | 2.1–5.4 | Matched original CH-P0 ordered phase wall times plus current same-phase pace; future memory-stage/host assumptions remain broad |
| BICG / F128 | 1.68 | 75.9% | K2 / 50.7% | No reliable interval | Strong phase-rate drift across2/10/30-minute windows |
| BICG / F256 | 0.26 | 51.6% | K2 / 1.3% | No reliable interval | Only1.3%of the historically dominant slow second kernel completed; early-stage rate not a stable future predictor |
| 2DCONV / F128 | 1.53 | 70.8% | K1 / 70.8% | 0.4–1.0 | Single-kernel recent pace stable against30-minute window |
| ATAX / F128 | 1.51 | 14.4% | K1 / 29.4% | 1.2–6.4 | Matched original CH-P0 ordered phase wall times plus current same-phase pace; future memory-stage/host assumptions remain broad |
| MVT / F128 | 1.51 | 18.5% | K1 / 37.7% | No reliable interval | Strong phase-rate drift across2/10/30-minute windows |
| GEMM / F128 | 1.51 | 69.5% | K1 / 69.5% | 0.4–1.1 | Single-kernel recent pace stable against30-minute window |

BICG-F256 has just entered the slow second phase; only 1.3% of that phase is retired. Its early rate cannot support a reliable ETA. MVT-F128 and BICG-F128 still show large 2/10/30-minute rate changes, so no reliable interval is released for them. The exploratory numeric scenarios retained in the capture JSON are explicitly superseded by ETA_RELEASE_ASSESSMENT.json.

At the snapshot, all 8 live generation handles match, latest progress is approximately 2–7s old, and process CPU/elapsed ratios are about 0.91–0.99. Four unconsumed F256 points (2DCONV/ATAX/MVT/GEMM) have no start time; this report gives no batch-completion deadline. Admission HOLD is not a scientific failure.

## Why stages have different host cost

The frozen trace/source map distinguishes lane stride from loop stride. ATAX/MVT K1 and BICG K2 access A[q*4096+t], with 16KiB between adjacent lanes and 4B between loop iterations; opposite phases access A[t*4096+q], with 4B lane stride. Both use 16CTAs and serial per-thread reductions. This explains a source-level opportunity for very different traffic/latency/event work per retired instruction; it is not a measured cache-hit, MSHR-merge or queue-cause proof. Kernel names/order and instruction populations are frozen trace identities; inspected source remains a candidate with unresolved capture-source/ELF binding.

A simulator spends host CPU time on modeled cycle/event processing even when few instructions retire. Parsing, memory-service events, request/response bookkeeping, divergence and fixed-grid supply can change host work per instruction. Scan adds 9 short scans then 8 firstpass/totals/uniform triples: its small chunk-total stage can retire very few instructions and finish quickly, while bulk stages dominate time. A single whole-run retirement fraction or gpu_total_sim_rate therefore does not map linearly to remaining wall time.

## Reproducibility and limits

HISTORICAL_CLOSED_STAGE_TIMES.json covers 32 accepted original references with exact RESULT/rawSHA, per-kernel instruction populations and explicit cumulative printed host seconds. Stage durations come from differences of host-time prints. DH timings are retained as context but are not the primary CH pace predictor because the L1 mechanisms differ. SLOW_PHASE_HISTORICAL_SKEW.json contains the exact percentages above.

LIVE_PHASE_SNAPSHOT.json binds each running PID/start/UUID, latest authenticated progress record, point-in-time compressed-prefix SHA, instruction-derived kernel boundary, recent same-kernel rates and observational CPU/freshness. The full intermediate observed progress-record capture remains in private/ on 164 and is excluded from the publication manifest; no raw progress log should be committed.

The ETA calculation uses same-kernel 120/600/1800-second retirement rates, historical future-stage wall costs and a conservative envelope with phase-weighted historical elapsed calibration. It cannot know a new F configuration’s eventual performance, future admission, hardware/host load shifts or final archive wait. Missing/unstable estimates remain unavailable. No running cycles or speedups are generated, no model is signaled, and unfinished points remain scientifically pending.
