# Observer equivalence qualification report

Status: `D3_PASS`; all retained rows are
`POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT`.

This report qualifies the observer implementation described in
`OBSERVER_TELEMETRY_SPEC.md`. It does not alter any accepted FAST64 result,
replace an accepted runtime, or establish a physical-pool mechanism claim.

## Qualified diagnostic lineage

The four retained pairs use the Core95 observer descendant
`f2c28217be36c9756afab3d937d6aaf35f23cd7b`, rooted at accepted Core95
`95ccdb7a056f2d53f740d90869785cac6d4ee0f5`. The executable SHA-256 is
`a7aeace93c288deb2c4f79a0a19c84ce2553744ef4297a2f64aedf38db9ae411`.
Each pair uses immutable runner SHA-256
`43ad754a87191107fb00f2b9d3ffa1b9183521d38b8ed323aa190c78f138eb24`, the
same workload trace/config identity on both sides, CPU 500, and a natural
terminal receipt with exit status zero.

The complete hashes, attempt IDs, input paths, terminal statuses, and
comparison properties are in
`generated/observer_diagnostic_identity_manifest.tsv`.

## Exact D3 gate

The comparator preserves the ordered compact-stat blocks. This is necessary
for Btree, which emits two blocks rather than one. It requires exact equality
of the `DTC_L1_`, `L2_`, `gpu_tot_sim_`, and `gpgpu_n_` compact-stat sequences;
cycles and instructions; and reports an error for any missing pre-existing
field. The existing accepted IO duplicate counter remains a pre-existing
field. New observer fields are separately required to be zero when telemetry
is off, and terminal observer live-record fields must be zero when telemetry
is on.

| Pair | Ordered cycles off/on | Ordered instructions off/on | Existing fields / observations | New fields / observations | D3 result |
| --- | --- | --- | ---: | ---: | --- |
| NN / IO | `6095` / `6095` | `1284872` / `1284872` | 90 / 128 | 8 / 8 | PASS |
| NN / OO | `6105` / `6105` | `1284872` / `1284872` | 66 / 104 | 9 / 9 | PASS |
| Btree / IO | `123308, 244231` / `123308, 244231` | `217350912, 444467849` / `217350912, 444467849` | 90 / 256 | 8 / 16 | PASS |
| Btree / OO | `90193, 172795` / `90193, 172795` | `217350912, 444467849` / `217350912, 444467849` | 66 / 208 | 9 / 18 | PASS |

For every row, the comparator found no changed or missing pre-existing
counter, telemetry-off new fields were all zero, and terminal live observer
records were zero. The raw retained observer values are in
`generated/observer_telemetry_results.tsv`; the closeout-only retained index
is `generated/observer_retained_exploratory_index.tsv`.

## Scope and downstream disposition

The D3 equality result establishes that the guarded observer is suitable for
diagnostic-only use on this Core95 lineage. It is not evidence that any
specific telemetry value causes a performance result. The Btree observer
values are retained as diagnostic telemetry only, with the classification
above.

No D4 physical-pool diagnostic wave is retained here. Lane B explicitly
states that its bounded source/correlation classifications do not require a
B5 exploratory result; the remaining H3/H4 arrows remain
`INSUFFICIENT_NEEDS_TELEMETRY` unless a separately scoped diagnostic wave is
authorized. No D5 duplicate-request wave is retained: Lane C states that the
source-backed IO evidence already resolves the dissertation no-MSHR claim and
does not require a formal OO rerun. Thus D4 and D5 are
`NOT_REQUIRED_FOR_CURRENT_CONCLUSION`, not negative experimental findings.

Failed, superseded, and mixed-provenance attempts are excluded from these
tables and listed explicitly in
`generated/observer_failed_or_obsolete_attempts.tsv`.
