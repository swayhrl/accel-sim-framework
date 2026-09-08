# C4 observability gaps

- Object-specific Weight/KV/PTE attribution by DRAM channel, bank, or row is
  not available; no such attribution is inferred from global native DRAM
  statistics.
- `L1D_ACCESS_ATTEMPT_WINDOW` is an observation-only access-attempt window,
  not an exact unique coalesced-transaction window.  It must not be used to
  derive exact transactions per memory instruction.
- Native global DRAM channel/bank/read/write/latency/row-locality values are
  reused existing GPGPU-Sim statistics and are retained in
  `NATIVE_DRAM_MEMORY_SYSTEM_STATS.tsv`.
- A counter difference alone is not a causal mechanism proof; the package
  separates measured facts from supported signals and unresolved gaps.
