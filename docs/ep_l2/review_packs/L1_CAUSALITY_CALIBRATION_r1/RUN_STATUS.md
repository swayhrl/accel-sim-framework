# Run Status and Promotion Contract

| Cell | Rows | Local state | Promotion state |
|---|---:|---|---|
| D256 META-HR | 7/7 | `COMPLETE_VALID` | accepted |
| D256 BANK-HR | 7/7 | `COMPLETE_VALID` | accepted |
| D512 META-HR | 7/7 | `COMPLETE_VALID` | `SPECULATIVE_PENDING_GATE` |
| D512 BANK-HR | 7/7 | `COMPLETE_VALID` | `SPECULATIVE_PENDING_GATE` |

D256 scan terminal cycles: META-HR `2,151,187`; BANK-HR `2,160,489`.
D512 scan terminal cycles: META-HR `2,149,591`; BANK-HR `2,165,543`.

Promotion requires both `D256_EQ_SCAN_PASS` and `D512_PREFLIGHT_PASS`, with
the exact Core/Framework/config/trace identity in `PROVENANCE.md`. The first
gate is PASS. Until the second is explicitly published PASS by Lane B, no
D512 result in this pack is calibration evidence.

