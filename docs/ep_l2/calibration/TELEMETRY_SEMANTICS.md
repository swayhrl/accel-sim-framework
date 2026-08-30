# Lane-D telemetry semantics

- Window `*_avg` is a producer-sampled occupancy average; it is not an event
  count. Window distributions are across emitted 5K stream records.
- `*_block`, `*_full`, and retry counters are events and need not be exclusive
  blocked cycles. They must not be summed into a cycle decomposition.
- A field absent from a producer is emitted as `NOT_EMITTED`; numeric zero is
  retained as a measured zero.
- `target_window.csv` is per L2 slice. `target_dram.csv` is per DRAM channel.
  C7e emits completed 5K intervals only, so expected rows use
  `floor(completion_cycles / 5000) * stream_count`.
- Channel imbalance is computed for each time interval over all channels using
  successful bytes, then summarized as p95/max of max-to-mean and CV. Zeros
  are real channel samples.
- Calibration deltas require matching workload, variant, Core SHA, Framework
  SHA, frequency, and trace identity. A differing config hash is accepted only
  for an explicitly declared descriptor/L1 cell; otherwise it is rejected.
