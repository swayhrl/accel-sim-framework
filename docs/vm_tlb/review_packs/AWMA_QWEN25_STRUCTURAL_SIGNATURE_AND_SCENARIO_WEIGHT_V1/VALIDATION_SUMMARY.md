# Validation

PASS:

- V2 and Lane C input hashes match their accepted authorities.
- 100 structural strata sum exactly to 34,677 launches and 154,876,910 ns.
- Catalog has 109 rows: 100 structural plus 9 Lane C unmapped Native-only rows.
- Every structural row is `UNTESTED_ACROSS_CONTEXT` and has a
  `SCENARIO_SPECIFIC` performance-weight label.
- No simulator-native coverage is inferred from an unknown Native-only row.
- No capture, node109 invocation, or Accel-Sim replay occurred.
