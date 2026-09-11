# C13 Selective Segment eligibility audit

## Input-only path: rejected with evidence

The frozen V2 registration parser constructs the same descriptor ranges for
both `weight_segment_map::translate()` and
`weight_segment_map::registered_ppn()`.  The latter is the common conventional
PTW modeled-PPN backend.  Therefore deleting or splitting a target descriptor
in the existing registration/map input would also remove its conventional PPN
mapping.  That violates the C13 contract, so an input-only selective map is not
expressible by the existing binary.

## Minimal C13 overlay

Independent Core commit `4f5f2a2583d71e5aee0e5ff59b67e5e6cd7d5be0` adds an
empty-by-default `-gpgpu_vm_weight_segment_exclude_map`.  It parses only
immutable VPN intervals and is consulted only before optional Segment
resolution.  `registered_ppn()` is deliberately unchanged.  Static validation
(`validate_c13_selective_static.py`) passes, and the Core/new binary are frozen
in `C13_COMMAND_MANIFEST.tsv`.

## Sidecar-derived target

Each immutable sidecar has a single flat WEIGHT allocation.  Its
`model.embed_tokens.weight` tensor starts at offset zero and occupies
525,336,576 bytes = 8,016 complete 64 KiB pages.  There is no distinct
`lm_head.weight` tensor in the flat layout; accepted operator attribution
shows final-output traffic intersects `model.embed_tokens.weight`.  C13 thus
excludes the complete shared Embedding/Output range rather than falsely
claiming a final-kernel-only bypass.

The generated artifacts are:

- `C13_PREFILL_EXCLUDE_EMBEDDING_OUTPUT_WEIGHT.tsv` — SHA-256 `3b54b32f…`
- `C13_DECODE1_EXCLUDE_EMBEDDING_OUTPUT_WEIGHT.tsv` — SHA-256 `b95b4504…`

Both ranges are statically proven to be contained in their immutable C12 V2
registration, while the registration artifact itself is untouched.  The replay
validator additionally requires zero Segment mapping mismatches, preserved
marker/telemetry cardinality, PTE conservation, object conservation, and
per-kernel cycle/snapshot conservation.
