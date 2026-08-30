# Telemetry completeness and semantic discipline

The accepted 26 runs provide all C7e parsed artifacts (`target_summary`, `target_slice`, `target_kernel`, `target_bank`, `target_window`, `target_l1`, and `target_dram`). `FORMAL_PROVENANCE_AUDIT.csv` records the artifact and invariant checks per run.

Lane-D V3 output in `analysis/lane_d_v3/` supplies the corrected analysis semantics:

- `bandwidth_util` is exposed only as `lower_admission_byte_rate_norm`; it is **not** named or interpreted as physical bandwidth.
- `NATIVE_DRAM_BANDWIDTH.csv` derives application-level physical data-bus utilization from the final complete native 32-channel snapshot. It reports weighted mean, p50/p95/max, command sum, and a pass/fail snapshot status.
- `TEMPORAL_CARDINALITY_AUDIT.csv` proves completed-only 5K windows with 64 L2 slices and 32 DRAM channels, including exact time-group alignment.
- `TEMPORAL_DISTRIBUTIONS.csv` supplies scheduler/ReturnQ cycle fractions and longest high-average-window runs. High average means adjacent completed 5K windows whose average exceeds the declared threshold; it is not a claim about every cycle in that interval.
- `CHANNEL_IMBALANCE.csv` reports traffic-conditioned and traffic-weighted channel imbalance. Idle-window extremes are not causal evidence.
- `native_dram_data_bus_util_window=NOT_EMITTED` / `native_dram_data_bus_window_status=NOT_RETAINED_PER_5K_WINDOW` deliberately distinguishes an unretained per-window physical-bus metric from measured zero.
