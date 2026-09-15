# Private export ingest

`PRIVATE_EXPORT_READY.json` was present and independently SHA-verified. Status is `OLD174_PRIVATE_CLOSEOUT_PASS_EXPORTED_PRIVATE_ASSETS`; `private_only_asset_count=5`; source deletion is false; GPU/simulation execution is false. The manifest binds C12 C5 raw (FORMAL baseline and arms), C13 repaired/diagnostic raw (DIAGNOSTIC), C14 dual-path micro-runs (DIAGNOSTIC), C3 control/trace-link inputs (FORMAL provenance), and a C12 PRE_FIX operator scan (PRE_FIX).

The complete export was copied to node164 `private_export/`. Source and exchange staging remain untouched. Destination file hashing was run against the export tree manifest and is recorded in `PRIVATE_DESTINATION_FILE_HASHES.tsv` under the canonical receipts directory. Private C12/C13/C14 payloads are not promoted beyond their manifest statuses.
