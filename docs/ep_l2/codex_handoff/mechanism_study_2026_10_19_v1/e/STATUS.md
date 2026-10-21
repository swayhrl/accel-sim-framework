# Lane E2 — capacity diagnostic / CAPACITY_COUNT_AND_TIME_REMOVAL_APPROVED_PENDING_DRAIN

Original174; T0 1792414193; actual 45/46, remaining 1; old36 immutable and charged, contingency8/8 preserved. Controller ACTIVE. New diagnostic accepted pairs 2/5. Original MAIN and control results unchanged.

Formal concurrency: RESOURCE_ONLY, APPLIED. Fixed E formal simulator-count limits removed by explicit user approval; existing CPU/RAM/disk and result/start budgets remain.

Result generation: new 6758839619B/10737418240B; old+new 21068416003B/25769803776B; growth since36 1604284403B. Workspace5GiB floor+2GiB monitor and Share/CPU/RAM controls unchanged. Authority4934388; no old-main61 eligibility or anchor reuse.

| Condition | Attempt | State |
|---|---|---|
| V3_CAPACITY_cfd_097k_S_OFF | E037_a423c80f | COMPLETE_VALID_PARSER_RECOVERY_ORIGINAL_FAILED_RETAINED |
| V3_CAPACITY_cfd_097k_S_ON | E038_d7ffe08b | COMPLETE_VALID_PARSER_RECOVERY_ORIGINAL_FAILED_RETAINED |
| V3_CAPACITY_sad_S_OFF | E039_0c426330 | COMPLETE_VALID |
| V3_CAPACITY_sad_S_ON | E040_b264d86f | RUNNING |
| V3_CAPACITY_vectorAdd_4M_S_OFF | E041_6412b85d | COMPLETE_VALID |
| V3_CAPACITY_vectorAdd_4M_S_ON | E042_307fac20 | COMPLETE_VALID |
| V3_CAPACITY_dwt2d_S_OFF | E043_c96ede71 | COMPLETE_VALID |
| V3_CAPACITY_dwt2d_S_ON | E044_4c4350db | RUNNING |
| V3_CAPACITY_convolutionSeparable_S_OFF | E045_3c8a6cc8 | RUNNING |
| V3_CAPACITY_convolutionSeparable_S_ON | None | NOT_STARTED |

Next never-started authorized conditions: V3_CAPACITY_convolutionSeparable_S_ON. No automatic retry.
