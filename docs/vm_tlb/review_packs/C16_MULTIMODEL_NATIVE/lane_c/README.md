# C16 Lane C review pack

Read `FINAL_REPORT.md`, `ENV_PREFLIGHT.json`, `STRATA_DEFINITION.json`, `PROSPECTIVE_PROTOCOL.json`, `P_EVENT_CONSUMPTION_CONTRACT.md`, and `SAMPLER_QUALIFICATION.tsv` first.  `SELECTOR_R_PLAN.tsv` and `SELECTOR_M_PLAN.tsv` are alternative, intentionally separate plans.  Historical tables are `RETROSPECTIVE_ORACLE_CALIBRATION` only.  P is consumed only through the exact-status, exact-commit, hash-closed train→freeze→AWQ route implemented by `c16_sampling_v2.py --freeze-p-train` then `--apply-p-awq-holdout`; live partial data are never read.
