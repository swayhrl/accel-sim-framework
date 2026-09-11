# FAST64.5 causal analysis

Status: **PASS — FAST64_5_CAUSAL_PASS**

The cap-resolved Stage4 bridge is
`generated/fast64_4_acceptance_bridge_v1/fast64_4_primary_accepted_matrix_v1.tsv`.
It is generated only after SHA/hash/cap-map revalidation and marks exactly 36
rows `STRICT_TERMINAL_ACCEPTED`; its adjacent compatibility matrix exists only
for the frozen feature renderer.  The measured FAST64.5 package at
`generated/fast64_5_measured_features_v3/` passes the V2 builder with exact
Stage3/4 membership and table-column provenance.  It is joined only to the
separately validated, source-backed classification; the join does not infer a
class from performance data.

`build_fast64_5_feature_tables_v1.py` remains a compact fixture/reference
builder.  The production path is now the future-only
`build_fast64_5_feature_tables_v2.py`: it requires the `FAST64.4 = PASS`
ledger state, exactly 36 explicit `STRICT_TERMINAL_ACCEPTED` matrix rows, exact
Base/IO/OO triplet identity, compact-result provenance equality, mode-specific
conservation and terminal drain before it delegates measured-table rendering.
It writes an immutable input manifest and a table/column-level emitted-feature
provenance table.  It cannot read provisional evidence or manufacture a PASS.

`FAST64_5_METRIC_PROVENANCE_V1.tsv` binds every output column to its source
metric/formula and explicitly preserves the Tag-bank/all-lines-reserved split.
No source-defined lower/live-miss occupancy integral exists in the audited Core
telemetry.  `average_live_misses_per_sm` is therefore emitted only as
`MISSING_SOURCE_DEFINED_AVERAGE`, never inferred from creates, peak, or PIB
occupancy.

Classification is a separate, researcher/source-backed step.  The frozen
template and validator enforce exact FAST12 coverage, legal enums, rationale
and evidence references; the validator cannot manufacture a class and rejects
an unresolved `IMPLEMENTATION_MODELING_ISSUE` for PASS.  When an evidence root
is provided, it also rejects a classification whose semicolon-separated
evidence path does not resolve to a real artifact.

`collect_fast64_5_causal_analysis_v1.py` is the fail-closed join path.  It
requires FAST64.3/4 PASS, the complete v2 measured-feature package, an exact
36-cell accepted feature manifest, and a fully validated supplied
classification.  It atomically produces a hash-bound package but does not
itself alter the stage ledger or infer causality.  The joined package is
`generated/fast64_5_causal_analysis_v1/`; its status is
`FAST64_5_CAUSAL_ANALYSIS_V1_CANDIDATE_PASS`, and it binds the V3 feature
directory SHA and the classification SHA.  Positive and prior-stage negative
regression fixtures cover this boundary.

The V2 regression fixture proves both a valid full accepted matrix and a
negative `PRIMARY_ACCEPTANCE_REQUIRED` case.  The production V2 builder,
classification validator, and collector all pass against the accepted 36-cell
cap-resolved matrix.

## FAST64.5 closeout

All twelve FAST12 members have exactly one accepted Base/IO/OO triplet from
the cap-resolved Stage4 matrix.  The joined classification is recorded in
`generated/FAST64_5_CAUSAL_CLASSIFICATION_V1.tsv`; every class cites actual
feature-table artifacts and the validator rejects missing evidence, incomplete
membership, illegal classes, and unresolved `IMPLEMENTATION_MODELING_ISSUE`.
It retains both mechanism non-beneficiaries and near-neutral rows rather than
discarding them.

The required plot-ready measured data are the five V3 tables:
`fast12_summary.csv`, `fast12_stalls.csv`, `fast12_live_misses.csv`,
`fast12_traffic.csv`, and `fast12_io_oo.csv`.  Their input manifest and
column-level provenance preserve the distinction between Tag-bank arbitration
and true Tag/cacheline allocation failure, and retain live-miss conservation.
`average_live_misses_per_sm` remains explicitly
`MISSING_SOURCE_DEFINED_AVERAGE`; it is never reconstructed from unrelated
counters.  Exact FAST12 GM speedups remain IO `1.326143376` and OO
`1.592062402`.

No unresolved implementation/modeling issue is hidden in the causal package.
The classifications are source-table reconciliations and bounded hypotheses,
not universal causal proof or a redefinition of the scientific mechanism.
Accordingly the FAST64.5 correctness, fidelity, and required-output gates are
closed as `FAST64_5_CAUSAL_PASS`.
