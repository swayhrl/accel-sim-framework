# C16 measurement-campaign design V1

This is a CPU-only **design**, not a capture authorization. Canonical predecessor: `C16_PROBLEM_DISCOVERY_V2_CURRENT_STATE.md` at `9759c08f3bb6e9abd134591007a27ed5bf8c23b1`; its zero qualified problems, zero active candidates and zero experiment authorizations remain unchanged.

Read `FINAL_DECISION.json`, `C16_MEASUREMENT_CAMPAIGN_RATIONALE.md`, `PRIMARY_DISCOVERY_QUESTIONS.md`, then `MEASUREMENT_POINT_PLAN.tsv` and the holdout/budget/stage documents. Eight pre-registered points address four discovery questions. Each point has a parent natural request scope, strong-baseline gate, possible oracle or authority gap, STOP condition and GPU-active reservation. The first proposed native platform is 109 RTX4080/SM89, **only after separate review and explicit authorization**.

`build_campaign_tables.py` generates all eight TSVs. `test_campaign_design.py` checks joins, coverage, holdout, closed-direction guards, budget, and fail-closed state. `DETERMINISTIC_RERUN_RECEIPT.json` records a byte-identical regeneration. No model was downloaded and no GPU, NCU, NVBit, SASS or Accel-Sim work was run.
