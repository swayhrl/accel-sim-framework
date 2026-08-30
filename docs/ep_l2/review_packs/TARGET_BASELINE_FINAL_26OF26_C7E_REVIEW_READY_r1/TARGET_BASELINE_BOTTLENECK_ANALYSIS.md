# Target-Baseline final bottleneck analysis

This is an observational classification based on exact blocker counters, not a causal model. `target_blocking_matrix.csv`, `target_resource_pressure.csv`, `target_l1_pressure.csv`, `target_lower_path.csv`, and `target_temporal_summary.csv` are the primary evidence.

- `scan`, `vectorAdd_4M`, `spmv`, `convolutionSeparable`, and both FWT inputs show observed descriptor-pool and/or lower-path pressure; the matrix retains the separate counters rather than collapsing them into generic descriptor/lower labels.
- No accepted row has line-MSHR-full blocking. Thus 128 line MSHRs are high-utilization in selected rows but not an observed full-blocker in this formal set.
- `btree` reaches high descriptor occupancy without a pool-full event, consistent with shared-pool pressure being workload-dependent rather than a fixed per-set merge fragmentation conclusion.
- `cfd_097k` is the only accepted Banked row with nonzero true-bank conflict operations. Its residual Banked cycle increase must be interpreted alongside those measured conflicts and wait cycles; aggregate waits can overlap with other stalls.
- `gemm` and `3mm` have zero measured true Banked conflicts and identical Legacy/Banked cycles, removing the pre-C6d artificial penalty from the formal evidence.
- Per-address-cap and WAD-full/hazard counters are nonzero for selected workloads, and scan has measured tag-way allocation blocks. Payload-capacity denial is zero across the accepted direct rows; payload-service denial occurs only in small counts and remains separate from capacity. These are measured producer fields, not inferred labels.
- Native physical DRAM data-bus utilization is provided only at the application final-complete 32-channel snapshot. The 5K physical-bus metric is `NOT_EMITTED`; lower admission normalization is retained separately and is not physical utilization.

No opportunity-mechanism benefit is estimated in this package.
