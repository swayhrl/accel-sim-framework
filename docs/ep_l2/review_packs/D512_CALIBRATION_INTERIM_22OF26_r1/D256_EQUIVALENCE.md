# D256 backward-equivalence (B3)

Status: **PASS** (`D256_EQ_SCAN_PASS`).

For each of `vectorAdd_4M`, `spmv`, and `scan`, the generalized Core
`878f80869ce212e779df20b6421e4dc7f987825d` was configured back to D256 against
the formal C7e Framework/config anchor. The independently repeated comparison
found all seven required parsed artifacts byte-identical: `target_summary`,
`target_slice`, `target_kernel`, `target_bank`, `target_window`, `target_l1`,
and `target_dram`.

`D256_EQUIVALENCE_STATUS.csv` records exact cycles, instructions, L1 misses,
DRAM read/write issues, descriptor-pool blocking, terminal invariants, source
and runtime-config identities, and SHA-256 for each generalized artifact.
The formal reference is
`/workspace/worktrees/accel-sim-ep-l2-c7e/docs/ep_l2/target_baseline_results_final_850/B0-Banked/`;
the generalized evidence is
`/workspace/worktrees/accel-sim-ep-l2-d512/docs/ep_l2/calibration_results/d512_d256_equivalence/B0-Banked/`.
