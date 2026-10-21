# Lane E2 — V2_CONTROL_dwt2d_S_VS_S_COPY_FREE_RAM_RETRY_MAIN61_CURRENT_ACCEPTED

Original174; originalT0=1792414193; actual31/40,remaining9,contingency8/8 consumed. main61/Core d010/Framework9dd unchanged. Controller ACTIVE; original unique registry/lock and maximum2.

| Main S/F | S cycles | F cycles | S/F |
|---|---:|---:|---:|
| V2_MAIN_cfd_097k_S_F_MAIN61 | 79093 | 79157 | 0.999191480 |
| V2_MAIN_convolutionSeparable_S_F_MAIN61 | 292932 | 291469 | 1.005019402 |
| V2_MAIN_dwt2d_S_F_MAIN61 | 166519 | 167643 | 0.993295276 |
| V2_MAIN_sad_S_F_MAIN61 | 110773 | 109754 | 1.009284400 |

| Independently accepted control | Anchor cycles | Control cycles | Anchor/control |
|---|---:|---:|---:|
| V2_CONTROL_cfd_097k_F_VS_F_MINUS_R_MAIN61 | 79157 | 80812 | 0.979520368 |
| V2_CONTROL_cfd_097k_F_VS_F_MINUS_V_MAIN61 | 79157 | 80586 | 0.982267391 |
| V2_CONTROL_convolutionSeparable_F_VS_F_MINUS_R_MAIN61 | 291469 | 292432 | 0.996706927 |
| V2_CONTROL_convolutionSeparable_F_VS_F_MINUS_V_MAIN61 | 291469 | 293463 | 0.993205276 |
| V2_CONTROL_convolutionSeparable_F_VS_WV_M_MAIN61 | 291469 | 291469 | 1.000000000 |
| V2_CONTROL_convolutionSeparable_F_VS_WV_T_MAIN61 | 291469 | 291469 | 1.000000000 |
| V2_CONTROL_convolutionSeparable_S_VS_S_COPY_FREE_MAIN61 | 292932 | 293671 | 0.997483579 |
| V2_CONTROL_convolutionSeparable_S_VS_W_ONLY_MAIN61 | 292932 | 291525 | 1.004826344 |
| V2_CONTROL_dwt2d_S_VS_S_COPY_FREE_RAM_RETRY_MAIN61 | 166519 | 166555 | 0.999783855 |

New results4662154054B, old+new18971730438B; growth since20-start control baseline1054791470B.6/20GiB and5GiB+2GiB monitoring reserves unchanged.

Remaining original qualified controls: . DWT/CFD four-cell revision is user-approved and independently qualified; exact matrix adoption retained with original history. Remaining approved controls: . FWT INCOMPLETE,Vector F RESOURCE_LIMIT/exit-15,Btree HOLD and all old receipts remain; no refunds,replay,newGoal,second controller or new migration. COPY_FREE remains diagnostic.

Attempted unsuccessful approved conditions remain charged and are excluded from the unstarted queue: E027_a4c2f04e:RESOURCE_LIMIT,E028_f9b6ca83:RESOURCE_LIMIT. Additional DWT retry follows only the separate explicit user-approved allocation where present; none is inferred from resource recovery. A resource block is not a production correctness PASS or failure. No background watcher or automatic replay.

Additional two-slot DWT recovery proposal: USER_APPROVED_SEE_SEPARATE_RECEIPT. It would forgo unstarted FWT S_L2_DATA_FREE/F_L2_DATA_FREE, charge two new LOCAL_DIAGNOSTIC starts (W_ONLY keeps physical P1), and yield32/40,remaining8 without refund or contingency expansion. Two unique planned configurations are forgone;32 bookkeeping rows do not imply32 distinct configurations. Exact proposal published at606351c2074c9ce340cec29cd518ce0c672ad5af. Execution follows the separately recorded explicit approval and exact matrix adoption, with all original gates. See USER_APPROVED_DWT_RESOURCE_RETRY.json for authority.
