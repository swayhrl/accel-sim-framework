# Shared export-manifest reference

The exported payload is intentionally retained outside Git at:
`/root/share/c12_c15_inheritance_exchange_v1/old174_private_export/`.

Its control-plane records are hash-bound as follows:

- `PRIVATE_EXPORT_MANIFEST.tsv`:
  `62564e06565be02ca63bf6fc3ce36c2df2a3adc2d23c619d73885c448bc1b6d4`
- `PRIVATE_EXPORT_TREE_MANIFEST.tsv`:
  `e03b1e3f757fcc053255de572f828e1774d5a0b0d6422c1a8c5e4628dfbdc3b3`
- `PRIVATE_EXPORT_READY.json`:
  `32dff6170ccf6172c0ebac2c8af0a0131c962d1dabe7349993f510742e046c0d`
- `PRIVATE_EXPORT_SHA256SUMS`:
  `f2ae361e43f540fbd46fba557482a57039b61ddb7af4d90351a3219c319a9b66`

The exchange checksum file covers the two per-side manifests for each of the
five payloads, in addition to all exchange control-plane records.  The Git
review pack retains the classification and lineage, but no raw payload bytes.
