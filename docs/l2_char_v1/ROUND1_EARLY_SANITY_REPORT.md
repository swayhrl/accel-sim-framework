# Round-1 Early Sanity Audit — PRE_FIX_DIAGNOSTIC

> All results in this report were produced by Core `c71c18a41b9a97eb3e62fce50827faf03b0fdbdc`, before the native pre-replenish DataPort/FillPort snapshot correction. They remain retained raw diagnostic evidence only and must not enter the formal Round-1 heatmap.

**Conclusion: `STOP_AND_FIX`**

Scope: 25 completed `COMPLETE_VALID` runs only. This is a preliminary, scheduling-biased audit; it does not select workloads or state paper conclusions.

## Run completeness

- Files, identity/provenance, 64-slice coverage, final terminal cycle/instruction matching, final 64 slice invariants, and 5K-window continuity were checked for every scoped run.
- `PASS` rows: 2; `WARN` rows: 0; `FAIL` rows: 23.
- Detailed per-run status and basic performance fields: `ROUND1_EARLY_SANITY_TABLE.tsv`.

## Histogram / aggregation

- Streamed final-snapshot HIST records verify exact weighted AVG/P50/P95/MAX and sample conservation for `reserved`, `mshr`, `merge_depth`, `missq`, and `missq_wb`.
- Exact global HIST validation is not emitted by v1 for `mshr_target`, ICNT→L2, L2→DRAM, DRAM→L2, L2→ICNT, or ROP. They remain explicitly `UNSUPPORTED_NO_PRODUCTION_HIST`; no missing metric was converted to zero.

## Blocking / causal semantics

- Every emitted blocker was checked per slice for `0 <= blocked <= eligible`, exact ratio/NA semantics, and request≤episode≤blocked for request-level blockers.
- Causal checks cross-reference DataPort/Fill busy, sampled MSHR/merge saturation, and queue maxima. Warnings identify only evidence that v1 cannot establish at its sampling granularity.

## Diversity (PRELIMINARY)

| resource | min | median | max | top-5 |
|---|---:|---:|---:|---|
| reserved_p95 | 0.0 | 4.0 | 65.0 | spmv, vectorAdd_4000000, vectorAdd_6000000, cfd_097k, fft |
| mshr_entry_p95 | 0.0 | 12.0 | 182.0 | spmv, vectorAdd_4000000, vectorAdd_6000000, cfd_097k, dwt2d |
| merge_depth_p95 | 0.0 | 1.0 | 4.0 | hotspot1, spmv, btree, dwt2d, vectorAdd_6000000 |
| missq_p95 | 0.0 | 0.0 | 32.0 | vectorAdd_6000000, vectorAdd_4000000, spmv, cfd_097k, dwt2d |
| fill_busy_ratio | 0.0 | 0.0 | 0.0 | vectorAdd_6000000, vectorAdd_4000000, transpose, spmv, sortingNetworks |
| wb_request_fraction | 0.0 | 0.0 | 0.6918229557389347 | mem_lat, sad, dwt2d, cfd_097k, ispass_lps |
| data_busy_ratio | 0.0 | 0.0 | 0.04008600000000001 | vectorAdd_4000000, dwt2d, vectorAdd_6000000, sad, hotspot1 |

Matrices: `round1_early_sanity/utilization_matrix.csv`, `blocking_matrix.csv`, `spatial_summary.csv`, and `temporal_summary.csv`. `mem_lat` is marked `reference`; V100/special workloads are marked `secondary`.

## Utilization vs blocking diagnostic correlations

| pair | Pearson r |
|---|---:|
| mshr_entry_p95__vs__block_mshr_new_ratio | 0.47239148461099817 |
| missq_p95__vs__block_missq_ratio | 0.8158422236683961 |
| fill_busy_ratio__vs__fill_ratio | NA |
| data_busy_ratio__vs__block_dataport_ratio | 0.09388715929772684 |

These correlations are diagnostic only; utilization and blocking are intentionally distinct metrics.

