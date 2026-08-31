# Frozen source provenance

The generator verifies each workload's paired `EPL2B0V1` and `EPL2MOTV1`
manifests before reading the plotted CSVs.  The pair must agree on Core commit,
Framework commit, and source-log SHA-256; all seven selected workloads must also
share the same Core and Framework runtime commits.  Exact CSV paths and hashes
are exported in `plotting_tables/frozen_source_csv_sha256.csv`.

Validated runtime provenance:

* Core: `ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919`
* Framework: `db1c90182fad02aacbd282b67ecdc57b8e4cc365`
* B0 schema: `EPL2B0V1`
* Motivation schema: `EPL2MOTV1`

Only these frozen CSV families are plotted:

* `b0/target_slice.csv` for utilization/occupancy proxies;
* `motivation/blocking_breakdown.csv`, filtered to `wbuf_capacity=8`, for the
  exclusive blocker figure.
