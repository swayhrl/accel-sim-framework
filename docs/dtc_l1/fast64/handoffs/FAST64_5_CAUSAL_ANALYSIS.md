# FAST64.5 causal-analysis preparation

Status: **ACTIVE — measured package complete; classification reconciliation pending**

The cap-resolved Stage4 bridge is
`generated/fast64_4_acceptance_bridge_v1/fast64_4_primary_accepted_matrix_v1.tsv`.
It is generated only after SHA/hash/cap-map revalidation and marks exactly 36
rows `STRICT_TERMINAL_ACCEPTED`; its adjacent compatibility matrix exists only
for the frozen feature renderer.  The measured FAST64.5 package at
`generated/fast64_5_measured_features_v3/` passes the V2 builder with exact
Stage3/4 membership and table-column provenance.  It remains non-causal until
the separately validated classification is joined.

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

Classification remains a separate, researcher/source-backed step.  The frozen
template and validator enforce exact FAST12 coverage, legal enums, rationale
and evidence references; the validator cannot manufacture a class and rejects
an unresolved `IMPLEMENTATION_MODELING_ISSUE` for PASS.  When an evidence root
is provided, it also rejects a classification whose semicolon-separated
evidence path does not resolve to a real artifact.

`collect_fast64_5_causal_analysis_v1.py` is the future-only join path.  It
requires FAST64.3/4 PASS, the complete v2 measured-feature package, an exact
36-cell accepted feature manifest, and a fully validated supplied
classification.  It atomically produces a hash-bound candidate package but
does not alter the stage ledger or infer causality.  Positive and prior-stage
negative regression fixtures cover this boundary.

The v2 regression fixture proves both a valid full accepted matrix and a
negative `PRIMARY_ACCEPTANCE_REQUIRED` case.  This is tooling preparation
only: FAST64.4 is not PASS, no feature output or causal claim is published.
