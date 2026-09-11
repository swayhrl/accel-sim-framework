# FAST64.5 causal-analysis preparation

Status: **PREPARED, FUTURE-ONLY — FAST64.4 PASS REQUIRED**

`build_fast64_5_feature_tables_v1.py` produces measured feature tables only
from an exact accepted FAST64.4 matrix and the corresponding accepted FAST64.3
structural table.  It refuses production execution until the stage ledger
records `FAST64.4 = PASS`; it does not read provisional evidence.

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
