# EP-L2 V5 exact8 rolling results

Only CLOSED_ACCEPTED cells with full true164 archive and two distinct Native restores have published accepted cycles. Missing cells are UNKNOWN. All eight cells release independently.

| Group | Cohort | State | Accepted cycles |
|---|---|---|---:|
| A | EP_PERF_PFV5_A_FWT_G32W8_S_V1 | CLOSED_ACCEPTED | 181827 |
| A | EP_PERF_PFV5_A_FWT_G32W8_WV_OFF_V1 | CLOSED_ACCEPTED | 178951 |
| A | EP_PERF_PFV5_A_FWT_G32W8_WV_ON_V1 | CLOSED_ACCEPTED | 180074 |
| B | EP_PERF_PFV5_B1_VECTOR4M_F_BASELINE_1700_V1 | CLOSED_ACCEPTED | 55925 |
| B | EP_PERF_PFV5_B1_VECTOR4M_F_PRESSURE_EPOCH_1700_V1 | CLOSED_ACCEPTED | 45425 |
| D | EP_PERF_PFV4_A2_3MM_S_G64W8_V1 | CONSUMED_BEFORE_FORK | UNKNOWN |
| D | EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_G64W8_V1 | CONSUMED_BEFORE_FORK | UNKNOWN |
| D | EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_REF32W8_V1 | CONSUMED_BEFORE_FORK | UNKNOWN |

Counts: {"accepted": 5, "technical_failure": 0, "pending": 3}

## Matched comparisons

- B_same_newSource_F_pressure_vs_Fbaseline: {"reference_cycles": 55925, "candidate_cycles": 45425, "saved_cycles": 10500, "reduction_percent": 18.775145283862315}
- A_cold_ON_vs_OFF: {"reference_cycles": 178951, "candidate_cycles": 180074, "saved_cycles": -1123, "reduction_percent": -0.6275460880352722}
- A_WV_OFF_vs_S: {"reference_cycles": 181827, "candidate_cycles": 178951, "saved_cycles": 2876, "reduction_percent": 1.5817232864206086}
- A_WV_ON_vs_S: {"reference_cycles": 181827, "candidate_cycles": 180074, "saved_cycles": 1753, "reduction_percent": 0.9641032409928119}
- D_G64_WV_vs_S: {"status": "UNKNOWN_UNTIL_BOTH_EXACT_CELLS_ACCEPTED"}
- D_WV_G64_vs_REF32: {"status": "UNKNOWN_UNTIL_BOTH_EXACT_CELLS_ACCEPTED"}
- A_observed_frontend_queries_OFF_vs_ON: {"OFF": 150462, "ON": 148843, "fewer_queries": 1619, "reduction_percent": 1.0760191942151507, "semantics": "final64-slice cumulative totals of matched complete FWT cells; exact cold_bypasses is not exported by frozen Source; no invented per-access attribution"}
- D_S_G64_vs_accepted_S_REF32: {"status": "UNKNOWN_UNTIL_EXACT_G64_S_ACCEPTED"}

## Architecture cost and bounded interpretation

Logical costs: {"A": {"Tag_entries_per_slice": 256, "Payload_slots_per_slice": 1168, "Banks": 4, "bank_ops_per_physical_cycle": 1, "extra_control_state_bits_per_slice": 1, "extra_query_ports": 0, "extra_payload_arrays": 0, "physical_mux_timing": "NOT_PROVEN"}, "B": {"Tag_entries_per_slice": 256, "Payload_slots_per_slice": 1168, "Banks": 4, "extra_control_state_bits_per_slice": 1, "query_port_and_query_cycle": "ORIGINAL_FINITE_COST_RETAINED", "extra_CAM_or_queue_entries": 0, "physical_timing_PPA": "NOT_PROVEN"}, "D": {"Tag_entries_per_slice_G32W8": 256, "Tag_entries_per_slice_G64W8": 512, "Tag_capacity_ratio": 2, "Payload_slots_per_slice": 1168, "Banks": 4, "same_Source78_fixed_service_background": true, "physical_PPA": "NOT_PROVEN"}, "C": {"scientific_models_authorized": 0, "qualification": "PARTIAL_REAL_PRODUCTION_ENGINEERING_NOT_FULL_QUOTA"}}

- B is a same-newSource F policy comparison; positive cycles savings do not isolate T and do not establish cross-workload optimality or GPU calibration.
- In this exact Vector input the pressure epoch never activated. The frozen admission counters show Native service before activation; RO acceptance must be reported explicitly rather than crediting a faster active RO path.
- A evaluates lifetime-never-installed cold proof only. It does not solve sustained Stencil Victim retention; no general empty-directory oracle is claimed.
- A reduced observed total frontend queries without reducing complete-application cycles. Query-count improvement alone is not an application performance benefit.

A cold filter is lifetime never-installed proof, not general empty-directory detection. B retains full query port and cycle costs. C remains partial production engineering with no science starts. 1700MHz is service diagnostic, not GPU calibration.
