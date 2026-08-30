# Validation summary

- Accepted direct rows: 26/26; unique `(workload, variant)` keys: 26.
- Runtime SHA uniformity: Core `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`, Framework `f08d2ce857972fad73c4e1ab7162ba94c6336507`.
- Runtime config uniformity: `85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d`.
- Parser stderr is empty, required artifacts are nonempty, and terminal/payload invariants pass for every accepted row.
- Lane-D V3 (`cb83606eb8640382b7c1932d8981b70608d9d130`) analyzed 26 records; all have `PASS_RUNTIME_CONFIG_BOUND`, `PASS_FULL_WINDOWS_ONLY`, exact L2/DRAM time-group alignment, and `PASS_FINAL_COMPLETE_CHANNEL_SNAPSHOT`.
- Excluded diagnostic records: 2 (the duplicate-write 3mm Legacy and Banked paths only); neither can enter direct `B0-*/*` discovery.
- Errors recorded by the packaging validator: 0.
