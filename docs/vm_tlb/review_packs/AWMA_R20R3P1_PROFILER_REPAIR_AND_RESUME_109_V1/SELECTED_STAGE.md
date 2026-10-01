# Stage selection from the single repaired B0 profile

The installed-toolchain canary qualified, and the one repaired scientific NSYS job produced a nonempty report plus explicit SQLite export. The four exact entry ranges (t128→t136→t144→t152) contain 568 CUDA graph child-kernel rows, all with graph-node IDs. Each entry has a source-matched pattern: 15 initialization nodes, 8–10 repetitions of the fixed 14-node `_solver_iteration` body, and one final qfrc recovery node. The per-iteration sequence agrees with pinned `solver.py`: 3 line-search kernels; counter reset; 3 constraint-update kernels; 5 incremental-gradient/factor kernels; solve-done; graph control. No row was assigned to an eligible stage by name alone without position/graph pattern verification.

Four-entry cumulative eligible-stage GPU kernel time (the frozen rule's metric):

| Stage | Cumulative GPU time |
| --- | ---: |
| `_update_gradient_incremental` including factor/search | 1024.802 µs |
| `_linesearch` | 663.618 µs |
| `_update_constraint` | 384.925 µs |

The top stage exceeds the second by 35.24% of the top; the ≤5% tie rule does not apply. **Selected: `_update_gradient_incremental`**. This is a profile-derived selection, not an expected-speedup choice. The parent `ELIGIBLE_STAGE_AUDIT.md` remains unchanged. `REPAIRED_B0_PROFILE_SUMMARY.tsv`, `REPAIRED_PROFILE_RECEIPT.json` and the node164 per-kernel manifest bind the ranking.

The selected stage is source-eligible but technically demanding. One bounded candidate is preregistered in `DIAGNOSTIC_CONTRACT.md`. If preserving the original within-world math requires broad solver redesign or the candidate fails its frozen correctness gates, STOP; do not substitute the second-ranked stage.
