# Validation summary

## Frozen provenance

- Core: `2a6a31591bc42023e5997cca969e4b672efe0405`
- Framework runtime: `02f36816f60afcff55e910cdef2b60937e691cdc`
- Branch: `hrl/ep-l2-motivation-v0`
- Simulator/configuration source: isolated Motivation worktrees only.

## Stage 4 — `MOTIVATION_INSTRUMENTATION_PREFLIGHT_PASS`

- Release build: PASS.
- Permanent directed contract and parser regressions: PASS (reuse boundaries
  through 1025, epoch/slice reset, clean/dirty eviction, packet/same-address
  WB identity, simultaneous 4/8/16, read/write and combined exclusive
  blockers, streaming and cumulative terminal selection, terminal fail-close).
- Corrected OFF/ON pairs (`vectorAdd_4M`, `convolutionSeparable`, `sad`):
  exact cycles, instructions, B0, M0a, L1, DRAM and terminal real-resource
  invariants; host wall/RSS recorded in their raw-run time logs.
- Motivation-ON pilot rows (`vectorAdd_4M`, `convolutionSeparable`, `spmv`,
  `sad`): 64 final application slices, parser/closure pass, and terminal
  packet-identity shadow WBUF state closed.

## Stage 5 / Stage 6

The machine-generated `WORKLOAD_STATUS.csv`, `RAW_LOG_INDEX.tsv`, aggregate
CSVs and figures bind the completed broad 10/10 set to the same pair. Every
row is revalidated during Stage-6 aggregation for manifest identity, WBUF
closure, reuse closure, and exclusive WBUF4/8/16 blocker closure.
