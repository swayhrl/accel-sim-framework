# Observability gaps and deferred work

- Exact attribution of paper's extra decode1 cycles to request class, L2
  victim/replacement, DRAM channel/bank/row, or source instruction remains a
  `C4_OBSERVABILITY_GAP` in this early pass.
- Object-specific Weight/KV/PTE × channel/bank/row attribution is unavailable.
  Native global memory data exists but cannot supply that object split.
- Large per-kernel/window exports are present externally but deliberately not
  full-scanned while the only formal simulator workload is active. Final C4
  will perform the required aggregation after C3 terminal.
- `L1D_ACCESS_ATTEMPT_WINDOW` remains an access-attempt window, not an exact
  unique-coalesced-transaction window; no exact transaction/instruction ratio
  is inferred here.
- The 7709376→a7c0759 Framework provenance split is preserved per arm. Core,
  binary, runtime, and accepted trace-list anchors are unchanged.
