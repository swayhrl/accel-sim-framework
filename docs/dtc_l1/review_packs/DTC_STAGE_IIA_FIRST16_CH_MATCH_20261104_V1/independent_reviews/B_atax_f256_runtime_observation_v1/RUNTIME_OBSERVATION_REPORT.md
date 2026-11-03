# ATAX CH-F256: two fresh runtime observations

**Finding:** this sample does not show an obvious host-throughput deterioration relative to closed CH-F128 at the same early K1 instruction position. Whole-application retirement is a misleading wall-time proxy here. This does not predict F256 final simulator cycles, establish its performance, classify an engineering failure, or replace strict completion.

## Identity and scope

PID3521937/start1049052693, UUID3b949083-a0f8-4778-92f1-d940c66acfe6, full input eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950 and ROI5ba85e56ae33e604c38407d5d8641078cb0a1b06aaaa9928cc0de4c61d94f442 match native intent/spec/maps and every observed progress record. Affinity remains CPU49, one native model thread.

Samples at 2026-11-04 05:27:53 and 05:29:18 Asia/Shanghai are 85.38 seconds apart, satisfying the requested >=55 seconds. Both are fresh, generation-matched, SIMULATE/end=NONE observations, with no DONE/RESULT at the sampled times. Only bounded diagnostic metadata is public; full last resource objects stay in private/ on 164 and must not be committed as live logs.

| Observation | Sample1 | Sample2 |
|---|---:|---:|
| Native elapsed seconds | 2718.18 | 2803.60 |
| App-cumulative retired instructions | 6,046,496 | 6,236,608 |
| Native user+system CPU seconds | 2486.58 | 2564.71 |
| Progress freshness seconds | 7.36 | 2.78 |

The second retired count is4.28% of app145666048 instructions but8.74% of K1's71380992 instructions. K1 is the row-strided phase; K2 has74285056 instructions and consumes tmp from K1. The observer counter is whole-input cumulative, not a direct per-kernel or wall-time fraction. K1 starts at0 so this particular position can be mapped without subtracting an earlier kernel.

## Matched historical positions, not P0 whole-run ETA

| Closed history | Time to second sample retired position | Final native elapsed | Historical later time after matched position | Affinity |
|---|---:|---:|---:|---|
| CH_P0 | 3410.55?3420.55s | 9902.35s | 6481.80s | [230] |
| CH_F128 | 2850.56?2860.56s | 8508.16s | 5647.60s | [47] |

Current F256 elapsed2803.60s is approximately the same as, slightly ahead of, closed F128 at the matched retired position2850.56?2860.56s; P0 took3410.55?3420.55s. Sampling has roughly10-second quantization and host/resource conditions differ, so this is an observational alignment, not a formal speedup. The initial claim that F256 must already be much slower than F128 is unsupported by this position-matched evidence.

The historical curve is strongly nonlinear: F128 reaches about6.24 million retired instructions after2861s but finishes the entire145.67million-instruction replay after8508s. Its first8million take3681s,20million5341s,40million6761s and60million7501s. Extending the current~2100inst/s across all remaining instructions would therefore grossly overestimate if the later curve behaves similarly. This empirical nonuniformity is not proof of a particular cache-warmup mechanism.

## CPU, IO, pressure and cycle observability

The 85.42-second CPU observation window contains+78.13s user+system CPU (91.46% of one core). Authenticated progress advances+190,112instructions over its own90.001-second timestamp window, about2112.3inst/s. The two windows differ because progress is emitted at about10-second cadence; do not divide these deltas as if their endpoints were identical.

Process read syscall count/rchar/read_bytes do not increase in the window; writes increase only1299characters/4096bytes. Runqueue wait increases1.651s, much smaller than CPU runtime. Cgroup CPU-throttle deltas are0 and quota is384core equivalents; affinity is intentionally one CPU. The samples do not support active trace-read IO or quota throttling as the dominant current slowdown. Host IO PSI around5%belongs to the host and is not this process's measured IO delay.

Process VmSwap=0; RSS is about1.324GiB. Cgroup memory is about34.65GiB under256GiB, host available about215.6GiB, no new cgroup OOM/high/max events, and sampled memory pressure0. Cgroup residual swap75MB is unchanged shared state, not evidence that this model is swapping. Scaling frequency snapshots stay about3.10GHz; cpuinfo_cur_freq reports2.25GHz in the same VM, so neither is a calibrated historical frequency measurement.

Closed F128 at the matched position had the same observed process-tree RSS1421869056bytes, memory/IO pressure0and no CPU throttle. Historical P0 had more cgroup memory use but still passed resource checks. Historical resource streams do not provide per-process CPU/io/schedstat series; those values remain unavailable and are not synthesized from cgroup totals.

There is direct continued retired-instruction and CPU-work evidence. Quantitative live GPU-cycle rate is not available in the emitted files: current raw diagnostics contain no usable live cycle line, and the perf gzip currently exposes only its header, no complete numeric data row. Missing cycle data is not zero cycles. Fixed Framework code observes SIMULATE retirement after cycle(), so advancement is source-bound evidence that model cycles continue to process, but no numerical cycle delta or live-cycle speedup is manufactured. No debugger/ptrace/signal was used.

## Conditional ETA and limits

The current run is consistent with the historically slow, nonlinear early K1 region. If its later trajectory remains comparable to same-input closed CH-F128, matched-position calibration gives roughly1.5 hours of historical remaining model wall time; a deliberately wide planning scenario is about1?3 additional hours from the second sample. This is conditional, not a final deadline or a claim about F256 scientific performance. Archive time, future host/frequency/IO changes and different later F256 memory-system behavior are excluded; re-estimate if the matched curve diverges.

We cannot reliably forecast final F256 cycles or rule out a later modeled-system performance regression. Host throughput, simulated GPU cycle cost, retired-instruction fraction and application dependency progress are different quantities. Continue to require natural strict termination. No engineering-failure label, intervention, restart, source/owner/input/budget change or additional model was made.

## Evidence

SAMPLE_01/02.json bind PID/start/input/ROI, compressed-prefix hashes, bounded resource/CPU/IO/affinity observations and last progress records. RUNTIME_COMPARISON.json keeps exact independent windows/deltas and observational cycle availability. CLOSED_MATCHED_PHASE_HISTORY.json binds both natural closed histories, raw/progress/resource SHA, matched instruction brackets and historical resource projections. COUNTER_SCOPE_SOURCE_EVIDENCE.json pins fixed Core9eed/FW02775 boundary definitions. Scripts live solely in this new true164 directory; private/ is excluded from publication manifest.
