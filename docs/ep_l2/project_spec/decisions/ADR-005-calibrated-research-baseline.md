# ADR-005 — Calibrated Research Baseline

Status: **ACCEPTED**

Date: 2026-08-30

## Context

Formal C7e used a 256-entry shared persistent request-descriptor pool. Promoted D512 calibration shows that D256 creates millions of descriptor-full admission events in several workloads. Increasing only descriptor capacity to 512 removes this structural ceiling at a bounded metadata cost but does not broadly improve application cycles; pressure moves to Line-MSHR, per-address, L1/lower/scheduler resources.

Lane-C L1 headroom produces no broad material (>5%) response. Lane-E removes 931,416 exact convolution Line-MSHR-full events with MSHR128->256 but improves cycles only ~0.38%, showing downstream-limited bottleneck substitution.

## Decision

Use the following **calibrated research baseline** for EP-L2 mechanism development/evaluation:

```text
Descriptor pool        512
Line MSHR              128
per-address cap         32
L1D                    64 KiB/core, 4 sets x 128 ways x 128 B
L1 banks               4
L1 latency             20 cycles
L1 MSHR                512
L1 merge cap           8
L1 MissQ               16
WAD                     128
payload physical budget 1152 x 128 B / slice
payload banks           4 x 288
bank service            one arbitrary op/bank/cycle
L2->DRAM queue          128
FR-FCFS scheduler       128/channel
ReturnQ                 192/channel
DRAM clock              850 MHz primary
```

The exact D512 calibration source family is the semantic parent for the next implementation stage unless a reviewed implementation branch supersedes it with an OFF-path-equivalent source.

## Rationale

D512 is chosen **not because it is faster** and not because it creates an MSHR bottleneck. It is chosen because a relatively cheap metadata resource should not prematurely truncate the concurrency/resource chain that EP-L2 mechanisms are intended to improve and measure.

The added D256->D512 metadata estimate (2–4 KiB/slice, 128–256 KiB/chip, about 1.39–2.78% of the frozen payload-byte budget) is accepted as plausibility context, not physical-area proof.

## Consequences

- Historical D256 formal evidence remains immutable and valid calibration provenance.
- Future mechanism comparisons hold the D512 base-resource configuration fixed unless a sensitivity experiment explicitly changes one dimension.
- Mechanism feature bits remain orthogonal to the base-resource configuration.
- All-features-OFF in a post-M1 implementation must reproduce this accepted research baseline.
- MSHR256 and L1 headroom configurations remain sensitivity evidence only.
- Primary 1GHz or downstream-headroom configurations are not baseline changes.
