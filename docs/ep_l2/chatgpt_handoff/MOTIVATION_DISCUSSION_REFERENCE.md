# EP-L2 Motivation Figures — Discussion Reference

## User goal

Create two paper-facing motivation figures that make the EP-L2 story easy to understand before the full mechanism is implemented:

1. a stacked distribution of L2 reuse distance by workload;
2. a stacked distribution of the primary L2 miss-admission blocking cause by workload.

The desired Figure-2 categories are analogous to a classic cache-bottleneck breakdown but must reflect the actual EP-L2 target model rather than relabel nonexistent structures.

## Research interpretation

### Reuse side

The intended question is not merely "does the L2 miss?" but whether reuse, when present, is concentrated at short distance or pushed far beyond realistic small auxiliary capacity.

A workload with both substantial reuse coverage and predominantly short reuse distance can motivate a victim-like retained-payload path.

A workload with low reuse coverage or mostly >1K distance is better interpreted as streaming/long-distance reuse, where increasing cache capacity alone is unlikely to be the most efficient response and concurrency/latency hiding may matter more.

### Blocking side

The intended question is: when a frontend demand miss cannot be admitted, which transient resource first prevents progress?

The four paper-facing classes are:

```text
Set/Assoc
MSHR/Metadata
MissQ/LowerQ
WB-path
```

Persistent descriptors are grouped under `MSHR/Metadata`, not the short lower queue.

The WB-path category is deliberately broader than a nonexistent baseline WBUF. It includes mandatory writeback-path ordering constraints and an explicitly defined finite shadow dirty-data WBUF.

## WBUF decision

The agreed shadow WBUF is a dirty writeback-data staging buffer.

```text
allocation:
  real dirty-victim data readout / WB packet creation

release:
  real successful lower-path / L2->DRAM acceptance
```

It does not remain allocated until final WB `set_done()`; WAD continues to represent the longer address-ordering lifetime.

One run simultaneously evaluates capacities 4/8/16.

This is valid for motivation pressure because all capacities observe the same real event stream. It is not a counterfactual timing/performance simulation. If a finite WBUF later becomes part of the functional architecture, its capacity must be simulated functionally for performance claims.

## Why one run can produce 4/8/16

The simulator records the real number/set of WB packets currently between WB creation and lower acceptance. For each dirty-victim admission opportunity, it can ask whether the same observed state would exceed C=4, C=8 or C=16 without changing any real request timing.

Thus the same run can emit three trace-projected capacity-pressure views.

## Main figure choice

Primary Figure 2 should use WBUF=8 as the reference unless later evidence changes the design choice.

WBUF=4 and WBUF=16 are retained as sensitivity data, preferably in a compact secondary plot/table rather than tripling the width of the main stacked bar figure.

## Key claim boundaries

Allowed from this stage:

- reuse locality distribution;
- short-vs-long reuse characterization;
- real/post-eviction reuse opportunity measurements;
- structural miss-admission blocking composition;
- trace-projected finite-WBUF capacity pressure;
- WBUF 4/8/16 sensitivity on the same observed stream.

Not established by this stage alone:

- victim-cache performance benefit;
- real WBUF4/8/16 speedup;
- end-to-end performance causality from one blocked-cycle category.

Later functional/headroom experiments are required for those stronger claims.