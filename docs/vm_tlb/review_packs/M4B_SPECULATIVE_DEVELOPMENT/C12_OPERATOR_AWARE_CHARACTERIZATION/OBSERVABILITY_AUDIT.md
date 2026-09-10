# C12 operator-aware observability audit

## Exact per kernel

- `Processing kernel` markers are ordered exactly as the C12 compute-only list; `INDEX_ALIGNMENT_AUDIT.tsv` records every mapping.
- `gpu_sim_cycle` and `gpu_sim_insn` appear once per processed kernel in each terminal raw log.
- `vm_*` translation, Segment, and Sub-entry fields are end-of-kernel cumulative snapshots.  This parser differences adjacent snapshots and verifies selected final totals against immutable `C12_ARM_VALIDATION.json`; the resulting deltas are exact per-kernel events.
- `m4c_telemetry` and `m4c_telemetry_l2` rows with scope `KERNEL` are exact per-kernel cache transactions.  Reservation fails remain a distinct outcome.

## Trace derived

- Weight/KV/UNKNOWN lane references and 64 KiB page sets are reconstructed from all predicated lanes in immutable trace records, using runtime SimVA ranges.  These are trace references, not coalesced cache transactions.
- Direct parameter labels are derived only by exact intersection of those trace addresses with `weight_layout` ranges.
- A `KV` object class proves only that a trace address intersects the selected runtime KV range. The available records do not establish per-instruction logical KV ownership, object lifetime use, or semantic fusion; `KV_CLASS_TRANSACTION_AUDIT.md` preserves that boundary for FFN and Embedding/Output observations.

## Full ROI only / deliberately unattributed

- Formal C12 cycles and speedup are also retained as `FULL_ROI_ONLY` anchors in `ARM_OPERATOR_CHARACTERIZATION.tsv`.
- `m4c_*` rows scoped `FIXED_WINDOW_PARTIAL` are intentionally excluded from operator cache totals: their scope cannot be made kernel-exact.
- No counter is divided by kernel count, trace refs, or cycle share.  No filename is used for semantic classification.
