# EP-L2 Evidence and Claim Model

## Purpose

EP-L2 must distinguish a better L2 structure from a faster full system. This file defines the evidence required for each claim so future mechanism work does not overclaim or discard useful L2-local improvement merely because another subsystem becomes limiting.

## Claim tier 1 — structural improvement

A mechanism may claim **L2 structural improvement** when it demonstrably reduces a real L2 resource constraint under comparable L2 storage/timing and identical workload/trace semantics.

Preferred evidence is demand-normalized or cycle-based:

```text
block / need
full cycles / observed cycles
wait cycles
avg / p50 / p95 / max occupancy
near-full/full temporal-window fraction
longest high-average-window run
```

Examples:

```text
descriptor_pool_full_block / descriptor_need
line_mshr_full_block / line_mshr_need
tag_way_alloc_block / tag_way_alloc_need
per_address_cap_block / per_address_cap_check
payload capacity/service denial with matching demand denominator
```

A raw retry counter alone is not sufficient if one logical request can contribute multiple events.

## Claim tier 2 — service effectiveness

A mechanism may claim **better L2 service effectiveness** when structural relief also improves how useful work flows through the L2, even if total application cycles change little.

Useful evidence includes:

- lower L2-local wait/blocked cycles;
- lower transaction age/lifetime;
- higher useful admission/completion rate;
- more sustained useful concurrency without extra invalid/retry traffic;
- reduced high-pressure duration;
- a clear move from an artificial L2 ceiling to a physically plausible downstream ceiling.

If throughput/latency counters are not directly sampled, Tier-2 claims must remain conservative and use blocker/occupancy/traffic movement as supporting rather than definitive evidence.

## Claim tier 3 — end-to-end performance

A mechanism may claim **system performance improvement** when cycles/throughput improve under the primary frozen system configuration.

Report:

```text
cycles
speedup
instructions / trace identity
memory traffic movement
all relevant downstream pressure
```

Do not attribute speedup to the L2 mechanism solely from correlation; controlled deltas and invariants are still required.

## Claim tier 4 — performance headroom / masking

When Tier-1/2 improve but Tier-3 is weak, a controlled downstream-headroom experiment may test whether the L2 improvement is **masked by a later bottleneck**.

The correct claim is conditional:

> The mechanism reduces L2 structural blocking under the primary system. When the independently identified downstream constraint is relaxed, more of that L2-local improvement converts into end-to-end performance.

This is different from claiming that the primary system already gains the headroom speedup.

## Bottleneck substitution classification

Use this classification when an upstream blocker falls and a downstream blocker/occupancy rises while performance changes little:

```text
BOTTLENECK_SUBSTITUTION
```

Examples already observed during calibration include:

- descriptor pressure -> Line-MSHR / lower-path pressure;
- Line-MSHR pressure -> MissQ/WAD/lower-path pressure.

Bottleneck substitution is meaningful architecture evidence: it identifies which earlier resource was prematurely limiting visible concurrency. It is not itself a performance win.

## Required comparison bundle for every future EP-L2 mechanism

Every primary mechanism comparison should include, where applicable:

```text
A. cycles / instructions
B. exact L2 structural demand/block counters
C. descriptor + Line-MSHR occupancy and temporal pressure
D. tag / per-address / WAD / payload pressure
E. Banked logical/grant/conflict/wait metrics
F. L1 pressure controls
G. L2->DRAM queue / scheduler / ReturnQ pressure
H. DRAM traffic bytes and native physical bus utilization
I. 5K temporal distributions
J. terminal invariants and provenance
```

## Interpretation rules

### Structural relief + meaningful speedup

Strong mechanism evidence. Still report where pressure moved.

### Structural relief + no speedup + downstream pressure rises

Valid Tier-1 evidence plus bottleneck substitution. Consider performance-headroom sensitivity.

### Structural relief + no speedup + no meaningful service/pressure movement

Likely a bookkeeping/retry-pressure reduction with low architectural value. Mechanism should be deprioritized unless another benefit is demonstrated.

### No structural relief + speedup

Investigate whether the mechanism changed an unmeasured timing/traffic behavior. Do not accept the story until the cause is identified.

### Occupancy rises without exact blocking

Treat as headroom consumption, not a causal bottleneck.

## Baseline calibration rule

A baseline should be hardware-plausible and should avoid an obviously arbitrary cheap metadata ceiling that prematurely hides the behavior being studied. It should not be enlarged until a desired bottleneck appears.

Baseline selection therefore considers:

```text
hardware plausibility
storage/timing cost
pressure sensitivity
causal sensitivity
whether the resource masks the intended research question
```

not only benchmark speedup.
