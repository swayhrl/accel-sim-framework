# Validation summary

**Interim disposition:** `M1_INTERIM_REVIEW_READY`; final PASS is intentionally withheld.

- Release Core build passed.
- Seven directed M1/lifecycle/mode-switch checks passed; the expected unsupported-mode abort was verified by its test harness.
- Ten completed parent-vs-M1 D512 rows match exactly in cycles and instructions and are byte-identical in `target_summary.csv`, `target_slice.csv`, `target_kernel.csv`, `target_bank.csv`, `target_window.csv`, `target_l1.csv`, and `target_dram.csv`.
- All recorded rows use the accepted D512 baseline (`descriptor_pool_size=512`, 850 MHz) with composite config digest `a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416`.
- Both M1 Banked long rows were healthy `RUNNING` processes on the same frozen candidate at the initial read-only snapshot. They completed normally during checkpoint assembly, and their exact comparisons are included.
- No mechanism experiment was run. Unified Payload Pool, RO, TVD, headroom/adaptive behavior, and production bypass traffic remain absent.

The status remains interim by instruction: no final PASS disposition is made here. This checkpoint does not authorize a new source change.
