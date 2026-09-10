# C12 C5 full-ROI fair performance replay

Status: `C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`

- primary matrix: 22/22 terminal PASS
- Core: `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- binary SHA-256: `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`
- functional/config anchor: `d64408a97d76a320a6d49468653d416e33677af8`
- labels: `SPECULATIVE_CANDIDATE`, `REFERENCE_APPROX_SUBENTRY_16`

All numerical comparison tables are machine-readable in the accompanying TSV files.  The report intentionally does not infer causality from a single telemetry counter.

## Required comparison coverage

- F1 vs F2: `COMPARISON_ANALYSIS.md` + `TRANSLATION_MECHANISM_SUMMARY.tsv`
- F5 vs F0: `COMPARISON_ANALYSIS.md` + `CROSS_LAYER_SUMMARY.tsv`
- F7 L5/L10/L20 and F8 L5/L10/L20: `COMPARISON_ANALYSIS.md` + `LSEG_SENSITIVITY.tsv`
- F8-L10 vs F9 / F1 and Prefill vs Decode: `COMPARISON_ANALYSIS.md`.

`COMPARISON_ANALYSIS.md` mechanically presents the required multi-layer deltas while keeping measured facts, supported mechanism signals, and unresolved questions separate.
