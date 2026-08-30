# Review-facing bandwidth semantics

The former review-table field `dram_bandwidth_util` has been removed.

- `lower_admission_byte_rate_norm` is the C7e producer's normalized accepted
  L2→DRAM request-byte admission rate. It is a lower-path admission metric,
  not physical DRAM data-bus utilization.
- `native_dram_data_bus_util_weighted_mean` is the physical application-level
  DRAM data-bus metric parsed from the final complete 32-channel native
  `DRAM[id]` raw-log snapshot, weighted by `n_cmd`.

`D512_CALIBRATION_COMPARISON.csv` exposes both quantities for D256 and D512;
`D512_RESOURCE_PRESSURE.csv` exposes both for D512; and
`D512_NATIVE_DRAM_BANDWIDTH.csv` preserves status, channel count, weighted
mean, p50/p95/max, command sum, and raw source path for all 52 cells. Every
snapshot is `PASS_FINAL_COMPLETE_CHANNEL_SNAPSHOT` with 32 channels.

No physical DRAM data-bus metric was retained per 5K window. It is therefore
`NOT_EMITTED`/`NOT_RETAINED_PER_5K_WINDOW`, rather than being inferred from
the lower-admission field.
