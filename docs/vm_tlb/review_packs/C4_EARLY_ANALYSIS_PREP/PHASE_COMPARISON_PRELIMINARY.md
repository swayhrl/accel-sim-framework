# Preliminary phase comparison

## OBSERVED_TERMINAL_FACT

Disabled and ideal controls are identical within each terminal ROI:

- Decode1: 10,938,651 cycles and 377.4279 IPC.
- Prefill: 36,328,725 cycles and 507.9348 IPC.

Generic is 2.999691× decode1 ideal cycles (125.8222 IPC) and 1.265574×
prefill ideal cycles (401.3472 IPC). Decode1-generic records 75,844,615
translation lookups, 69,483 L1-TLB misses, and 23,805 L2-TLB misses; terminal
prefill-generic records 93,933,006, 1,246,241, and 56,467 respectively.

## SUPPORTED_MECHANISM_SIGNAL

The ROIs have clearly different aggregate translation volumes and raw miss
counts. Prefill generic uses 22,783 translation-MSHR allocations and 33,684
merges with zero recorded MSHR-full events; decode1 generic uses 15,694
allocations, 8,111 merges, and 2,301,691 full events. This supports
phase-aware—not aggregate-only—C4 interpretation.

## UNRESOLVED_CAUSAL_GAP

These are different workload phases with different instruction counts and
profile shells. This package makes no normalized cross-phase IPC, footprint,
or object-interference conclusion. `prefill-paper` remains
`PREFILL_PAPER_PENDING` and is not an interim performance sample.
