# Run Status and Promotion Contract

| Cell | Rows | Local state | Promotion state |
|---|---:|---|---|
| D256 META-HR | 7/7 | `COMPLETE_VALID` | accepted |
| D256 BANK-HR | 7/7 | `COMPLETE_VALID` | accepted |
| D512 META-HR | 7/7 | `COMPLETE_VALID` | `PROMOTED_VALID_CALIBRATION` |
| D512 BANK-HR | 7/7 | `COMPLETE_VALID` | `PROMOTED_VALID_CALIBRATION` |

D256 scan terminal cycles: META-HR `2,151,187`; BANK-HR `2,160,489`.
D512 scan terminal cycles: META-HR `2,149,591`; BANK-HR `2,165,543`.

Promotion required both `D256_EQ_SCAN_PASS` and `D512_PREFLIGHT_PASS`, with
the exact Core/Framework/config/trace identity in `PROVENANCE.md`. Both gates
are PASS. Lane B's fanout handoff additionally records `D512_READY` and
`D512_MIRROR_COMPLETE` for Core `878f80869ce212e779df20b6421e4dc7f987825d`
and Framework `aae62b66685f15437cecf0193934f628e6fac6ae`. The Lane-C
promotion manifest records workboard commit `454264f8e74e6c72126f4efabad793ada2bdd031`
and 14 promoted rows; no simulator was rerun.
