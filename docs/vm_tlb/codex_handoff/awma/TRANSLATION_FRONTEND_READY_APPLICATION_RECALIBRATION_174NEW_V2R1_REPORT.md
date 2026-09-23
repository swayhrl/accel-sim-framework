# Translation Frontend READY-Application Recalibration V2R1

V2R1 repairs the pre-repair V2 READY-retention bookkeeping defect using the accepted V1 `consume_ready` API. In V1 prelaunch remains observe-only; V2R1 prelaunch consumes READY and applies its PA/outcome to the exact resident access.

| T2 point | cycles | GPU instructions | CTA | full controller quiescence |
| --- | ---: | ---: | ---: | --- |
| V2R1 10/80 | 111607 | 43357696 | 1216 | PASS |
| V2R1 0/80 | 71743 | 43357696 | 1216 | PASS |

Both points have full UID coverage, no untranslated/unobserved UID, no duplicate application, dormant Segment F0, `m_lookups=0`, `LOOKUP_READY=0`, empty MSHR/PWQ, no active walk, and `quiescent_invariants_hold=true`.

Residual sensitivity is 35.7182%. Final classification: `READY_APPLICATION_HOL_NOT_PRIMARY`.

The pre-repair V2 publication remains preserved as `PRE_REPAIR_READY_RETENTION_INVALID_FOR_FINAL_CLASSIFICATION`. No T0/T1, Native calibration, or new translation mechanism was run.
