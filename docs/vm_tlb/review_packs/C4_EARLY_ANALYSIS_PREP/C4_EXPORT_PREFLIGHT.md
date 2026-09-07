# C4 structured-export preflight

Seven terminal arms were exported sequentially at idle CPU/I/O priority from
their existing run logs. For every arm, all 11 expected exporter outputs are
present. TSV headers and the first provenance-bearing record match the original
arm manifest; the detailed check is in `C4_EXPORT_PREFLIGHT.tsv`.

`C4_EARLY_VALIDATION.tsv` records PASS for the seven terminal gates and export
schema/provenance. Replay is explicitly `NOT_PERFORMED`; prefill-paper is
`PENDING`. The C4 final consumer can read the generated schema, while full
per-kernel aggregation is intentionally deferred until the eighth arm ends.
