# Lane E2 — capacity diagnostic / CAPACITY_NEW_RUNTIME_QUALIFIED_BATCH_ADMISSION

Original174; T0 1792414193; actual 38/46, remaining 8; old36 immutable and charged, contingency8/8 preserved. Controller STOPPED. New diagnostic accepted pairs 1/5. Original MAIN and control results unchanged.

Formal concurrency: RESOURCE_ONLY, APPLIED. Fixed E formal simulator-count limits removed by explicit user approval; existing CPU/RAM/disk and result/start budgets remain.

Result generation: new 6112117512B/10737418240B; old+new 20421693896B/25769803776B; growth since36 957562296B. Workspace5GiB floor+2GiB monitor and Share/CPU/RAM controls unchanged. Authority4934388; no old-main61 eligibility or anchor reuse.

| Condition | Attempt | State |
|---|---|---|
| V3_CAPACITY_cfd_097k_S_OFF | E037_a423c80f | COMPLETE_VALID_PARSER_RECOVERY_ORIGINAL_FAILED_RETAINED |
| V3_CAPACITY_cfd_097k_S_ON | E038_d7ffe08b | COMPLETE_VALID_PARSER_RECOVERY_ORIGINAL_FAILED_RETAINED |
| V3_CAPACITY_sad_S_OFF | None | NOT_STARTED |
| V3_CAPACITY_sad_S_ON | None | NOT_STARTED |
| V3_CAPACITY_vectorAdd_4M_S_OFF | None | NOT_STARTED |
| V3_CAPACITY_vectorAdd_4M_S_ON | None | NOT_STARTED |
| V3_CAPACITY_dwt2d_S_OFF | None | NOT_STARTED |
| V3_CAPACITY_dwt2d_S_ON | None | NOT_STARTED |
| V3_CAPACITY_convolutionSeparable_S_OFF | None | NOT_STARTED |
| V3_CAPACITY_convolutionSeparable_S_ON | None | NOT_STARTED |

Next never-started authorized conditions: V3_CAPACITY_sad_S_OFF, V3_CAPACITY_sad_S_ON, V3_CAPACITY_vectorAdd_4M_S_OFF, V3_CAPACITY_vectorAdd_4M_S_ON, V3_CAPACITY_dwt2d_S_OFF, V3_CAPACITY_dwt2d_S_ON, V3_CAPACITY_convolutionSeparable_S_OFF, V3_CAPACITY_convolutionSeparable_S_ON. No automatic retry.
