# Lane-E validation report

Overall: **PASS**

| Check | Status | Measured evidence |
|---|---|---|
| A00_PINNED_INPUTS | PASS | manifest SHA-256 and pinned commit/path closure match |
| A01_FAST12_ORDER | PASS | order is derived from pinned FAST12 source; aggregate is excluded |
| A02_PRIMARY_CELLS_AND_GM | PASS | cycles and GM are recomputed from pinned integers; diagnostic rows are rejected |
| A03_D4_CARTESIAN_AND_DENOMINATOR | PASS | exact D4 cartesian coverage and source observer_sample_sm_cycles field |
| A04_D4_LAUNCH_REUSE | PASS | counts computed from pinned rows, not a handwritten observed phrase |
| A05_D5_QUALIFIED_PAIRS | PASS | D5 exact OO metric required; proxy substitution is rejected |
| A06_LOGICAL_MEMBERSHIP | PASS | output rows equal pinned Lane-A table; numeric plot membership is row_kind=NUMERIC_ACCEPTED_POINT |
| A07_PHYSICAL_MEMBERSHIP_AND_BOUNDARY | PASS | output rows equal pinned Lane-A table; numeric plot membership is row_kind=NUMERIC_ACCEPTED_POINT; BICG/GESUMMV 16.5 nonnumeric and Btree 16.5 numeric verified |
| A08_PIB_MEMBERSHIP | PASS | output rows equal pinned Lane-A table; numeric plot membership is row_kind=NUMERIC_ACCEPTED_POINT |
| A09_FIGURE_IDENTITY | PASS | F07 duplicate index/stale series path is prohibited |
| A10_RICH_WORKLOAD_EXPLANATIONS | PASS | Lane-A performance/pressure/HOL/reclaim/traffic/caveat fields are retained per workload |
| MACHINE_F01 | PASS | SVG XML parsed; PNG=1500x900; PDF signature |
| MACHINE_F02 | PASS | SVG XML parsed; PNG=1500x900; PDF signature |
| MACHINE_F03 | PASS | SVG XML parsed; PNG=1500x900; PDF signature |
| MACHINE_F04 | PASS | SVG XML parsed; PNG=1500x900; PDF signature |
| MACHINE_F05 | PASS | SVG XML parsed; PNG=1500x900; PDF signature |
| MACHINE_F06 | PASS | SVG XML parsed; PNG=1500x900; PDF signature |
| MACHINE_F07 | PASS | SVG XML parsed; PNG=1800x1160; PDF signature |
| MACHINE_F08 | PASS | SVG XML parsed; PNG=1500x900; PDF signature |
| MACHINE_F09 | PASS | SVG XML parsed; PNG=1600x1492; PDF signature |
| CLAIM_required_claim_id_set | PASS | required register coverage |
| CLAIM_artifact_claim_references | PASS | explicit figure/workload claim-id mapping; no NLP inference |
| CLAIM_paper_section_traceability | PASS | paper prose references scoped claim groups |
| NEGATIVE_N01_FAST12_ORDER | PASS | core validation failures: ['A01_FAST12_ORDER: order is derived from pinned FAST12 source; aggregate is excluded', "ValueError('coverage/sensitivity audit artifact differs from recomputed result: E_COVERAGE_SENSITIVITY_AUDIT.tsv')"] |
| NEGATIVE_N02_PRIMARY_OBSERVER_CONTAMINATION | PASS | core validation failures: ['A02_PRIMARY_CELLS_AND_GM: cycles and GM are recomputed from pinned integers; diagnostic rows are rejected', "ValueError('coverage/sensitivity audit artifact differs from recomputed result: E_COVERAGE_SENSITIVITY_AUDIT.tsv')"] |
| NEGATIVE_N03_PHYSICAL_16P5_NUMERIC | PASS | core validation failures: ['A07_PHYSICAL_MEMBERSHIP_AND_BOUNDARY: output rows equal pinned Lane-A table; numeric plot membership is row_kind=NUMERIC_ACCEPTED_POINT; BICG/GESUMMV 16.5 nonnumeric and Btree 16.5 numeric verified', "ValueError('coverage/sensitivity audit artifact differs from recomputed result: E_COVERAGE_SENSITIVITY_AUDIT.tsv')"] |
| NEGATIVE_N04_OO_DUPLICATE_PROXY | PASS | core validation failures: ['A05_D5_QUALIFIED_PAIRS: D5 exact OO metric required; proxy substitution is rejected', "ValueError('coverage/sensitivity audit artifact differs from recomputed result: E_COVERAGE_SENSITIVITY_AUDIT.tsv')"] |
| NEGATIVE_N05_INVENTED_D4_40KIB | PASS | core validation failures: ['A03_D4_CARTESIAN_AND_DENOMINATOR: exact D4 cartesian coverage and source observer_sample_sm_cycles field', "ValueError('coverage/sensitivity audit artifact differs from recomputed result: E_COVERAGE_SENSITIVITY_AUDIT.tsv')"] |
| NEGATIVE_N06_PAYLOAD_RELABEL_DRAM | PASS | core validation failures: ['A05_D5_QUALIFIED_PAIRS: D5 exact OO metric required; proxy substitution is rejected', "ValueError('coverage/sensitivity audit artifact differs from recomputed result: E_COVERAGE_SENSITIVITY_AUDIT.tsv')"] |
| CORE_DETERMINISM_EXECUTION | PASS | two isolated core builds; build exit codes=0/0; validation exit codes=0/0; recursive SHA-256 plus byte-size comparison |
| FINAL_PACKAGE_DETERMINISM_EXECUTION | PASS | two isolated complete final-package builds (record included); recursive SHA-256 plus byte-size comparison; both final validators executed |
| VALIDATOR_READONLY_VALIDATE_CORE | PASS | ordinary strict invocation; recursive relative-path SHA-256 plus byte-size map before/after; validator output: LANE_E_CORE_VALIDATION_PASS |
| VALIDATOR_READONLY_VALIDATE | PASS | ordinary strict invocation; recursive relative-path SHA-256 plus byte-size map before/after; validator output: LANE_E_FINAL_VALIDATION_PASS |
