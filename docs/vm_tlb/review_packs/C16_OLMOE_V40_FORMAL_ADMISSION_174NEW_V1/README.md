# C16 OLMoE V40 174-new Authority Admission

## Current decision

`PENDING_BUNDLE` ¡ª dependency-free receiver preparation is complete; no matching
OLMoE V40 Pipeline V1 `.partial` exists in either current node164 inbox layout.
This is not a scientific PASS or an admission decision.

## Frozen scope

- `allenai/OLMoE-1B-7B-0125-Instruct` at `b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`
- S2_TEXT, B1/T2048/D32; layer1 decode32 natural expert58 `down_proj`
- actual-JIT variant A only; variant B remains unformalized
- 243 selected statics, with historical `9d2d...` retained only as an opaque checksum

## Bundle-dependent artifacts (not yet generated)

- destination transport verification receipt
- selector authority verification receipt
- independent 243-shard recompute receipt and producer delta
- immutable admission/catalog snapshot receipt
- positive ACK
- final authority decision and third-lineage handoff

The only allowed transition out of this state is a matching bundle manifest,
destination verification, independent CPU recompute, serial immutable admission,
and then a schema-valid positive ACK.
