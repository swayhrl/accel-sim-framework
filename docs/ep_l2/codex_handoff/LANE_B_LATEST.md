# Lane B — Descriptor-512 Calibration

Stage: Descriptor-512 Calibration — Interim 22/26  
Status: `LANE_B_INTERIM_D512_22_OF_26`

| Field | State |
|---|---|
| Frozen D512 Core | `878f80869ce212e779df20b6421e4dc7f987825d` |
| Frozen D512 Framework | `aae62b66685f15437cecf0193934f628e6fac6ae` |
| Runtime composite SHA-256 | `a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416` |
| D256 equivalence | **PASS**: vectorAdd_4M, spmv, and scan; `D256_EQ_SCAN_GATE.json` present |
| D512 preflight | `PENDING_RUNNING_SCAN`; Banked scan is live |
| D512 mirror | 22/26 `COMPLETE_VALID`; 4 live rows |
| Evidence maturity | all completed rows `SPECULATIVE_PENDING_GATE`, dependencies `D256_EQ_SCAN_PASS`, `D512_PREFLIGHT_PASS` |
| >256 telemetry | PASS locally: vectorAdd max/p95 368/339; spmv 403/382 |
| Running jobs healthy | YES at 2026-08-30T12:56:05+08:00; each simulator active, ~99.6% CPU, raw log growing |

The four uncompleted rows are `B0-Banked/scan`, `B0-Legacy/scan`,
`B0-Legacy/3mm`, and `B0-Banked/3mm`. They are not restarted, moved, or
duplicated. `D512_READY` and `D512_MIRROR_COMPLETE` are not declared.

Interim review: `docs/ep_l2/review_packs/D512_CALIBRATION_INTERIM_22OF26_r1/`.
It includes exact provenance audit, D256 equivalence evidence, D512 pressure and
temporal comparisons, and provisional (non-causal) research findings. The
automatic promotion monitor remains responsible for promotion after D512
preflight passes.
