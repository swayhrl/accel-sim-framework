# EP-L2 Experiment Roadmap

## Principle

EP-L2 uses a dependency graph, not chapter-by-chapter serial execution. Compute may run speculatively when source/config identities are frozen, while evidence promotion remains gated by reviewed provenance and acceptance criteria.

This roadmap describes scientific stages. Exact live status remains in `docs/ep_l2/coordination/PARALLEL_WORKBOARD.md`.

## Stage 0 — target-baseline correctness

Goal:

- establish a timing-correct B0-Legacy/B0-Banked comparison;
- remove artificial payload-bank staging effects;
- add exact L1/L2/lower/DRAM telemetry;
- establish reproducible source/config/trace provenance.

Primary output: frozen D256 Target Baseline 26-run at 850 MHz.

## Stage 1 — baseline resource calibration

### Descriptor calibration

Question:

> Is a 256-entry global descriptor pool an unnecessarily tight metadata ceiling that hides later L2 behavior?

Compare D256 vs D512 with all other modeled resources frozen.

Interpretation is based on both performance and pressure migration. D512 is not adopted merely because descriptor blocks fall, nor rejected merely because application cycles do not improve.

### L1 causality screen

Question:

> Are the large observed L1 queue/MSHR/bank retry counts a primary performance bottleneck that invalidates L2 conclusions?

Use metadata/queue headroom and bank headroom as sensitivity configurations while keeping L1 capacity/tag geometry/latency fixed.

### Line-MSHR causality probe

Question:

> When descriptor relief exposes exact Line-MSHR blocking, is the Line-MSHR capacity performance-causal or simply the next admission throttle?

Use a small Descriptor x Line-MSHR controlled matrix plus a negative control.

## Stage 2 — calibration convergence / primary baseline decision

Inputs:

```text
D256 formal baseline
D512 promoted calibration
L1 sensitivity results
Line-MSHR causal probe
hardware metadata cost estimates
Lane-D provenance-safe joint analysis
```

Decide:

- Descriptor 256 or 512 for the primary research baseline;
- whether L1 stays at the original target configuration;
- whether Line-MSHR remains 128 in the primary baseline;
- which resources are structural ceilings versus performance-causal ceilings;
- which opportunity mechanism should be prioritized.

Do not select a baseline because it creates a convenient mechanism story.

## Stage 3 — performance-headroom sensitivity

Purpose:

When an L2 mechanism or calibrated resource change clearly improves Level-1/2 L2 behavior but end-to-end speedup is weak, independently relax a measured downstream bottleneck and test whether the L2 improvement converts into performance.

Candidate downstream axes are selected from evidence, not guessed:

```text
DRAM scheduler headroom
L2->DRAM queue headroom
memory-bandwidth / DRAM-frequency headroom
potentially a combined headroom point only after single-axis results
```

This stage is a sensitivity study, not a primary-baseline redefinition.

See `PERFORMANCE_HEADROOM_PLAN.md`.

## Stage 4 — opportunity characterization

Before implementing a functional mechanism, quantify how often it could apply and what resource/lifetime it could save.

Examples:

### RO no-traditional-MSHR opportunity

Measure certified read-only pending lines/requests, potential Line-MSHR occupancy/lifetime avoided, tag lifetime, descriptor interaction, and downstream headroom.

### TVD / payload-lifetime opportunity

Measure dirty/pending payload lifetime, WAD overlap, payload reuse/eviction conflicts, and whether decoupled temporary data storage can reduce structural blocking.

### Unified payload opportunity

Measure simultaneous resident/bypass/pending demand, stranded quota, bank distribution, reuse distance, and whether static 1024/128 roles cause capacity denials or unnecessary evictions.

Opportunity results may justify or reject a mechanism before functional implementation.

## Stage 5 — functional mechanism implementation

Only after Stage 2/4 evidence defines the mechanism and expected benefit.

Each mechanism gets:

```text
source-level semantic design
invariants
capacity/timing budget
directed tests
observation/timing-neutral control where applicable
representative preflight
full target comparison
ablation
performance-headroom follow-up if needed
```

## Stage 6 — combined EP-L2 architecture

Combine only individually justified mechanisms. Do not bundle multiple unproven changes and attribute the result to EP-L2 as a whole.

Required final paper evidence should separate:

```text
baseline calibration
mechanism opportunity
individual mechanism effect
combined effect
storage/timing cost
L2 structural effect
end-to-end effect
performance-headroom sensitivity
```

## Current convergence logic

Conceptually:

```text
Formal D256
   + D512 descriptor calibration
   + L1 causality
   + Line-MSHR causality
          |
          v
   CALIBRATION ANALYSIS
          |
          v
   BASELINE DECISION
          |
          +------> performance-headroom sensitivity as needed
          |
          v
   opportunity characterization
          |
          v
   functional EP-L2 mechanisms
```
