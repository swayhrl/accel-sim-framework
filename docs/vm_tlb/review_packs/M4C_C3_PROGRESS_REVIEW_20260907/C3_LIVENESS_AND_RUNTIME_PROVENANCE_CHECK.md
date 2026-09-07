# C3 liveness and runtime provenance check

Status: **PASS — runtime provenance and generic liveness only; not M4C PASS**.

This is a read-only observation. It did not signal, pause, restart, rebuild,
or attach a debugger to C3; it did not modify a config, object map, trace list,
scratch directory, binary, Core source, or any `RUN_MANIFEST.tsv`.

## Runtime provenance

`/proc/<pid>/maps` was queried for every `libcudart.so*` mapping of the active
simulator. The direct observations are versioned in
[C3_RUNTIME_PROVENANCE_SUPERSEDING_RECORD.tsv](C3_RUNTIME_PROVENANCE_SUPERSEDING_RECORD.tsv).

For active `prefill-generic` PID `2704010`, the only mapped library was the
Core local simulator runtime:

```
/workspace/worktrees/gpgpu-sim-vm-llm-m4b-integration/lib/gcc-11.4.0/cuda-11080/release/libcudart.so
SHA-256 fc07def22e239de9fec8a3dd83d237a607a82162cab2933d6707a37c0a208b0a
```

Its resolved realpath and SHA-256 equal the Core local runtime. They differ
from `/usr/local/cuda-11.8/lib64/libcudart.so` (resolved to CUDA
`libcudart.so.11.8.89`, SHA-256
`d0da41ae1323cf4eeb610123d69d7714124cfe5ebfcc4e45f02b910e51c57ee6`).
The same Core-local mapping was directly observed again after automatic
transition to active `prefill-paper` PID `3229570`.

Therefore the old host-path value in
`M4C_C3_INTERIM_CHECKPOINT/C3_PROVENANCE_SUPPLEMENT.tsv` is a
**provenance-recording error**: it identifies an installed host library rather
than the library actually mapped by the simulator. This check supersedes that
runtime-library attribution with direct read-only evidence. The historical
supplement and all formal manifests are intentionally left unchanged. This is
not a retroactive claim about a binary rebuild or a change to formal results.

## Liveness observation for the final generic kernel

| Observation | Time | PID / PPID / state | CPU time (user+system jiffies) | `%CPU` | RSS KiB | Generic `run.log` | Last started trace |
| --- | --- | --- | --- | --- | --- | --- | --- |
| First | `2026-09-07T10:49:42+08:00` | `2704010` / `2704009` / `R` | `4987763 + 14959 = 5002722` | `99.5` | `2217360` | `105556021` bytes; mtime `10:49:43.353027744 +0800` | `kernel-1458-ctx_0x55f2413c4de0.traceg.xz` |
| Second | `2026-09-07T11:02:02+08:00` | PID `2704010` exited | unavailable after normal exit | unavailable | unavailable | `105738760` bytes; mtime `10:54:33.903562549 +0800` | same terminal trace |

At the first observation the process was runnable and consumed a full CPU;
its CPU time was the liveness criterion. Before the second observation it
produced the final telemetry record, terminated with `simulator_exit_status=0`,
and the supervisor emitted `GATE_PASS arm=prefill-generic expected=692
completed=692 telemetry=692`. It then automatically launched
`prefill-paper`; at the second observation its PID `3229570` was `R`, at
`99.7%` CPU, with `41265 + 147 = 41412` CPU jiffies and `741376` KiB RSS.

The existing log provides per-completed-kernel progress only. It recorded
the final generic kernel block as `gpu_sim_cycle = 13399603`,
`gpu_sim_insn = 4391485440`, yielding totals `gpu_tot_sim_cycle = 45976701`
and `gpu_tot_sim_insn = 18452620427`. No nonintrusive, intra-kernel
cycle/instruction marker was available, so no such value was invented.

## Final-trace size comparison

The terminal generic trace is `48823572` compressed bytes. Across all 692
prefill generic compressed kernel traces the distribution was:

| count | min | p50 | p90 | p95 | p99 | max | terminal rank |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 692 | 788 | 42804 | 342764 | 1180572 | 1196904 | 48823572 | 692 / 692 (100th percentile) |

The final trace is the maximum, about `40.8×` p99. Its extended wall time is
therefore consistent with an exceptionally large final kernel, not evidence of
a deadlock. Generic has now passed and paper was allowed to start normally.
