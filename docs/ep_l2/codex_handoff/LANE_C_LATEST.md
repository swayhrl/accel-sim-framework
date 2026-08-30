# Lane C Latest — L1 Causality / Headroom

Status: `L1_CAUSALITY_SCREEN_COMPLETE`.

All D256 and D512 Lane-C interaction runs are complete in isolated result
roots. D256 META-HR and BANK-HR are accepted: no META-HR workload met the
mandatory material-response trigger, so no one-at-a-time decomposition is
required. Lane B published `D512_PREFLIGHT_PASS`, `D512_READY`, and
`D512_MIRROR_COMPLETE` for the exact matching candidate Core
`878f80869ce212e779df20b6421e4dc7f987825d` and Framework
`aae62b66685f15437cecf0193934f628e6fac6ae`. All 14 existing D512 interaction
rows are now `PROMOTED_VALID_CALIBRATION` without rerun.

Four `EP_L2_CALIBRATION_CONTRACT_V2` contracts and compact comparison/temporal
tables are published in the review pack. The screen does not change the
primary L1 baseline or authorize functional EP-L2 work.

Review pack: `docs/ep_l2/review_packs/L1_CAUSALITY_CALIBRATION_r1/`.
