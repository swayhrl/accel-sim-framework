# Open issues

- No V2 shard has arrived at node164, so both indexes are intentionally
  `READY_FOR_INCREMENTAL_INGEST`, not evidence claims.
- No node109 compact binary format specification/version has been frozen.  The
  implementation will fail closed until a source manifest supplies one.
- A shard union is not a temporal stream.  Cross-shard/global order and reuse
  distances remain mechanically absent from aggregate outputs.
- Existing RTX3090 Q2 fixtures remain parser regression anchors only; they do
  not establish V2 coverage or cross-model conclusions.