## Required follow-up / known unsupported observations

- **Production instrumentation defect**: the existing simulator reports nonzero DataPort and/or FillPort utilization for workloads where L2CHARV1 reports zero across every slice. Inspection shows L2CHAR samples after `baseline_cache::cycle()` has replenished port bandwidth. This loses one-cycle occupations and cannot be repaired from raw logs; fix the collector sampling point before any future campaign wave.
- **FAIL**: BlackScholes: production:fill_port_busy_sampling_mismatch
- **FAIL**: fastWalshTransform_11_19: production:data_port_busy_sampling_mismatch; production:fill_port_busy_sampling_mismatch
- **FAIL**: scalarProd_13920: production:data_port_busy_sampling_mismatch; production:fill_port_busy_sampling_mismatch
- **FAIL**: scalarProd_8192: production:data_port_busy_sampling_mismatch; production:fill_port_busy_sampling_mismatch
- **FAIL**: transpose: production:data_port_busy_sampling_mismatch; production:fill_port_busy_sampling_mismatch
- **FAIL**: vectorAdd_4000000: production:fill_port_busy_sampling_mismatch
- **FAIL**: vectorAdd_6000000: production:fill_port_busy_sampling_mismatch
- **FAIL**: ispass_bfs: production:data_port_busy_sampling_mismatch; production:fill_port_busy_sampling_mismatch
- **FAIL**: ispass_lps: production:fill_port_busy_sampling_mismatch
- **FAIL**: ispass_ray: production:data_port_busy_sampling_mismatch
- **FAIL**: fw_block: production:data_port_busy_sampling_mismatch
- **FAIL**: bfs: production:data_port_busy_sampling_mismatch
- **FAIL**: mri-q: production:data_port_busy_sampling_mismatch; production:fill_port_busy_sampling_mismatch
- **FAIL**: sad: production:fill_port_busy_sampling_mismatch
- **FAIL**: spmv: production:data_port_busy_sampling_mismatch; production:fill_port_busy_sampling_mismatch
- **FAIL**: btree: production:fill_port_busy_sampling_mismatch
- **FAIL**: cfd_097k: production:fill_port_busy_sampling_mismatch
- **FAIL**: dwt2d: production:fill_port_busy_sampling_mismatch
- **FAIL**: hotspot1: production:fill_port_busy_sampling_mismatch
- **FAIL**: lud: production:data_port_busy_sampling_mismatch; production:fill_port_busy_sampling_mismatch
- **FAIL**: nn: production:fill_port_busy_sampling_mismatch
- **FAIL**: fft: production:data_port_busy_sampling_mismatch; production:fill_port_busy_sampling_mismatch
- **FAIL**: gemm: production:data_port_busy_sampling_mismatch; production:fill_port_busy_sampling_mismatch
- Global exact HIST aggregation is not emitted for: draml2q, icntl2q, l2dramq, l2icntq, mshr_target, rop. Per-slice extrema/averages remain available, but global weighted P50/P95 cannot be validated from v1 raw records.
- **WARN**: fastWalshTransform_11_19: causal:respq_block_without_sampled_draml2q_full
- **WARN**: ispass_bfs: causal:mshr_merge_block_without_sampled_merge_limit_full; causal:respq_block_without_sampled_draml2q_full
- **WARN**: fw_block: causal:mshr_merge_block_without_sampled_merge_limit_full
- **WARN**: bfs: causal:mshr_merge_block_without_sampled_merge_limit_full
- **WARN**: spmv: causal:mshr_merge_block_without_sampled_merge_limit_full
- **WARN**: btree: causal:mshr_merge_block_without_sampled_merge_limit_full
- **WARN**: cfd_097k: causal:respq_block_without_sampled_draml2q_full
- **WARN**: gemm: causal:mshr_merge_block_without_sampled_merge_limit_full; causal:respq_block_without_sampled_draml2q_full

No frozen Core/Framework instrumentation was modified by this audit. Raw logs were stream-read only.
