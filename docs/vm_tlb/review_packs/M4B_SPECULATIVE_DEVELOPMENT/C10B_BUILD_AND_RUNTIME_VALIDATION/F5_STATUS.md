# F5 physical PWC status

Status: `C10B_F5_PASS` — `SPECULATIVE_CANDIDATE` model, not a PPA claim.

Core `4a38227d` implements the C9 F5 path separately from the historical
generic logical 128-entry PWC. The current Core head `5b409493` retains that
implementation and adds the all-arm bounded sanity target.

The realized F5 model is exactly the C9 accounting point:

- 120 entries, partitioned 40/40/40 over the three non-leaf levels;
- ten four-way sets per level with three tree-PLRU bits/set;
- `valid + ASID + level + prefix(6|15|24) + next_table_PPN(33) + attrs(2)`;
- 8,280 array bits and 90 PLRU bits, hence 8,370 PWC bits;
- one global PWC accept/cycle with an explicit pending queue, denials, queue
  wait, maximum wait, and high-watermark telemetry; and
- exact L2 remainder `E=656`, 16-way/41 sets, yielding
  `8,370 + 56,375 = 64,745 <= 66,000` charged bits.

`vm_c10b_f5_physical_pwc_test` and the emitted-telemetry parser both pass.
They exercise all three non-leaf prefix levels under contention, payload
validation on hits, four-way replacement/eviction, ASID flush, PTE 1:1
completion, and complete drain. The historical generic PWC remains a separate
standard-mode path and is not relabelled F5.

`next_table_PPN` is the C9 33-bit modeled physical child-table-frame payload;
it is not the M3 synthetic PTE transport address. F5 timing is a configurable
model point, not a silicon latency/area/power measurement.
