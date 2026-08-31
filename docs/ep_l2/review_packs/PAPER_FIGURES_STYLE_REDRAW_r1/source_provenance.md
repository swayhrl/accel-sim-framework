# Source provenance

The two figures directly read the review-ready plotting tables in
`../UTILIZATION_QUICKLOOK_r1/plotting_tables/`:

* `A1_A2_utilization_hotspot_table.csv` for Figure 1S;
* `B_blocking_wbuf8_subset.csv` for Figure 2.

Their source-path SHA-256 records are exported in
`plotting_tables/source_table_sha256.csv`.  The redraw script validates the
seven-workload order, the 7 x 4 utilization table shape, and exact Figure-2
primary-blocker closure before rendering.

The current quicklook itself records the frozen runtime provenance as Core
`ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919` and Framework
`db1c90182fad02aacbd282b67ecdc57b8e4cc365`.
