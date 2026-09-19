# Target boundary delta schema

For cumulative simulator fields, `TARGET_DELTA = post-Q05 snapshot − pre-Q05 snapshot`, where snapshots are adjacent per-kernel report boundaries in the same process. `gpu_sim_cycle` and `gpu_sim_insn` are direct Q05 kernel fields and are not subtracted. `AWMA_VM_COVERAGE` is explicitly target-kernel gated. The 499 whole-prefix walk count is therefore never asserted as a target value; the delta TSV is the target-scoped source for comparisons.
