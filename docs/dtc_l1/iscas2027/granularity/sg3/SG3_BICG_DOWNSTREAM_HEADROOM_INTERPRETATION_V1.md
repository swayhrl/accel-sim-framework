# SG3 BICG downstream-headroom interpretation V1

## Scope and evidence boundary

This Phase-A record uses only the ten accepted observer-ON BICG rows named in
`SG3_BICG_DOWNSTREAM_TELEMETRY_HEADROOM_TABLE_V1.tsv`: IO and OO at default,
capacity=2x, MSHR=4x, cap=2048, and cap=512.  Every row is a natural-exit
strict PASS on Core `9b6bd33f`; all instruction counts are 145,666,048.

The table preserves raw counters.  Its derived columns use exactly:

- average DTC outstanding = `SG3_dtc_lower_outstanding_integral / SG3_dtc_core_tick_samples`;
- average L2 MSHR occupancy per bank = `SG3_l2_mshr_occupancy_integral / SG3_l2_bank_tick_samples`;
- average miss-queue occupancy per bank = `SG3_l2_miss_queue_occupancy_integral / SG3_l2_bank_tick_samples`;
- average lower lifetime = `SG3_lower_lifetime_sum_cycles / SG3_lower_lifetime_completed`;
- cycle change = `row_cycles / same-mode_default_cycles - 1`.

`DTC_L1_lower_outstanding_peak` is source-defined but not emitted by these
accepted historical terminal receipts; it is explicitly `NOT_REPORTED`, not
reconstructed.  The classified resource-reservation total is the sum of only
`MSHR_ENTRY_FAIL`, `MSHR_MERGE_ENTRY_FAIL`, `MISS_QUEUE_FULL`,
`LINE_ALLOC_FAIL`, and `MSHR_RW_PENDING`.  The merge-tag identity-guard field
is shown separately and excluded; it is zero for every BICG row.

## Findings and predeclared trigger receipt

- **SOURCE_PROVEN:** the default L2 has a 32-entry per-bank miss queue and
  source-defined `MISS_QUEUE_FULL`; the DTC cap is GPU-wide.  The field map
  and telemetry inventory identify queue occupancy/failure and lower lifetime
  as valid diagnostics.
- **MEASURED:** in IO, `MISS_QUEUE_FULL` decreases monotonically from
  145,882,748 (default) to 85,372,492 (cap=2048) to 1,519,623 (cap=512).
  In OO it decreases from 43,594,150 to 22,091,866 to 5,483,102.  Lower
  lifetime and cycles decrease in the same order in both modes: IO lifetime
  10,455.99 -> 4,256.99 -> 659.56 cycles and total cycles 93.94M -> 59.80M
  -> 24.42M; OO lifetime 5,612.70 -> 3,082.41 -> 505.00 cycles and total
  cycles 47.23M -> 35.14M -> 18.94M.
- **CORRELATION:** this is a coherent queue-pressure chain under DTC cap
  reduction.  It does not by itself prove that queue capacity is the unique
  physical root cause.  The modest average queue occupancies are not treated
  as a refutation of the source-defined full-event counts.
- **NOT_SUPPORTED / INSUFFICIENT (port):** data/fill port utilization is not
  near saturation in these accepted rows and does not consistently fall under
  cap reduction (for example IO data-port utilization is 0.005, 0.015, and
  0.064 at default, cap=2048, cap=512).  The port-path precondition therefore
  is not met.
- **INTERVENTION_SUPPORTED:** not yet applicable at Phase A.  It can only be
  assigned after a strict-PASS queue=128 intervention at cap=8192.

### Decision

**Path Q is triggered.**  The nontrivial source-defined `MISS_QUEUE_FULL`
counts fall consistently with cap reduction, while lifetime and cycles improve
in the same direction for both IO and OO.  Phase B may run only the four
predeclared `miss_queue=128` rows (BICG/GESUMMV x IO/OO), with cap=8192 and
all other scientific identity held fixed.

**Path P is not triggered.**  The queue path is the dominant coherent pattern
and port evidence does not meet its independent condition.  No port, combined,
capacity, MSHR, service, NoC, ROP, DRAM, or additional cap point is authorized
by this receipt.

## Remote-state delta

The 2026-09-24 fetch observed SG1=`e909f90a`, SG3=`4f6e136e`, and
SG5=`f4077f46`, matching the coordination anchors.  SG4A remote is
`7c0a90e`, which is a descendant of the older coordination anchor
`42735258`; no SG4A evidence is used or modified in this stage.
