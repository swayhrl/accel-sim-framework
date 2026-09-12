# C16 Lane C — Sampling V2 checkpoint

Status: `C16_C_SAMPLING_V2_READY_FOR_REVIEW` for offline implementation and retrospective oracle calibration; prospective qualification is pending a committed Wave-1 native catalog.  The selector has fixed Phase × Operator × Implementation × ShapeBucket × DType strata, certainty-unit weight 1, separately published probability (`Selector-R`) and medoid (`Selector-M`) plans, and 12/24/48 per deployment/scenario/phase alternative budgets.

C12/C13 are read-only `RETROSPECTIVE_ORACLE_CALIBRATION`; C13 mode=1 is rejected.  Historical operator fields are oracle-only.  `HISTORICAL_STRUCTURAL_OBSERVATIONS.tsv` reports only sampled modeled-SimVA page sets by stratum; no page/line union is extrapolated with N/n.  No GPU, native profiler, trace capture, or simulator replay was started.

No Wave-1 committed G catalog exists at publication, so `NVBIT_TARGET_PLAN.tsv` deliberately has no historical capture target.  The prospective protocol freezes selector code, strata, seed, budgets, deployment split and thresholds before any holdout metric may be read.  Qualification is metric-by-metric; there is no overall PASS.
