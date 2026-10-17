# H0 residence anchors for r19 — no new condition data

| Workload | Mode | Mean staging-data lifetime (GPU cycles) | Max WAD lifetime across slices (GPU cycles) | Scheduler-full / eligible issue attempts |
|---|---|---:|---:|---:|
| convolutionSeparable | B16_BANKED | 74.960601 | 3278 | 0.440159762 |
| convolutionSeparable | U_WB16 | 133.451769 | 3500 | 0.444134234 |
| FWT_7_21 | B16_BANKED | 131.623624 | 3142 | 0.426291497 |
| FWT_7_21 | U_WB16 | 208.938612 | 3449 | 0.430077650 |

Derived from preserved H0 native slice evidence and hash-bound raw logs. Core7b8e6ac7 ep-l2-ft-cache.inc:271/299 defines B16 staging start at actual source read and U at in-place commit; :392 accumulates to actual lower acceptance. This excludes earlier B16 admission waiting and is not full WAD lifetime or total GPU stall. Longer U staging does not independently prove a capacity benefit or a unique downstream cause.

The scheduler denominator is the source-defined issue attempt counter (l2cache.cc:1588–1598). L2→DRAM-full and WBUF-full lack a matching emitted opportunity denominator; their fractions remain null. No normalized90% relief claim is made from these counts. Final32-channel cumulative byte totals cross-check all64 slices; kernel-boundary snapshots are not summed.
