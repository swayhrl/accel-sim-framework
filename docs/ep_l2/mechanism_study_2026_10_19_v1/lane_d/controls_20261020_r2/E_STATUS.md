# Lane E2 — Conv controls batch2 running

Original174; T0=1792414193; actual24/40, remaining16, contingency8/8 consumed. Original controller ACTIVE; original registry/lock, maximum2, main61 and all source identities unchanged.

| Accepted MAIN S/F | S cycles | F cycles | S/F |
|---|---:|---:|---:|
| V2_MAIN_cfd_097k_S_F_MAIN61 | 79093 | 79157 | 0.999191480 |
| V2_MAIN_convolutionSeparable_S_F_MAIN61 | 292932 | 291469 | 1.005019402 |
| V2_MAIN_dwt2d_S_F_MAIN61 | 166519 | 167643 | 0.993295276 |
| V2_MAIN_sad_S_F_MAIN61 | 110773 | 109754 | 1.009284400 |

| Accepted control | Anchor cycles | Control cycles | Anchor/control |
|---|---:|---:|---:|
| V2_CONTROL_convolutionSeparable_F_VS_F_MINUS_V_MAIN61 | 291469 | 293463 | 0.993205276 |
| V2_CONTROL_convolutionSeparable_S_VS_W_ONLY_MAIN61 | 292932 | 291525 | 1.004826344 |

W_ONLY E021 and F_MINUS_V E022 independently accepted: realexit0/wait0,714547200instructions,64slice closure. Both result identities/counters sent to D immediately after remote verification. F_MINUS_R E023 and S_COPY_FREE E024 are now running; WV_M/WV_T follow only after batch2 independently accepts. S_COPY_FREE is diagnostic, not hardware throughput.

Cumulative new results3970888304B; old+new18280464688B. Growth since20-start baseline363525720B.6/20GiB generation budgets do not reset after migration.

The exact four-cell DWT/CFD revision is USER APPROVED and target-profile independently qualified (58c54e0). It has NOT been adopted or launched. After all six Conv controls accept and original controller is STOPPED, adopt only those four rows and retain original matrix/history; full1.5GiB reservation and all resource/time/source/input gates remain mandatory. This approval supersedes the old feeder template wording that says proposal-only; the current registry matrix remains original during Conv.

No FWT retry, Vector F retry, Btree promotion, budget refund/extension, main61 mutation or second controller. D new SAD W_ONLY/DWT F_MINUS_R suggestions remain outside this four-cell approval. Start cutoff2026-10-21 18:00 Beijing; intake22:00 unchanged.
