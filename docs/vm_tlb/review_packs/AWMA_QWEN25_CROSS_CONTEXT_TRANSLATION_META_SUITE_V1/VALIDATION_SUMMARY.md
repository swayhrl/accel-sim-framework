# Validation summary

- All S2 and cross-context input SHA-256 values match accepted authorities.
- Scenario strata sums match receipt full GPU durations:
  S2 154,876,910 ns; T256 113,218,961 ns; T8192 317,794,729 ns;
  B4 308,549,681 ns; D128 497,208,082 ns.
- S2 BALANCED contains exactly 23 disjoint structural clusters and 25
  targets; Level 3 S2 mass is 139,333,064 ns (89.9637%).
- CROSS_CONTEXT_CLUSTER_MAP.tsv has 115 rows, one for every selected S2
  cluster in each of five scenarios.
- T256 retains five PORTABLE_EXACT Decode GEMV shapes. B4 has zero Decode
  GEMV strata and five S2 GEMV clusters labeled SCENARIO_SPECIFIC_DISPATCH;
  the report does not assign one-to-one operator equivalence.
- D128 retains the 32 S2 trajectory grids and has exactly 96 new contiguous
  step 33–128 grids with 48 launches each and 28,654,328 ns mass.
- Extension candidates partition every nonauxiliary Level 3 gap without
  overlapping the accepted S2 exact set. The proposal has 25 core plus
  28 extension target identities, all unique.
- Four directed identity/recurrence tests pass. A second full generation is
  byte-identical for generated TSV/JSON outputs. SHA256SUMS closes published
  code, report, and review evidence.
- No GPU, capture, Accel-Sim, mechanism, C1, or Lane B operation was run.
