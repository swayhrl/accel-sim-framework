# D512 Calibration — Interim 22/26 Review Pack r1

Status: `LANE_B_INTERIM_D512_22_OF_26` (snapshot: 2026-08-30T12:56:05+08:00).

This is an evidence snapshot of the 22 locally valid rows available while four
frozen D512 simulations continue. It is not a final mirror, a primary baseline,
or a baseline decision. `COMPLETE_VALID` is local completion only; every D512
row in this pack remains `SPECULATIVE_PENDING_GATE` until the D512 preflight
gate passes and the automatic promotion monitor records promotion.

Contents:

- `D256_EQUIVALENCE.md` and `D256_EQUIVALENCE_STATUS.csv`: B3 evidence.
- `D512_PREFLIGHT_INTERIM.md`: required-preflight state and >256 validation.
- `D512_RUN_STATUS_22OF26.csv` and `D512_PROVENANCE_AUDIT_22OF26.csv`: state
  and machine-readable provenance audit.
- `D512_INTERIM_COMPARISON.csv`, `D512_INTERIM_RESOURCE_PRESSURE.csv`, and
  `D512_INTERIM_TEMPORAL.csv`: exact-field D256/D512 comparisons for completed
  rows.
- `RUNNING_JOBS_SNAPSHOT.csv`: read-only health snapshot of the four live jobs.

The analyzer imports the `run_record` field semantics from the checked-in C7e
final-review analyzer. It does not reinterpret coarse `block_*` values.
