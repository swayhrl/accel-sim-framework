# FAST64.5 causal-analysis preparation

Status: **PREPARED, FUTURE-ONLY — FAST64.4 PASS REQUIRED**

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
an unresolved `IMPLEMENTATION_MODELING_ISSUE` for PASS.

The v2 regression fixture proves both a valid full accepted matrix and a
negative `PRIMARY_ACCEPTANCE_REQUIRED` case.  This is tooling preparation
only: FAST64.4 is not PASS, no feature output or causal claim is published.
