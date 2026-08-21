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
