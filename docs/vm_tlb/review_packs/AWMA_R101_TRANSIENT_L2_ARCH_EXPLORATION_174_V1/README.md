# AWMA R101 transient-L2 architecture exploration — 174 V1

Status: `PREP_COMPLETE_AWAITING_FORMAL_INPUT`.

Producer-independent work is complete:

- accepted baseline/source/L2-writeback audit;
- isolated candidate build;
- default-OFF exact smoke;
- ten directed transient-policy tests plus accepted regressions;
- O1 and M1 opt-in implementation;
- strict producer admission/derived-sidecar consumer.

Formal B0/O1/M1 results are intentionally absent until the 109 producer branch
publishes `R101_TRANSIENT_SIM_CAPTURE_PASS` and independent hash/admission
passes. No simulator parameter is tuned to Native numbers.

Primary files at this checkpoint are `SIMULATOR_SCOPE_REQUALIFICATION.md`,
`TRANSIENT_REGION_CONTRACT.md`, `M1_DESIGN_AND_COST.md`,
`M1_DIRECTED_TESTS.tsv`, and `TRANSIENT_L2_CORE.patch`.
