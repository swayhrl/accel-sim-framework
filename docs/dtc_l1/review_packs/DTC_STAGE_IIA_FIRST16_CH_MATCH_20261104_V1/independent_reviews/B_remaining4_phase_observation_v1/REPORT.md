# Remaining four CH jobs: phase and conditional wall-time observations

**As of 2026-11-04 06:08:21 Asia/Shanghai.** All four original PID generations remain live, nonterminal and advancing. This packet reports runtime observations only; it does not predict final F128/F256 simulated cycles, count these jobs as accepted, or replace natural strict/archive/restore completion. No process, owner, controller, source, input, budget or manuscript was changed.

Two endpoint observations for each job are 127.83-128.11seconds apart (06:06:13 to06:08:21), comfortably above 55seconds. An intermediate 06:06:50capture is retained. Every observed progress row is checked against PID/start ticks/UUID/full input digest/ROI, along with monotonic retirement, freshness, unchanged canonical spec/intent/maps/binding SHA and fixed build identity for the closed histories. Full live resource/raw-prefix diagnostic captures remain on164 in private/ and are excluded from this manifest/publication.

## Trace-defined phase progress

| Job | PID/start ticks | App retired / contract | Mapped phase | Retired inside phase | Native elapsed h | Affinity CPU |
| --- | --- | --- | --- | --- | --- | --- |
| scan-F128 | 3495633/1048139893 | 1,400,578,545 / 1,963,460,720 | K21 _Z13uniformUpdateP5uint4Pj | 81.37% | 3.965 | [40] |
| scan-F256 | 3501039/1048216855 | 1,544,562,590 / 1,963,460,720 | K24 _Z13uniformUpdateP5uint4Pj | 95.41% | 3.751 | [48] |
| ATAX-F256 | 3521937/1049052693 | 22,001,248 / 145,666,048 | K1 _Z12atax_kernel1PfS_S_ | 30.82% | 1.430 | [49] |
| MVT-F256 | 3534697/1049386468 | 4,004,320 / 145,666,048 | K1 _Z11mvt_kernel1PfS_S_ | 5.61% | 0.502 | [34] |

Progress is whole-input cumulative GPU-thread retired instructions. The phase is an inference from ordered frozen trace bodies and cumulative instruction boundaries; it is not a live instruction pointer or an instrumented phase marker. App retirement fraction and within-phase retirement fraction are separate from elapsed-wall fraction. A progress emission at a boundary may span contexts. All current positions are inside their mapped phase.

scan has 33 declared kernels and 1,963,460,720instructions; this is not the two-kernel 145,666,048contract. Both scan jobs are in `uniformUpdate`, after the corresponding local scan and partial-sum phases. scan-F128 is near the end of K21, with 12 later kernels; F256 is near the end of K24, with 9 later kernels. Actual capture sequence is retained in the full qualification and historical phase table; it is not assumed to be 11 identical three-stage repetitions.

The fixed source candidate maps `scanExclusiveShared` to local exclusive scan (`scan.cu:49-153`), `scanExclusiveShared2` to scanning chunk totals (`156-181`), and `uniformUpdate` to applying scanned chunk offsets (`185-201`). This distinguishes different memory/reuse and dependency phases. The current mapping is trace-defined; no static reuse becomes a measured cache hit or MSHR merge.

ATAX and MVT currently map to K1 (71,380,992instructions); each K2 has 74,285,056. Candidate ATAX K1 computes tmp=A*x and K2 consumes tmp for A^T*tmp; MVT K1/K2 use opposite access directions and separate vectors, without asserting the same cross-kernel data dependence as ATAX. These fixed-source mappings are conditional: capture-source/ELF and native numerical input remain unbound. For lane-varying rows, K1 has row-strided matrix accesses; memory timing and simulator event cost may differ substantially from K2. This is a mapping rationale, not a proven dominant runtime bottleneck.

## Measured advancement and host conditions

| Job | Progress timestamp window s | Retired delta | Instructions / progress s | CPU / capture wall | Runqueue wait delta s | Read syscall / physical-read bytes delta | VmSwap KiB |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scan-F128 | 130.015 | 8,030,728 | 61767.5 | 98.60% | 0.572 | 3185 / 0 | 0 |
| scan-F256 | 130.025 | 7,525,181 | 57874.8 | 98.66% | 0.560 | 3086 / 0 | 0 |
| ATAX-F256 | 130.001 | 981,472 | 7549.7 | 91.28% | 2.530 | 0 / 0 | 0 |
| MVT-F256 | 130.001 | 318,048 | 2446.5 | 91.46% | 2.490 | 0 / 0 | 0 |

CPU observations cover about 128.1 seconds, while progress records span about 130 seconds because emission is approximately 10-second periodic. Do not treat the endpoints as identical. Both scan processes make ~13 MB of read syscalls during the window with 0 physical read_bytes/major faults; cached trace parsing or other cached reads are active and must not be described as no IO work. ATAX/MVT read syscalls/rchar do not advance. No process swaps, no major faults, no cgroup CPU-throttle increments and no memory high/max/OOM events are observed.

The four models have distinct singleton affinities 40,48,49,34. Their single-thread CPU usage is about 98.6%,98.7%,91.3%,91.5%; runqueue wait is only 0.56-2.53seconds. Cgroup memory is about 27.7 GiB under 256 GiB, memory/IO PSI avg10 is 0, and CPU full PSI avg10 is 0. Host IO PSI around 6% is shared host evidence and is not these processes' measured IO delay. Residual shared-cgroup swap 75 MB is unchanged, while each process VmSwap=0. No fresh evidence supports memory exhaustion, quota throttling or severe runnable contention as the current cause of a stalled job. Short-window evidence cannot exclude future host variation or all VM scheduling effects.

