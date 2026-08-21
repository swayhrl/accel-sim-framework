# C2P target-port contention diagnostic

This diagnostic explains an observed C2P performance result; it is not a
Figure 10--14 architectural comparison point.

## Counters

The C2P model emits four cycle counters for every run:

| Counter | Meaning |
| --- | --- |
| `c2p_target_probe_port_busy_cycles` | A nonempty target-probe FIFO could not start its head probe because the target L1 shared data port was busy. One target contributes at most once per cycle. |
| `c2p_target_probe_queue_wait_cycles` | Sum, per C2P probe, of FIFO residence from enqueue through service or timeout. It includes both queueing behind prior probes and target-port blockage. |
| `c2p_target_probe_queue_full_cycles` | Candidate issue cycles that observed a full target FIFO and a busy target port. |
| `c2p_requester_fill_wait_cycles` | Remote responses whose fixed return latency had elapsed but whose requester L1 fill port was still unavailable. |

They are observation-only: canonical C2P state transitions and all timing
remain unchanged when the default configuration is used.

## Counterfactual control

`configs/c2p-cache/c2p-target-port-bypass.config` sets
`-c2p_cache_diagnostic_target_port_bypass 1`.  It is deliberately a separate
overlay.  It removes only C2P probes' reservation of the target L1 data port:

- unchanged: Snapshot Matrix lookup, candidate order, target tag latency,
  remote-return latency, requester fill-port contention, and non-C2P traffic;
- removed: target-probe FIFO and target data-port contention for C2P probes.

The control is therefore a bound on the same candidate stream without target
port contention.  It must not be used in aggregate paper figures or compared
as a new architectural scheme.

## Required use

Run the canonical C2P configuration and this overlay for SGEMM, Btree, and
NN.  Interpret the result with probe counts, Snapshot classifications, L2
accesses, and IPC together.  A recovery only in the bypass control supports a
target-port contention explanation; no recovery requires further examination
of candidate quality, return/fill pressure, or transaction timing.

## Completed v1 evidence

`hw_run/c2p-target-port-diagnostic-v1-20260821/target_port_bypass.md` is the
strict, raw-`run.out` result.  It passed configuration and
`remote_hits == l2_requests_avoided` checks for all three cases.

| Case | Normal cycles | Bypass cycles | Bypass IPC / normal | Interpretation |
| --- | ---: | ---: | ---: | --- |
| SGEMM | 435,411 | 430,619 | 1.0111x | Target contention is the dominant part of the C2P/baseline gap, but bypass remains 0.19% slower than the 429,816-cycle baseline. |
| Btree | 229,052 | 225,845 | 1.0142x | Contention suppresses remote hits and L2 avoidance, while the existing finite path is already faster than baseline. |
| NN | 7,224 | 7,224 | 1.0000x | Expected negative control: no candidate or remote reuse exists to benefit. |

This control is an explanatory upper bound only.  It is intentionally excluded
from paper Figure 10--14 aggregates and must not be presented as an additional
architectural proposal.
