# Stats Equivalence Schema

A11 emits comparison-grade stats in two layers.

`A11_normalized_stats_*.csv` is a long table of parsed Accel-Sim/GPGPU-Sim log stats. Each row records the parser mode: `first`, `last`, `aggregate_sum`, or `per_kernel`. These modes are not mixed silently. `per_kernel` is best effort unless a log provides robust kernel boundaries.

`A11_stats_equivalence_matrix_*.csv` maps prior stats-field names to Accel-Sim log fields. Equivalence classes are conservative:

- `exact`: same stat key and same required mode.
- `derived`: needs a documented formula such as instructions divided by cycles.
- `approximate`: similar metric family but config or hierarchy equivalence is not fully proven.
- `accel_missing` or `prior_missing`: one side is absent.
- `not_comparable`: present but not suitable for paper-effect comparison.
- `unknown`: insufficient evidence.

A11 is intentionally narrow: Mascar/hotspot and MeDiC/srad only.
