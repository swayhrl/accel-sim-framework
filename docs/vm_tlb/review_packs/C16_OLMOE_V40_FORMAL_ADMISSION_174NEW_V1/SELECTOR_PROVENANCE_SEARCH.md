# Receiver-side bounded selector provenance search

`historical_hash: 9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33`

## Read-only locations searched

- all visible Git history and current worktree C16 documentation/utilities;
- V38, V39, V39R2, and V40 OLMoE review packs and handoffs;
- node164 `provenance/` and `legacy/` C16 trees available from 174-new;
- exact text/file-name keys: `9d2d4149`, `VARIANT_A_COMPLETE_STATIC_SELECTOR`,
  `COMPLETE_VARIANT_A_STATIC_SELECTED_SET`, `normalized selector`, and `selector SHA`.

## Result

`OPAQUE_HISTORICAL_CHECKSUM_SERIALIZATION_NOT_DURABLY_RETAINED`

No retained script, command, complete selector, or serialization algorithm was
found that itself produces the historical SHA. Existing files contain summary
references; the visible legacy V40 formalizer copies `9d2d...` as an expected
value and is not an historical serializer.

The historical value therefore remains historical provenance only. The future
destination bundle must instead be verified with its literal selector TSV SHA and
the independently implemented `C16_SELECTOR_CANONICAL_V1` authority; neither may
be relabeled as the V38 checksum.
