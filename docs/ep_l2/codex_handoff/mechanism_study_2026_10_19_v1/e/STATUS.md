# Lane E2 — capacity diagnostic / CAPACITY_PARSER_FIX_AND_RESOURCE_ONLY_SWITCH_REVIEWED

Original174; T0 1792414193; actual 38/46, remaining 8; old36 immutable and charged, contingency8/8 preserved. Controller ACTIVE. New diagnostic accepted pairs 0/5. Original MAIN and control results unchanged.

Formal concurrency: RESOURCE_ONLY, ADOPTED_PENDING_SAFE_CONTROLLER_SOURCE_SWITCH. Fixed E formal simulator-count limits removed by explicit user approval; existing CPU/RAM/disk and result/start budgets remain.

Result generation: new 6103575638B/10737418240B; old+new 20413152022B/25769803776B; growth since36 949020422B. Workspace5GiB floor+2GiB monitor and Share/CPU/RAM controls unchanged. Authority4934388; no old-main61 eligibility or anchor reuse.

| Condition | Attempt | State |
|---|---|---|
| V3_CAPACITY_cfd_097k_S_OFF | E037_a423c80f | FAILED |
| V3_CAPACITY_cfd_097k_S_ON | E038_d7ffe08b | RUNNING |
| V3_CAPACITY_sad_S_OFF | None | NOT_STARTED |
| V3_CAPACITY_sad_S_ON | None | NOT_STARTED |
| V3_CAPACITY_vectorAdd_4M_S_OFF | None | NOT_STARTED |
| V3_CAPACITY_vectorAdd_4M_S_ON | None | NOT_STARTED |
| V3_CAPACITY_dwt2d_S_OFF | None | NOT_STARTED |
| V3_CAPACITY_dwt2d_S_ON | None | NOT_STARTED |
| V3_CAPACITY_convolutionSeparable_S_OFF | None | NOT_STARTED |
| V3_CAPACITY_convolutionSeparable_S_ON | None | NOT_STARTED |

Next never-started authorized conditions: V3_CAPACITY_sad_S_OFF, V3_CAPACITY_sad_S_ON, V3_CAPACITY_vectorAdd_4M_S_OFF, V3_CAPACITY_vectorAdd_4M_S_ON, V3_CAPACITY_dwt2d_S_OFF, V3_CAPACITY_dwt2d_S_ON, V3_CAPACITY_convolutionSeparable_S_OFF, V3_CAPACITY_convolutionSeparable_S_ON. No automatic retry.