## Same-input, same-design closed history comparison

Only CH histories are used: original CH-P0 for all three programs, and this batch's closed CH-F128 for ATAX/MVT. No DH historical wall clock is substituted. Natural exit, exact input/ROI/generation, full progress termination, raw gzip/uncompressed SHA, actual kernel order/instruction boundaries and fixed Core/Framework/binary identity are independently checked. Historical per-process CPU/io/schedstat was not logged, so it remains missing; cgroup totals are not assigned to the old model.

| Current job | Closed CH history | Current elapsed h | History time to same retired position h | Historical residual h | History time for current retired slice s | Current slice s |
| --- | --- | --- | --- | --- | --- | --- |
| scan-F128 | CH_P0 | 3.965 | 5.605-5.608 | 2.710-2.713 | 260.1-280.1 | 130.0 |
| scan-F256 | CH_P0 | 3.751 | 6.280-6.283 | 2.035-2.038 | 190.0-210.0 | 130.0 |
| ATAX-F256 | CH_P0 | 1.430 | 1.795-1.797 | 0.953-0.956 | 60.0-80.0 | 130.0 |
| ATAX-F256 | CH_F128 | 1.430 | 1.533-1.536 | 0.827-0.830 | 70.0-90.0 | 130.0 |
| MVT-F256 | CH_P0 | 0.502 | 0.672-0.675 | 2.018-2.021 | 170.0-190.0 | 130.0 |
| MVT-F256 | CH_F128 | 0.502 | 0.522-0.525 | 1.645-1.648 | 130.0-150.0 | 130.0 |

All current cumulative elapsed positions are earlier than their matched histories; this is observational wall-time alignment under different host/configuration conditions, not a final scientific speedup. Locally, scan-F128 needs ~130 s for a retirement slice that P0 needed 260-280s, and scan-F256~130s versus P0 190-210s. MVT-F256 needs ~130 s versus closed F128 130-150s, consistent with its early K1 trajectory.

**ATAX local caveat:** cumulative F256 elapsed is about 7% ahead of closed F128 at 22,001,248 retired instructions, but its recent 981,472 instruction slice takes 130 s versus old F128 70-90 s (P0 60-80 s). A cumulative lead does not rule out a local slowdown. Its CPU remains busy with little runqueue wait and no reads; this observation does not isolate simulated-system behavior, cache timing, host frequency, or other per-cycle cost as the cause. Do not label an engineering failure or predict F256 cycle regression from it.

The history is strongly nonlinear. ATAX P0/F128 K1 host wall is 9301/8000 s and K2 only 601/507 s, though the kernels have similar instruction counts. MVT K1 is 9106/7300 s and K2 590/512 s. For scan P0, chunk-total kernels take 12-14 s, uniform updates 846-1013 s and local scans 1118-1445 s. Remaining wall time must therefore follow phase-position history rather than remaining app instructions times the present instruction rate. These historical costs include host/simulator work and do not themselves identify real-GPU critical paths.

## Conditional planning scenarios, not deadlines

The table below deliberately exposes the assumption: future residual wall cost is between 0.5 and 2 times the residual of a matched CH history. This factor is a planning sensitivity band, not a statistical confidence interval or empirically guaranteed bound. It allows later F256 memory-system/host behavior to differ. It does not multiply single-parameter scientific speedups or predict final cycles.

| Job | Residual if later CH history wall curve is comparable | 0.5x-2x conditional scenario h |
| --- | --- | --- |
| scan-F128 | CH_P0: 2.71h | 1.35-5.43 |
| scan-F256 | CH_P0: 2.03h | 1.02-4.08 |
| ATAX-F256 | CH_P0: 0.95h / CH_F128: 0.83h | 0.41-1.91 |
| MVT-F256 | CH_P0: 2.02h / CH_F128: 1.64h | 0.82-4.04 |

On equal-residual-history behavior the four-model batch is dominated by scan-F128 with about 2.7 hours remaining from 06:08 CST. Under the stated 0.5x-2x sensitivity assumption, the maximum of all four residuals is about 1.4-5.5 hours, roughly 07:30-11:40CST. This is conditional model wall time, not a promised finish window; archive/restore/strict-consumption/publication time is additional, and any phase divergence invalidates the estimate. No reliable calibrated confidence interval is available from this short observation. The batch cannot scientifically close until its slowest job naturally passes all terminal checks.

## Live-cycle and publication boundary

Retired instructions and CPU work advance directly. scan running raw contains prior completed-kernel/uArch diagnostic lines, while ATAX/MVT expose no useful live cycle rows at these samples. Such text is not a numeric, matched current-cycle time series, and no live-cycle speedup is computed. Fixed Framework invokes the retirement observer after cycle(); this supports continued model execution but supplies no cycle-rate measurement. No live counters or partial-kernel cycles enter the accepted performance tables.

CONSUMED_COUNTER_SCOPE_SOURCE_EVIDENCE.json pins Core9eedb3131937748f0492fa83aad37d3691118d70 / Framework02775fd795cde5aae1480d81cee6eb481d0a08f4 retirement/stat boundaries. CONSUMED_FIXED_SOURCE_PHASE_MAP.json cites Atlas47a097aad4406893a07f8d230e1e0a850609bf39, exact candidate source paths/commits/SHA and unresolved ELF limitations. MATCHED_CLOSED_CH_HISTORIES.json records each source RESULT, progress, resource, raw and exit SHA; FOUR_RUNTIME_COMPARISONS.json holds windows and computed deltas. All private full captures stay solely on164.

CPU_VALIDATION.json records 80 passing read-only checks. No simulator, GPU task, capture, signal, debugger, restart, admission change, additional registration or next 48 experiment was invoked. The existing four jobs and original single owner continue unchanged.
