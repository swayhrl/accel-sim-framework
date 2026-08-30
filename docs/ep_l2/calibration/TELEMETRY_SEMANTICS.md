# Lane-D telemetry semantics

- Window `*_avg` is a producer-sampled occupancy average; it is not an event
  count. Window distributions are across emitted 5K stream records.
- `*_block`, `*_full`, and retry counters are events and need not be exclusive
  blocked cycles. They must not be summed into a cycle decomposition.
- A field absent from a producer is emitted as `NOT_EMITTED`; numeric zero is
  retained as a measured zero.
- `target_window.csv` is per L2 slice. `target_dram.csv` is per DRAM channel.
  C7e emits completed 5K intervals only, so expected rows use
  `floor(completion_cycles / 5000) * stream_count`. Stream validation rejects
  duplicate `(stream_id, start_cycle)` keys, unexpected IDs, and missing or
  gapped windows. L2 starts are exactly 5K apart; DRAM's global-cycle starts
  are 5K/5K+1 apart because sampling occurs on the 850-MHz DRAM cadence.
- C7e `bandwidth_util` is renamed to
  `lower_admission_byte_rate_norm`: it credits accepted L2->DRAM request bytes
  and is **not** physical DRAM data-bus utilization. The matrix separately
  parses final application-level native `bwutil`/`n_cmd` from retained raw
  logs as `native_dram_data_bus_util`. No physical 5K-window bus metric was
  retained, so it is explicitly `NOT_EMITTED`.
- `longest_high_average_window_run` means consecutive 5K window *averages*
  at or above 90% capacity. It cannot establish the absence of a sub-window
  burst or full event.
- Channel imbalance uses admitted bytes, not physical bus bytes. It reports
  active channels and an all-window view, but causal interpretation uses only
  windows at or above 1% of the aggregate per-window nominal byte capacity,
  plus traffic-weighted summaries. Near-idle extremes are not bottleneck
  evidence.
- Calibration deltas require matching workload, variant, frequency, and trace
  identity. Source SHA changes require a machine-readable lineage contract
  naming the formal base SHA pair and a PASS equivalence-gate evidence path.
  Effective config maps must differ in exactly the fields authorized for the
  declared D512/META-HR/BANK-HR cell; opaque config hashes alone are not
  accepted as proof.
