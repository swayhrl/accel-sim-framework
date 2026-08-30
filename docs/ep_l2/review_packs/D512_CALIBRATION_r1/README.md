# D512 Calibration Review Pack r1

Status: **D512_READY + D512_MIRROR_COMPLETE** (2026-08-30).

This pack records the completed 13-workload × 2-variant D512 calibration
campaign. It is promoted calibration evidence, not a `PRIMARY_BASELINE` or a
`BASELINE_DECISION`. Lane B stops at this boundary; no RO/TVD/Unified work is
included.

The 26 rows use one frozen source/config family and have all passed local
completion, parser, terminal-clean, payload-consistency, provenance, D256
equivalence, and D512 preflight gates. `D512_CALIBRATION_COMPARISON.csv`,
`D512_RESOURCE_PRESSURE.csv`, and `D512_TEMPORAL.csv` use the same exact C7e
field semantics as the formal D256 review analyzer.

Key files:

- `FINAL_STATUS.md`: acceptance-gate disposition.
- `D256_EQUIVALENCE.md`, `D256_EQUIVALENCE_STATUS.csv`, and
  `D256_EQ_SCAN_GATE.json`: D256 backward-equivalence lineage.
- `D512_PREFLIGHT.md` and `D512_PREFLIGHT_GATE.json`: natural D512 preflight.
- `D512_RUN_STATUS_26OF26.csv`, `D512_PROVENANCE_AUDIT_26OF26.csv`, and
  `D512_PROMOTION_STATUS.json`: complete promoted-mirror audit.
- `D512_FINAL_FINDINGS.md`: conservative research interpretation.
