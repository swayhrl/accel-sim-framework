# C16 E1 Oracle-Elastic B16 Reuse Performance Canary

Status: `C16_E1_ORACLE_ELASTIC_B16_REUSE_CANARY_COMPLETE_V1`

Interpretation: `CASE_3_RESIDENCY_ACTIVITY_WITHOUT_TARGET_LOCAL_TIMING_BENEFIT`

## Independently validated results

| Metric | R0 cycles | M1 cycles | R0-M1 cycles | Response |
|---|---:|---:|---:|---:|
| `C_window` | 134571764 | 134848220 | -276456 | -0.205433883% |
| `C_D2_prefix` | 3535452 | 3520859 | 14593 | 0.412761933% |
| `C_L0_up_D2` | 1286074 | 1289645 | -3571 | -0.277666759% |

## Qualification

- R0 and M1 workload identity and correctness: PASS.
- Mechanism activation and full diagnostic coverage: PASS.
- M1 diagnostic neutrality, including per-UID cycles/instructions/CTA: PASS.
- Reproducibility: `BOUNDED_REPRODUCIBILITY_PREFIX_PASS_UID168`; this is not a full-window repeat.
- D1 L0 class-1 occupancy after fill: 131072.
- D1 L0 class-1 occupancy retained immediately before D2 reuse: 0.
- Exact diagnostic coverage: 1,565 UIDs x 16 L2 instances = 25,040 counter rows and 25,040 class-occupancy rows.
- External test summary supplied to the publisher: yes (PASS).

## Interpretation boundary

The Case 4 exact zero-retention subset was not satisfied. No post-hoc numeric definition of qualitative words such as 'almost' or 'large' is introduced.

## Claim boundary

`FIRST_QUALIFIED_REAL_TRACE_B16_REUSE_WINDOW_CANARY_ONLY`. This pack does not claim whole-model/system speedup, does not provide a budget-matrix promotion decision, and does not begin a later mechanism stage.

`VALIDATION_SUMMARY.json` records the fail-closed publication checks and input hashes. `FOLLOWUP_RECEIPT.json` is the byte-exact controller receipt.
