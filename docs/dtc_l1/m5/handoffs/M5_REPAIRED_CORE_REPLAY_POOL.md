# M5 repaired-Core replay-pool admission

Status: **ACTIVE acquisition; no stage PASS claim**.

Timestamp: 2026-09-06T10:33+08:00

## Measured admission basis

| Item | Observation | Decision relevance |
| --- | --- | --- |
| Host topology | 512 logical CPUs; two NUMA nodes | independent simulations use distinct non-SMT sibling CPUs |
| Existing pool | 15 live M5 simulators, including four stats-light A/B diagnostics | all have isolated output namespaces |
| Per-job RSS | light 0.55--3.3 GiB; heavy approximately 8.9 GiB | use a mixed workload/mode pool |
| MemAvailable | approximately 110 GiB before dispatch; approximately 101 GiB after | permits three additional light BICG jobs with substantial headroom |
| Swap / vmstat | swap occupied historically, `si=0`, `so=0` | no current swap pressure; do not treat occupancy as usable capacity |
| CPU / I/O | each worker near one CPU; iowait approximately 5% | no CPU or trace-store saturation observed |
| Output filesystem | approximately 32 GiB free | current simulation outputs are MB-scale; continue low-frequency space checks |

## Active limit and dispatch

Set the current dynamic **N_safe = 18** workers, with no more than five
approximately 9-GiB heavy workers.  The pre-dispatch 15 jobs include four
stats-light A/B diagnostics and five known-heavy ATAX/MVT/recovery rows.  The
three added workers are BICG Base/IO/OO, historically lighter than the heavy
rows.  At 18 workers MemAvailable remained approximately 101 GiB and swap I/O
remained zero; do not dispatch a nineteenth worker without a new calibration.
This is a host scheduling choice only: configs, traces, payloads and simulator
semantics are unchanged.

The BICG triplet uses its one immutable bundle, the repaired Core
`15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`, Framework
`dc7836c484544b78d143837bbbb40ecbabb15aee`, the frozen ratio-zero 80-SM/
cap-10240 configs, and distinct output directories.  Its purpose is to
re-establish T2 under the post-repair identity; the older BICG T2 remains a
diagnostic anchor only.

Recalibrate before any further dispatch or if MemAvailable, swap activity,
iowait, trace-store throughput or output-space headroom becomes adverse.
