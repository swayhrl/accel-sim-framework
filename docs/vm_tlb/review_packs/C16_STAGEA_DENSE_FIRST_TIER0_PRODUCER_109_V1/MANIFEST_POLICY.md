# Manifest policy

`RAW_PAYLOAD_SHA256SUMS` covers the immutable scientific/raw payload and `RAW_INDEX.tsv`, excluding only the final decision and manifest files to avoid self-reference. Its SHA256 is the `durable_raw_manifest_sha256` recorded in `FINAL_DECISION.json`.

`REVIEW_PAYLOAD_SHA256SUMS` covers the review payload before the final decision and publish receipt; its SHA256 is `review_pack_sha256`. `RAW_SHA256SUMS` and `SHA256SUMS` are the final non-self-referential full-directory manifests.
