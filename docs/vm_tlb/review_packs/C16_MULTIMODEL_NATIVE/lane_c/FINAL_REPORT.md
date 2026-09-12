# C16 Lane C — Sampling V2 checkpoint

Status: `C16_C_SAMPLING_V2_READY_FOR_REVIEW` for offline implementation and retrospective oracle calibration; prospective qualification is pending a committed P-ready native catalog.  The selector has fixed Phase × Operator × Implementation × ShapeBucket × DType strata, certainty-unit weight 1, separately published probability (`Selector-R`) and medoid (`Selector-M`) plans, and 12/24/48 per deployment/scenario/phase alternative budgets.

C12/C13 are read-only `RETROSPECTIVE_ORACLE_CALIBRATION`; C13 mode=1 is rejected.  Historical operator fields are oracle-only.  `HISTORICAL_STRUCTURAL_OBSERVATIONS.tsv` reports only sampled modeled-SimVA page sets by stratum; no page/line union is extrapolated with N/n.  No GPU, native profiler, trace capture, or simulator replay was started.

P may be admitted only at `C16_P_NATIVE_CATALOG_READY_FOR_C_CONSUMPTION` with exact commit/hash closure.  C first consumes only the direct Llama/Qwen0.5/Qwen7-raw train roster, audits schema/join, freezes source SHA plus strata/threshold/seed/budget rules and all 12/24/48 plans, then separately unseals Qwen7-AWQ cheap catalog.  It reads no NCU/NVBit outcome, treats UNKNOWN semantic fields as explicit strata, and publishes a bounded request-only target plan immediately after AWQ application.  Qualification remains metric-by-metric; there is no overall PASS.
