# Round-1 Early Sanity Audit review pack

Commit: `2c161c5`

Archive: `round1_early_sanity_2c161c5.tar.gz`

Included artifacts:

- `ROUND1_EARLY_SANITY_REPORT.md`
- `ROUND1_EARLY_SANITY_TABLE.tsv`
- four `round1_early_sanity/*.csv` matrices
- the parser-only reparse utility and the audit utility
- the parser/runner changes that preserve recorded source provenance and emit
  `NA` for a zero blocker denominator

The canonical per-run `raw.log`, `summary.csv`, `slice.csv`, `window.csv`,
and `manifest.json` files remain in `round1_results/`. They are not duplicated
in this compact review pack; they are large, ignored campaign artifacts and
are referenced by the audit table.
