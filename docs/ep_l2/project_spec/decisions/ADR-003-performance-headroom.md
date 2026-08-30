# ADR-003 — Performance Headroom Is a Sensitivity Study, Not a Baseline Rewrite

## Context

A mechanism may improve L2 structural behavior but show little speedup because the primary system is already limited by scheduler, lower queues, or memory bandwidth.

## Decision

Use controlled performance-headroom experiments only after a measured downstream constraint is identified.

Headroom changes are labeled sensitivity configurations, for example:

```text
scheduler queue headroom
L2->DRAM queue headroom
DRAM-frequency / bandwidth headroom
```

The primary L2 storage/timing and mechanism definition stay fixed.

## First-pass telemetry decision

Do not block the first headroom screen on new instrumentation. Existing C7e/Lane-D V3 telemetry is sufficient for initial causal sensitivity.

If a meaningful mechanism × headroom interaction appears, prioritize observation-only additions:

1. native per-channel physical DRAM bus utilization per 5K window;
2. cycle-based L2 admission blocking by reason;
3. transaction-stage lifetime/age distributions and useful per-window throughput only for selected paper-critical workloads.

## Rejected alternative

Do not enlarge all downstream resources together until a speedup appears. This would make the result impossible to attribute.

## Consequences

A headroom result can demonstrate that primary-system performance masks some L2-local benefit, but the headroom speedup must never be reported as the primary-system speedup.
