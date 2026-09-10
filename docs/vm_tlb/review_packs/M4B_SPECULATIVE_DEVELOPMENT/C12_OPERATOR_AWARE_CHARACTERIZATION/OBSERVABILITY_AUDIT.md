# C12 operator-aware observability audit

## Exact per kernel

- `Processing kernel` markers are ordered exactly as the C12 compute-only list; `INDEX_ALIGNMENT_AUDIT.tsv` records every mapping.
- Every one of the 22 terminal-PASS arms has exactly one explicit `gpu_sim_cycle` value per processed kernel.  The per-kernel sum must equal both formal `gpu_tot_sim_cycle` and `C12_ARM_VALIDATION.json`, or parsing fails.
- `vm_*` translation, Segment, and Sub-entry fields are end-of-kernel cumulative snapshots.  For every field used for per-kernel attribution, this parser requires exactly one value at every kernel snapshot, monotonicity, delta-sum closure to the terminal raw value, and equality to a numeric immutable validation value when emitted; any mismatch fails parsing.  A field absent from an entire raw arm is not attributed.
- `m4c_telemetry` and `m4c_telemetry_l2` rows with scope `KERNEL` are exact per-kernel cache transactions.  Reservation fails remain a distinct outcome.

## Trace derived

- Weight/KV/UNKNOWN lane references and 64 KiB page sets are reconstructed from all predicated lanes in immutable trace records, using runtime SimVA ranges.  These are trace references, not coalesced cache transactions.
- Direct parameter labels are derived only by exact intersection of those trace addresses with `weight_layout` ranges.

## Full ROI only / deliberately unattributed

- Formal C12 cycles and speedup are also retained as `FULL_ROI_ONLY` anchors in `ARM_OPERATOR_CHARACTERIZATION.tsv`.
- `m4c_*` rows scoped `FIXED_WINDOW_PARTIAL` are intentionally excluded from operator cache totals: their scope cannot be made kernel-exact.
- No counter is divided by kernel count, trace refs, or cycle share.  No filename is used for semantic classification.
