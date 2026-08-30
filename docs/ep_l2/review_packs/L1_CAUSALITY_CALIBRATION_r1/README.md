# L1 Causality Calibration r1

Status: `L1_CAUSALITY_SCREEN_COMPLETE`.

Lane C completed all 28 isolated B0-Banked runs: D256 META-HR/BANK-HR
and D512 META-HR/BANK-HR, seven selected workloads each. D256 is accepted.
Lane B subsequently published `D512_PREFLIGHT_PASS`, `D512_READY`, and
`D512_MIRROR_COMPLETE` for the exact recorded parent; all 14 existing D512
rows were promoted without simulator rerun to `PROMOTED_VALID_CALIBRATION`.

This is a causality screen only. It makes no primary-L1-baseline change and
implements no functional EP-L2 mechanism.

Contents:

- `PROVENANCE.md` — immutable sources, config contracts, and isolation.
- `CAUSAL_ANALYSIS.md` — D256 and provisional D512 conclusions.
- `RUN_STATUS.md` — all local completion state and promotion rule.
- `RAW_LOG_INDEX.md` and `SHA256SUMS` — result-root return path.
- `D256_*` / `D512_*` CSVs — compact copied comparison, classification and
  5K temporal evidence.
- `FINAL_RUN_PROMOTION_STATUS.csv` — per-cell final maturity evidence.
