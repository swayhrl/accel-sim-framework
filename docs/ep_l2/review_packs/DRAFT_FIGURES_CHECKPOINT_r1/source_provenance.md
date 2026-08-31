# Source provenance

All plotted values came only from the current frozen machine-readable CSV products listed in `plotting_tables/SOURCE_ROWS.csv`.

| Figure | Exact CSV inputs |
| --- | --- |
| Figure 1 v2 Panel A | `sector/sector_reuse_summary.csv` |
| Figure 1 v2 Panel B | `sector/sector_reuse_distance.csv` plus the temporal-instance count in sector summary |
| Figure 1 supplement | `motivation/motivation_summary.csv` plus sector summary |
| Figure 2 WBUF=8 | `motivation/blocking_breakdown.csv`, filtered to `wbuf_capacity=8` |

Runtime provenance for every included row is Core `ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919`, Framework `db1c90182fad02aacbd282b67ecdc57b8e4cc365`, and config SHA-256 `6412ba9303d54826739dd474ec234d7b6ca7ece4f25a955c0df211d762ff48c3`. Trace identities are recorded per row in `SOURCE_ROWS.csv`.

The Figure 1 draft render is copied from the just-generated CSV-only draft aggregation for the same complete 13-row formal set; the plotting tables here are regenerated directly from the frozen per-run CSVs and are the review authority.

