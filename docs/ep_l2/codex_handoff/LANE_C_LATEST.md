# Lane C Latest — L1 Causality / Headroom

Status: `LOCAL_SCREEN_COMPLETE_PENDING_D512_PREFLIGHT_PROMOTION`.

All D256 and D512 Lane-C interaction runs are complete in isolated result
roots. D256 META-HR and BANK-HR are accepted: no META-HR workload met the
mandatory material-response trigger, so no one-at-a-time decomposition is
required. D512 META-HR and BANK-HR are locally `COMPLETE_VALID` but retain
`SPECULATIVE_PENDING_GATE` maturity pending Lane B's
`D512_PREFLIGHT_PASS` for Core `878f80869ce212e779df20b6421e4dc7f987825d`
and Framework `aae62b66685f15437cecf0193934f628e6fac6ae`.

`D256_EQ_SCAN_PASS` is already PASS. Do not treat D512 results as calibration
evidence, change the primary L1 baseline, or implement a functional EP-L2
mechanism until the remaining promotion gate is published PASS.

Review pack: `docs/ep_l2/review_packs/L1_CAUSALITY_CALIBRATION_r1/`.
