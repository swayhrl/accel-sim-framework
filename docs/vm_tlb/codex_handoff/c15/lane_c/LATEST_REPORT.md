# C15 Lane C handoff

`planning_sha`/initial HEAD: `9a755b14b01c5a77a6fc98c2547616e1c490e806`.

Status: `C15_C_SAMPLING_VALIDATION_READY_FOR_FINAL_REVIEW`. The zero-sampling C12 control passed; the frozen cheap primary sampler remains `SAMPLER_NOT_QUALIFIED` for mechanism claims. The final cross-config audit has 432 rows: 426 `INCONCLUSIVE`, 6 `HISTORICAL_SIGN_AGREEMENT_ONLY`, 0 `SIGN_DISAGREEMENT`, and 36 confounded rows (including the 48 predeclared random-seed-envelope rows).

Relative error is presented as both `relative_error_fraction = abs(error/reference)` and `relative_error_percent = 100 * fraction`; the frozen qualification threshold remains fraction `<=0.05` (5%). `TRACE_INFORMED_ORACLE_DIAGNOSTIC_V1` currently uses phase-level uniform N/n expansion, not an operator/layer stratum-specific estimator; its errors cannot prove operator/layer features are useless.

B's committed offline/header-only checkpoint was hash-verified but supplied no native dynamic metric, so no cross-model claim is made. See the Lane-C review pack FINAL_REPORT, MECHANISM_SIGN_AUDIT, and RELATIVE_ERROR_UNITS for receipts and boundaries.
