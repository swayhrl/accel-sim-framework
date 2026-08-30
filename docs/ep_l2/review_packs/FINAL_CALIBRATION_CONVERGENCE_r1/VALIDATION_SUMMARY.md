# Validation summary

- Six V2 contracts have schema/cell/PASS config-delta gates checked.
- D256/D512 direct formal/promoted provenance checks cover 26 + 26 rows.
- Lane-C consumes only reviewed config-delta and promotion evidence; the
  non-direct binding is explicit rather than silently presented as raw hash.
- Matrix has 80 rows; archetype CSV has 13 unique workloads; native summary
  has 52 final-complete 32-channel base rows.
- Lane-D V3 status-audit hash-location bug fix has 18 passing tests.
- No simulator/rebuild/result-root write occurred.

Completion: `FINAL_CALIBRATION_CONVERGENCE_REVIEW_READY`, not
`BASELINE_DECISION_PASS`.
