# Final C7e telemetry field audit

`TELEMETRY_COMPLETENESS.csv` provides 22 × family producer checks. All rows are `MEASURED`; measured zero is retained as zero rather than re-labeled as absent.

- Tag/set: exact `c7e_tag_way_alloc_need/block` and `c7d_tag_set_all_reserved_block` from `target_slice.csv`.
- Line MSHR / descriptor / per-address: exact C7e need plus C7d full/cap fields and descriptor-chain fields from `target_slice.csv`.
- WAD: occupancy/full/hazard/hazard-wait are final parsed fields. WAD lifetime has a producer field in `target_slice.csv`; kernel lifetime remains explicitly unavailable where the producer records that condition.
- Payload: resident occupancy, VALID, DIRTY, pending sectors, bypass state, service denial, and capacity denial are producer fields in `target_slice.csv`. The final analysis retains service and capacity separately.
- Bank: logical ops, attempts, grants, retries, true-conflict ops/events, wait, four-bank totals, and operation classes are producer fields in `target_slice.csv`/`target_bank.csv`; conflict rate is `true_conflict_ops / logical_ops`.
- L1D: accesses/misses, allocation, MSHR entry/merge/RW-pending, MissQ, and bank/latency queue are `EPL2L1V1` fields in `target_l1.csv`.
- Lower path: MissQ, L2-to-DRAM, issue attempts, scheduler causal/observed state, ReturnQ, DRAM-to-L2, successful transactions/bytes, and bandwidth are the `EPL2B0V1` and `EPL2DRAMV1` producer fields used by the exact final analyzer.
- Temporal: L2 5K windows are `target_window.csv`; per-channel DRAM 5K windows are `target_dram.csv` scope `window`.
