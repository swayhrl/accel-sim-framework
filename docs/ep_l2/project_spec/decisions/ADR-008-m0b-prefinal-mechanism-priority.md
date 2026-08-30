# ADR-008 — Mechanism Priority After M0b Pre-Final Evidence

Status: **accepted for next-stage preparation; final M0b scan delta pending**.

## Context

M0b pre-final evidence now directly distinguishes three previously competing mechanism families.

## Decision

### 1. RO / pending-state is the only active first-mechanism candidate

Current workload evidence shows a large and long-lived population of ordinary tracked read-like Line-MSHR allocations, but all remain `UNCERTIFIED_CANDIDATE_ONLY` because source semantics do not yet prove a safe eligibility predicate.

Proceed to a dedicated certification/state-minimality stage before any functional M3 implementation.

### 2. Retire the specific early-resident-payload TVD motivation

The current model does not retain the old dirty-victim resident payload handle until WAD `set_done`; observed old handles are already non-live after replacement/reassignment.

Therefore do not implement TVD merely to free that old resident payload earlier.

This does not prohibit future WAD/victim mechanisms aimed at other state or scheduling bottlenecks.

### 3. Defer standalone Unified/shared payload

The current production path has zero real non-resident payload allocations across the completed M0b set. Dormant bypass capacity is not demand.

Do not implement standalone capacity sharing until a real non-resident/transient payload consumer exists.

## Consequence

Near-term sequence becomes:

```text
M0b final scan delta
      ||
M3A RO certification + pending-state minimality design
      |
      v
choose safest evidence-backed M3 v1 boundary
      |
      v
functional M3 implementation / ablation
```

M2 shared payload may re-enter after M3 or another mechanism creates a real transient/non-resident payload role.
