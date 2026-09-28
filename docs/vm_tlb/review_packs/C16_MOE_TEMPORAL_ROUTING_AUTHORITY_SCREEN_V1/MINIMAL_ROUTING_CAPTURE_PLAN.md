# Minimal routing capture plan (not executed)

This plan exists because current authority is insufficient for a three-lineage temporal comparison. It requires separate user authorization before any node109/GPU execution.

## Goal

Capture 32 continuous natural-routing decode steps for each lineage, preferably reusing its accepted S2 input, model revision, prompt/token authority, seed, and runtime environment. Capture all MoE layers when an all-layer router hook has negligible overhead; do not drop to one target layer merely to reduce storage.

For every `(decode_step, layer_id)` record, persist:

- ordered top-k expert IDs and route weights;
- router-input SHA-256 and router-logits SHA-256;
- next-token ID;
- model ID/revision, input authority, zero/one-based decode convention, and seed.

At run level, persist the exact input-token checksum, generated-token checksum, software/runtime identity, status, immutable destination path, file SHA-256 manifest, and positive catalog/transfer receipt.

## Validation gates

1. Exactly 32 unique consecutive decode steps.
2. Every expected MoE layer appears exactly once per step.
3. Every top-k has the configured size, legal IDs, no duplicates, and matching route-weight length.
4. Router-input/logit hashes and token bindings are present for every record.
5. Routing is natural: no forced expert and no model modification.
6. Two CPU-side parsers independently reproduce record counts and canonical sequence hashes before admission.

## Explicit non-goals

No NVBit, NCU, SASS trace, model download, weight copy, forced routing, cache/TLB mechanism, LRU simulation, or timing claim. NSYS is unnecessary unless a later authority review specifically requires launch identity. This document authorizes no capture by itself.
