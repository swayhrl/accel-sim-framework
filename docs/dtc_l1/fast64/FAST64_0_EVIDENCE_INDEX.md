# FAST64.0 Tier-A and Tier-C evidence index

Status: **PIVOT_EVIDENCE_INDEX — NOT A FAST64 PERFORMANCE RESULT**.

This index preserves historical M5 evidence under its original identities.
It does not convert any M5 row into a FAST64 row or mix any historical metric
into `GM-FAST12`.

| tier | evidence | frozen disposition | retained reference |
| --- | --- | --- | --- |
| A | DTC directed/lifecycle/accounting tests and M1-M4 validation | mechanism correctness | Core `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`; M5 DTC specification and review packs |
| A | repaired-Core BICG same-bundle Base/IO/OO | mechanism-fidelity trace replay anchor | M5 `review_packs/M5_0BT_T2_BICG/` and `m5/handoffs/M5_0BT_BICG_T1_REVIEW.md` |
| A | stats-light A1 terminal equivalence | observer-only equivalence anchor | M5 `m5/handoffs/M5_STATS_LIGHT_A1_TERMINAL_EQUIVALENCE.md`; overlay SHA `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e` |
| A | lower-create-queue repair and preserved pre-repair failures | repair correctness / invalidation anchor | Core `15cfa76e...`; M5 issue/handoff evidence |
| A | exact SpMV capture and validated replay evidence | irregular trace-path support | M5 `m5/handoffs/M5_0BT_SPMV_CAPTURE_CLOSEOUT.md` |
| C | large repaired 80-SM ATAX recovery | `BACKGROUND_HEAVY_REPAIR_STRESS` | live auxiliary namespace recorded in `handoffs/FAST64_0_PIVOT.md` |
| C | SYR2K capture/archive/immutable evidence | `DEFERRED_HEAVY_AUXILIARY` | M5 `m5/handoffs/M5_0BT_SYR2K_HEAVY_STORAGE_RECALIBRATION.md` |
| C | 2MM archive-only/receipt evidence | `DEFERRED_HEAVY_AUXILIARY` | retained `/workspace/m5-trace-immutable/2mm/2mm.tar.zst`; M5 `m5/handoffs/M5_0BT_2MM_STORAGE_ADMISSION_STOP.md` |
| C | Extended-20 E1 source formalization | `DEFERRED_OPTIONAL_GENERALIZATION` | M5 `m5/extended20/` and associated handoffs |

## Non-reuse rule

Tier-A evidence may establish mechanism and observer confidence.  Tier-C
evidence may support robustness discussion.  Neither can be numerically reused
as a FAST64 primary result unless every FAST64 formal identity field matches,
which is not claimed here.
