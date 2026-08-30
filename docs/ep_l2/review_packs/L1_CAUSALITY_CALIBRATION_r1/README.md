# L1 Causality Calibration r1

Status: `LOCAL_COMPLETE_AWAITING_D512_PREFLIGHT_PASS`.

Lane C completed all 28 isolated B0-Banked runs: D256 META-HR/BANK-HR
and D512 META-HR/BANK-HR, seven selected workloads each. D256 is locally
accepted. D512 rows are locally `COMPLETE_VALID` but remain
`SPECULATIVE_PENDING_GATE` until Lane B publishes `D512_PREFLIGHT_PASS` for
the exact frozen candidate recorded in `PROVENANCE.md`.

This is a causality screen only. It makes no primary-L1-baseline change and
implements no functional EP-L2 mechanism.

Contents:

- `PROVENANCE.md` — immutable sources, config contracts, and isolation.
- `CAUSAL_ANALYSIS.md` — D256 and provisional D512 conclusions.
- `RUN_STATUS.md` — all local completion state and promotion rule.
- `RAW_LOG_INDEX.md` and `SHA256SUMS` — result-root return path.

