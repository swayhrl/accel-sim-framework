# Scope, limitations, and forbidden claims

This is a bounded simulator-model study.  It can establish only whether the
pre-registered queue-chain and DRAM-service counterfactuals recover execution
headroom under the frozen identity and default DTC lower cap of 8192.

It must not be used to claim any of the following:

- a unique global GPU bottleneck;
- a physical-GPU frequency or bandwidth prediction;
- the absence of other downstream bottlenecks;
- a result for workloads beyond the registered BICG rows and, only when its
  gate closes, the at-most-two registered GESUMMV configurations;
- a result for changed DTC admission semantics, Core, runtime, trace, L2
  MSHRs, NoC, ROP, DRAM mapping/channel count, or unregistered queues/clocks.

The all-headroom `20 MiB` L2 point is not a new capacity sweep.  It is the
single pre-registered conditional ceiling paired with the full F queue-chain
and DRAM-service configuration.  It may distinguish residual capacity effects
from the already measured queue-chain/service effects only for BICG.

All attempts, including any future non-scientific failure, retain immutable
UUID-specific directories.  A non-PASS row is never silently replaced or
promoted.
