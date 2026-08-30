# ADR-002 — Treat Bottleneck Substitution as First-Class Evidence

## Context

Descriptor calibration and Line-MSHR sensitivity show that removing one L2 ceiling can expose another resource without producing material speedup.

## Decision

Use `BOTTLENECK_SUBSTITUTION` as a first-class architectural result when:

```text
an upstream L2 structural blocker materially decreases,
a downstream blocker/occupancy materially increases,
trace/source/config provenance is controlled,
and application performance changes little.
```

The conclusion is that the earlier resource was prematurely limiting visible concurrency, not that the later resource is necessarily the final performance cause.

## Required evidence

At minimum:

- exact demand/block counters for the relieved resource;
- downstream occupancy/block movement;
- cycles/instructions;
- temporal pressure where available;
- a causal headroom test for any claim that the newly exposed resource limits performance.

## Consequences

Mechanism selection can be guided by structural-resource lifetime/coupling even when speedup is small, but performance claims require additional causal evidence.
