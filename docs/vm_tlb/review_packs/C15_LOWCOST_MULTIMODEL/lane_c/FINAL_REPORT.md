# C15 Lane C final report

Status: `C15_C_SAMPLING_VALIDATION_READY_FOR_FINAL_REVIEW`. The 22-arm C12 zero-sampling conservation control passed using hash-verified historical raw logs; corrected C13 admitted only the ten EQ-gated mode=0 identities. No simulator replay, trace capture, GPU task, Core change, or protected-source write occurred.

The released primary is a phase/opaque-order cheap selector with seed 15001 and virtual budgets 8/12/24/48. It intentionally has explicit UNKNOWN operator/implementation/shape/dtype/KV/TP buckets. The historical operator/layer/page scan is an oracle only, never the primary selector. Historical C12/C13 outcomes are retrospective calibration/cross-config tests, not blind tests.

Primary cycle relative-error presentation (fraction; percent): prefill B8/B12/B24/B48 = 48.1870458711 / 32.8033034749 / 15.8636227043 / 8.30290448691; 4818.7046% / 3280.3303% / 1586.3623% / 830.2904%. Decode B8/B12/B24/B48 = 19.4859168735 / 12.6388018008 / 5.9501609825 / 3.29451020821; 1948.5917% / 1263.8802% / 595.0161% / 329.4510%. The frozen screening threshold remains fraction `<=0.05` (5%) and none of these presentation changes alters a verdict.

The final cross-config table has 432 rows: 426 `INCONCLUSIVE`, 6 `HISTORICAL_SIGN_AGREEMENT_ONLY`, 0 `SIGN_DISAGREEMENT`, and 36 explicitly confounded rows. This includes 48 predeclared random-seed-envelope rows added after the initial 384-row sign audit.

Scientific boundary: the cheap selector is `SAMPLER_NOT_QUALIFIED` for mechanism or causal conclusions; deterministic estimates have no fabricated confidence interval, and small or unresolved effects are `INCONCLUSIVE`. `TRACE_INFORMED_ORACLE_DIAGNOSTIC_V1` currently uses phase-level uniform N/n expansion, not an operator/layer stratum-specific estimator; its errors cannot prove operator/layer features are useless. Existing compact scans support exact 64KiB page-set fingerprints, but not bytes, read/write/atomic, line-set, MRC, private-L1, or global-order claims. C14 cold micro comparisons remain confounded by explicit state/context non-equivalence.

Lane B commit `8963919d608d05713e2caa22965d8895c728bc92` was consumed read-only after manifest validation: all 21 payload hashes matched, but its declared state is `NO_NEW_NATIVE_GPU_RUN` and its catalog is header-only. No dynamic metric was imported; dynamic cross-model validation therefore remains pending a future committed native manifest.
