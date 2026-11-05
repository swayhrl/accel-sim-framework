# EP-L2 V5 exact8 rolling results

Only CLOSED_ACCEPTED cells with full true164 archive and two distinct Native restores have published accepted cycles. Missing cells are UNKNOWN. All eight cells release independently.

| Group | Cohort | State | Accepted cycles |
|---|---|---|---:|
| A | EP_PERF_PFV5_A_FWT_G32W8_S_V1 | CONSUMED_BEFORE_FORK | UNKNOWN |
| A | EP_PERF_PFV5_A_FWT_G32W8_WV_OFF_V1 | CONSUMED_BEFORE_FORK | UNKNOWN |
| A | EP_PERF_PFV5_A_FWT_G32W8_WV_ON_V1 | CONSUMED_BEFORE_FORK | UNKNOWN |
| B | EP_PERF_PFV5_B1_VECTOR4M_F_BASELINE_1700_V1 | CLOSED_ACCEPTED | 55925 |
| B | EP_PERF_PFV5_B1_VECTOR4M_F_PRESSURE_EPOCH_1700_V1 | CLOSED_ACCEPTED | 45425 |
| D | EP_PERF_PFV4_A2_3MM_S_G64W8_V1 | CONSUMED_BEFORE_FORK | UNKNOWN |
| D | EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_G64W8_V1 | CONSUMED_BEFORE_FORK | UNKNOWN |
| D | EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_REF32W8_V1 | CONSUMED_BEFORE_FORK | UNKNOWN |

Counts: {"accepted": 2, "technical_failure": 0, "pending": 6}

## Matched comparisons

- B_same_newSource_F_pressure_vs_Fbaseline: {"reference_cycles": 55925, "candidate_cycles": 45425, "saved_cycles": 10500, "reduction_percent": 18.775145283862315}
- A_cold_ON_vs_OFF: {"status": "UNKNOWN_UNTIL_BOTH_EXACT_CELLS_ACCEPTED"}
- A_WV_OFF_vs_S: {"status": "UNKNOWN_UNTIL_BOTH_EXACT_CELLS_ACCEPTED"}
- A_WV_ON_vs_S: {"status": "UNKNOWN_UNTIL_BOTH_EXACT_CELLS_ACCEPTED"}
- D_G64_WV_vs_S: {"status": "UNKNOWN_UNTIL_BOTH_EXACT_CELLS_ACCEPTED"}
- D_WV_G64_vs_REF32: {"status": "UNKNOWN_UNTIL_BOTH_EXACT_CELLS_ACCEPTED"}
- D_S_G64_vs_accepted_S_REF32: {"status": "UNKNOWN_UNTIL_EXACT_G64_S_ACCEPTED"}

A cold filter is lifetime never-installed proof, not general empty-directory detection. B retains full query port and cycle costs. C remains partial production engineering with no science starts. 1700MHz is service diagnostic, not GPU calibration.
