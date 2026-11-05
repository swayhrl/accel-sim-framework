# EP-L2 V5 exact8 rolling results

Only CLOSED_ACCEPTED cells with full true164 archive and two distinct Native restores have published accepted cycles. Missing cells are UNKNOWN. All eight cells release independently.

| Group | Cohort | State | Accepted cycles |
|---|---|---|---:|
| A | EP_PERF_PFV5_A_FWT_G32W8_S_V1 | CLOSED_ACCEPTED | 181827 |
| A | EP_PERF_PFV5_A_FWT_G32W8_WV_OFF_V1 | CLOSED_ACCEPTED | 178951 |
| A | EP_PERF_PFV5_A_FWT_G32W8_WV_ON_V1 | CLOSED_ACCEPTED | 180074 |
| B | EP_PERF_PFV5_B1_VECTOR4M_F_BASELINE_1700_V1 | CLOSED_ACCEPTED | 55925 |
| B | EP_PERF_PFV5_B1_VECTOR4M_F_PRESSURE_EPOCH_1700_V1 | CLOSED_ACCEPTED | 45425 |
| D | EP_PERF_PFV4_A2_3MM_S_G64W8_V1 | CLOSED_ACCEPTED | 1666917 |
| D | EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_G64W8_V1 | CONSUMED_BEFORE_FORK | UNKNOWN |
| D | EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_REF32W8_V1 | CLOSED_ACCEPTED | 1671121 |

Counts: {"accepted": 7, "technical_failure": 0, "pending": 1}

## Matched comparisons

- B_same_newSource_F_pressure_vs_Fbaseline: {"reference_cycles": 55925, "candidate_cycles": 45425, "saved_cycles": 10500, "reduction_percent": 18.775145283862315}
- A_cold_ON_vs_OFF: {"reference_cycles": 178951, "candidate_cycles": 180074, "saved_cycles": -1123, "reduction_percent": -0.6275460880352722}
- A_WV_OFF_vs_S: {"reference_cycles": 181827, "candidate_cycles": 178951, "saved_cycles": 2876, "reduction_percent": 1.5817232864206086}
- A_WV_ON_vs_S: {"reference_cycles": 181827, "candidate_cycles": 180074, "saved_cycles": 1753, "reduction_percent": 0.9641032409928119}
- D_G64_WV_vs_S: {"status": "UNKNOWN_UNTIL_BOTH_EXACT_CELLS_ACCEPTED"}
- D_WV_G64_vs_REF32: {"status": "UNKNOWN_UNTIL_BOTH_EXACT_CELLS_ACCEPTED"}
- A_observed_frontend_queries_OFF_vs_ON: {"OFF": 150462, "ON": 148843, "fewer_queries": 1619, "reduction_percent": 1.0760191942151507, "semantics": "final64-slice cumulative totals of matched complete FWT cells; exact cold_bypasses is not exported by frozen Source; no invented per-access attribution"}
- D_REF32_WV_vs_accepted_S_REF32: {"reference_cycles": 1696618, "candidate_cycles": 1671121, "saved_cycles": 25497, "reduction_percent": 1.5028132437590547}
- D_S_G64_vs_accepted_S_REF32: {"reference_cycles": 1696618, "candidate_cycles": 1666917, "saved_cycles": 29701, "reduction_percent": 1.7506003119146443}

## Architecture cost and bounded interpretation

Logical costs: {"A": {"Tag_entries_per_slice": 256, "Payload_slots_per_slice": 1168, "Banks": 4, "bank_ops_per_physical_cycle": 1, "extra_control_state_bits_per_slice": 1, "extra_query_ports": 0, "extra_payload_arrays": 0, "physical_mux_timing": "NOT_PROVEN"}, "B": {"Tag_entries_per_slice": 256, "Payload_slots_per_slice": 1168, "Banks": 4, "extra_control_state_bits_per_slice": 1, "query_port_and_query_cycle": "ORIGINAL_FINITE_COST_RETAINED", "extra_CAM_or_queue_entries": 0, "physical_timing_PPA": "NOT_PROVEN"}, "D": {"Tag_entries_per_slice_G32W8": 256, "Tag_entries_per_slice_G64W8": 512, "Tag_capacity_ratio": 2, "Payload_slots_per_slice": 1168, "Banks": 4, "same_Source78_fixed_service_background": true, "physical_PPA": "NOT_PROVEN"}, "C": {"scientific_models_authorized": 0, "qualification": "PARTIAL_REAL_PRODUCTION_ENGINEERING_NOT_FULL_QUOTA"}}

- B is a same-newSource F policy comparison; positive cycles savings do not isolate T and do not establish cross-workload optimality or GPU calibration.
- In this exact Vector input the pressure epoch never activated. The frozen admission counters show Native service before activation; RO acceptance must be reported explicitly rather than crediting a faster active RO path.
- A evaluates lifetime-never-installed cold proof only. It does not solve sustained Stencil Victim retention; no general empty-directory oracle is claimed.
- A reduced observed total frontend queries without reducing complete-application cycles. Query-count improvement alone is not an application performance benefit.

## Preserved A Host/consumer incident

Original PARSE_HOLD records remain immutable. The first consumer retained an obsolete282 count while the frozen actual map is283. The final ELF also embeds a precommit78_modified6 banner. Main independently rehashed all832 canonical Source files,142 reproduced objects,8 complete libraries and the entire ELF; the reproduction exactly matches the consumed ELF SHA. An exact three-result signed metadata compatibility guard checks the whole original/reproduced ELF and library, exact old literal banners and immutable raw/Spec/HOLD references. Canonical Source7b4 is not relabelled78, and no log text or consumed Spec is rewritten. The original complete postprocess outer checks, unchanged7cc/bf91 numerical body, full283 map, archive and two fresh restores remain mandatory. The failed initial reproduction with another output basename is retained. The old PFV3_G32W16 profile string is a legacy display label; actual options and sealed geometry are G32x8.


## Preserved D postprocess incident

The consumed D Specs omitted compact_module_ref. Main retains each original HOLD and supplies the exact already-qualified c17 compactor in an isolated postprocess instance, with no Spec/raw/Source/ELF change. All original source, full282 map, complete application numerical/outer checks and mandatory archive/two-restores remain unchanged. This is a consumer metadata correction, not a model retry or refund.


A cold filter is lifetime never-installed proof, not general empty-directory detection. B retains full query port and cycle costs. C remains partial production engineering with no science starts. 1700MHz is service diagnostic, not GPU calibration.
