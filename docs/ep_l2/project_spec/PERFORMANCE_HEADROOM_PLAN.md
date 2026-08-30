# EP-L2 Performance Headroom Plan

## Goal

Performance-headroom experiments answer a specific question:

> If an EP-L2 change demonstrably removes an L2 structural ceiling but application speedup is small, is the L2 improvement being masked by a separately measured downstream bottleneck?

This is a causal sensitivity study. It is not permission to enlarge every downstream resource until a speedup appears.

## Do we need new sampling before the first headroom screen?

**No broad new simulator telemetry is required for the first headroom screen.**

The current C7e + Lane-D V3 evidence is already sufficient to launch a conservative first pass because it includes:

```text
exact descriptor / Line-MSHR / tag / per-address demand+block counters
WAD / payload pressure
Banked logical/grant/conflict/wait counters
L1 pressure counters
L2->DRAM queue occupancy/full blocking
DRAM scheduler occupancy/full-cycle/causal-block counters
ReturnQ / DRAM->L2 return blocking
successful DRAM read/write bytes
application-level native physical DRAM bus utilization
64-slice / 32-channel 5K temporal windows
traffic-conditioned channel imbalance
terminal invariants and exact provenance
```

These allow a first experiment to determine whether an L2-local improvement persists while downstream pressure is independently relaxed.

## Recommended first-pass headroom axes

Choose axes only where the frozen baseline/mechanism shows measurable pressure.

### H0 — primary system

The reviewed primary configuration. No headroom changes.

### H-SCHED — scheduler headroom

Example sensitivity point:

```text
FR-FCFS scheduler queue 128 -> 256
```

All L2 resources, L1, traces, and DRAM clock remain fixed.

Use when scheduler occupancy/full/causal-block evidence is significant.

### H-L2D — L2->DRAM queue headroom

Example:

```text
L2->DRAM queue 128 -> 256
```

Use only where L2->DRAM-full is measurable. This tests whether the L2 mechanism is hidden by immediate downstream buffering/backpressure.

### H-BW — memory-bandwidth headroom

Example sensitivity point:

```text
DRAM clock 850 MHz -> 1 GHz
```

This must be labeled **HEADROOM/SENSITIVITY**, not a new primary baseline. The L2 timing/storage remains unchanged.

Use primarily for workloads with high native physical DRAM bus utilization or strong scheduler/lower-path pressure.

### H-COMBO — combined downstream headroom

Do not start here. Use only after single-axis experiments identify two independent downstream constraints. A combined point can then estimate upper-bound conversion of L2-local relief into performance.

## Recommended workload selection

First tier should focus on workloads with strong L2-local relief and different downstream regimes, for example:

```text
convolutionSeparable  descriptor relief -> exact Line-MSHR full -> downstream-limited
scan                  extreme descriptor + lower/scheduler pressure
vectorAdd_4M          sustained descriptor/lower/scheduler pressure, high DRAM utilization
spmv                  descriptor relief + per-address pressure, moderate/high DRAM utilization
FWT_7_21              burstier descriptor/lower pressure
sad or btree          low-pressure control
```

Do not run the full suite until a small matrix shows a scientifically useful interaction.

## Headroom experiment structure

For one proposed L2 mechanism M and one downstream headroom H:

```text
                         primary downstream      headroom downstream
baseline L2                  B,H0                    B,H
mechanism L2                 M,H0                    M,H
```

Interpret both interaction dimensions:

```text
mechanism effect at H0
mechanism effect at H
headroom effect on baseline
headroom effect on mechanism
```

The most useful case is:

```text
M reduces L2 structural blocking at H0
M has little speedup at H0
H independently reduces the measured downstream pressure
M has larger speedup under H
```

This supports downstream masking.

If both baseline and mechanism gain equally from H, the headroom axis is important system-wide but does not specifically validate the L2 mechanism.

## Minimum metrics for every headroom comparison

### L2-local

```text
descriptor need/block/occupancy
Line-MSHR need/block/occupancy
tag-way need/block
per-address cap check/block
WAD/payload pressure
bank conflict/wait
```

### Service/downstream

```text
L2->DRAM full/occupancy
scheduler occupancy/full cycles/causal block
ReturnQ/return-path pressure
DRAM read/write bytes
native DRAM data-bus utilization
channel imbalance
5K temporal distributions
```

### System

```text
cycles
instructions
speedup
terminal invariants
```

## Recommended targeted telemetry extensions for paper-grade headroom analysis

These are **recommended but not required before the first sensitivity screen**. Add them observation-only only if the first-pass results make a headroom story important.

### P1 — per-channel physical DRAM bus utilization in 5K windows

Current 5K C7e `bandwidth_util` is a lower-admission byte-rate normalization, not physical bus utilization. Lane-D V3 recovers native physical bus utilization only from the final complete application snapshot.

For a strong temporal headroom argument, add native per-channel window counters based on actual issued data-bus work, for example:

```text
physical_data_bus_busy_cycles
physical_data_bus_capacity_cycles
physical_data_bus_util
```

per channel / 5K DRAM window.

This directly answers whether short burst phases hit real memory-bus capacity even when application-average utilization is moderate.

### P2 — L2 admission-blocked cycles by reason

Add cycle-based, non-retry-counting stall accounting such as:

```text
admission_blocked_any_cycles
admission_blocked_descriptor_cycles
admission_blocked_line_mshr_cycles
admission_blocked_tag_cycles
admission_blocked_per_address_cycles
admission_blocked_payload_cycles
admission_blocked_lowerq_cycles
```

Prefer independent reason bits plus a clearly defined primary/overlap policy. Do not turn retry events into pseudo-cycle counts.

This is valuable because it lets the paper say not only that `N` retry/block events disappeared, but that the L2 spent fewer cycles unable to admit useful work.

### P3 — transaction lifetime / stage-age distributions

For selected sensitive workloads only, sample aggregate distributions for:

```text
Line-MSHR lifetime from allocation -> final requester response enqueue
Descriptor lifetime
L2->DRAM queue wait
DRAM scheduler wait
DRAM service/return wait
```

Report avg/p50/p95/max and preferably 5K-window average/p95 for phase behavior.

This is the strongest way to show where latency/lifetime goes after a structural blocker is removed, but it is more instrumentation than P1/P2 and should be added only when needed.

### P4 — useful L2 throughput per window

Optional counters:

```text
new line misses admitted
merged requests admitted
requests submitted to DRAM
fill/return completions
requester responses enqueued
```

per slice / 5K window.

This supports a Tier-2 service-effectiveness claim by showing that lower blocking converts into more useful work, not merely different retry accounting.

## Recommended instrumentation order

Do not add P1-P4 all at once.

```text
First headroom screen using existing C7e/V3 telemetry
        |
        +-- no useful interaction --> no extra telemetry needed
        |
        +-- clear L2 relief + headroom interaction
                 |
                 +--> add P1 + P2 first
                 |
                 +--> add P3/P4 only for selected paper-critical workloads
```

Any added producer telemetry must pass observation/timing neutrality at the original configuration and preserve existing C7e semantics.

## Claim wording

### Allowed when primary system speedup is weak

> EP-L2 reduces L2 structural admission blocking and exposes downstream pressure that was previously hidden by the L2 resource ceiling.

### Allowed if headroom interaction is measured

> Under independently relaxed downstream pressure, a larger fraction of the L2-local structural improvement converts into end-to-end speedup, showing that the primary configuration masks part of the mechanism's performance headroom.

### Not allowed

> The mechanism provides the headroom-configuration speedup on the primary system.

or

> Removing a blocker necessarily improves performance.
