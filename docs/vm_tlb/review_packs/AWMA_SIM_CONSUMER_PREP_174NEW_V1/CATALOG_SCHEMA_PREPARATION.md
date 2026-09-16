# Catalog and schema preparation

Draft 2020-12 JSON Schemas now define closed records for `SIM_INPUT`,
`SIM_BASELINE`, `SIM_RUN`, and `SIM_EVIDENCE`. String type constraints accompany
all hash/ID patterns. `identity_for()` uses the same required semantic fields
and canonical sorted compact JSON, excluding only formal ID fields, before
SHA256 and the record-kind prefix are applied.

`catalog_put()` is create-once and idempotent only for byte-identical content;
same-ID mutation fails. The four Schema files are closed by
`SCHEMA_SET_RECEIPT.json`.

No current-model `SIM_INPUT_ID`, `SIM_RUN_ID`, or `SIM_EVIDENCE_ID` exists in
this checkpoint. `EXPECTED_FIRST_CURRENT_MODEL_INPUT.json` is explicitly a
pending contract template and is not a catalog entry.
