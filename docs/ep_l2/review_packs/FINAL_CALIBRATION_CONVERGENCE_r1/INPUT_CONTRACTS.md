# Input contracts and provenance gate

| Cell | Rows | Binding used |
| --- | ---: | --- |
| D256_BASE | 26 | `D256_BASE.json`, formal 26-row direct audit. |
| D512_BASE | 26 | `D512_BASE.json`, promoted 26-row direct audit. |
| D256_META_HR | 7 | V2 contract plus reviewed Lane-C config-delta and promotion evidence. |
| D256_BANK_HR | 7 | V2 contract plus reviewed Lane-C config-delta and promotion evidence. |
| D512_META_HR | 7 | V2 contract plus reviewed Lane-C config-delta and promotion evidence. |
| D512_BANK_HR | 7 | V2 contract plus reviewed Lane-C config-delta and promotion evidence. |

Every contract is V2 and has a PASS config-delta gate. The D256/D512 base
tables retain direct runtime hashes; Lane-C's compact reviewed evidence binds
its retained runner audits/config-file maps to the V2 hash. That distinction is
explicitly encoded in `CALIBRATION_MATRIX_FINAL.csv`.

Result roots: formal D256 `/workspace/worktrees/accel-sim-ep-l2-c7e/docs/ep_l2/target_baseline_results_final_850/`; D512 `/workspace/worktrees/accel-sim-ep-l2-d512/docs/ep_l2/calibration_results/d512_850/speculative_rows/`; D256 L1 `/workspace/results/ep_l2_l1_causality_d256/`; D512 L1 `/workspace/results/ep_l2_l1_causality_d512_speculative/`.
