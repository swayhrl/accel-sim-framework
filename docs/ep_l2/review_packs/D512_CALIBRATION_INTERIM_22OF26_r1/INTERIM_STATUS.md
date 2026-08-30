# Interim status

`D256_EQ_SCAN_PASS` is **PASS**. The generalized D256 candidate reproduces the
formal C7e results for `vectorAdd_4M`, `spmv`, and long `scan` exactly across
seven parsed artifacts per workload. The machine-readable gate is included as
`D256_EQ_SCAN_GATE.json`.

`D512_PREFLIGHT_PASS` is **PENDING_RUNNING_SCAN**. Banked `vectorAdd_4M`,
`spmv`, `FWT_7_21`, and low-pressure `sad`, plus the Legacy `vectorAdd_4M`
paired control, are `COMPLETE_VALID`. The required Banked `scan` is live;
therefore B6, `D512_READY`, and promotion cannot be declared.

Mirror state is **22/26 COMPLETE_VALID, 4/26 RUNNING**. The completed rows are
provenance-audited and analysis-ready locally, but their maturity is
`SPECULATIVE_PENDING_GATE` with dependencies
`D256_EQ_SCAN_PASS;D512_PREFLIGHT_PASS`. No row is promoted by this snapshot.

Do not infer a final conclusion from the four absent rows: `B0-Banked/scan`,
`B0-Legacy/scan`, `B0-Legacy/3mm`, and `B0-Banked/3mm`.
