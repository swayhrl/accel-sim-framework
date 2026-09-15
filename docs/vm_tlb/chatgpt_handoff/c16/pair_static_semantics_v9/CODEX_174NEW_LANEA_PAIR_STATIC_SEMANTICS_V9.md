# CODEX 174-new Lane A Goal — C16 Raw7B/AWQ Pair Static Semantics Completion V9

## Accepted base

Start from the accepted Lane A V8 result:

`04448e24b716ef16e13573f7adf9bc291ac777a6`

Suggested branch:

`hrl/c16-pair-static-semantics-174new-laneA-v9`

This is CPU-only and independent of node109 V8 execution. Do not wait for node109.

## Why this Goal exists

Lane A V8 correctly stayed fail-closed and did not promote any raw7B/AWQ causal comparison. However two preparation items remain intentionally incomplete:

1. `PAIR_SEMANTIC_SHAPE_INVENTORY.tsv` is currently a 28-layer × 7-role schema skeleton with `PENDING_CANONICAL_*` values rather than a closed checkpoint-derived semantic inventory.
2. `COMPARATOR_TEST_RESULTS.tsv` reports `replay_missing=FAIL` because the V8 test mutates an AWQ-side field named `raw_replay_equivalence`, while the comparator only applies raw replay equivalence to the raw side. The field semantics and test must be made side-specific and fail-closed.

Do not create a standalone repair-only change. Complete the missing scientific preparation in the same Goal.

## Primary objective

Build a deterministic, checkpoint-derived raw7B/AWQ semantic operator inventory and a side-specific pair comparator V2 so that, once node109 proves the exact AWQ semantic anchor, Lane A can immediately resolve the matching BF16 raw operator without another static-preparation round.

Canonical model identities:

- raw BF16: `Qwen/Qwen2.5-7B-Instruct@a09a35458c702b33eeacc393d103063234e8bc28`
- AWQ: `Qwen/Qwen2.5-7B-Instruct-AWQ@b25037543e9394b818fdfca67ab2a00ecc7dd641`

Use canonical node164 receipts/config/index/safetensors headers as authority. Do not load the full models and do not execute CUDA.

## P0 — Exact 28 × 7 semantic tensor inventory

For every decoder layer `0..27` and semantic linear role:

- `q_proj`
- `k_proj`
- `v_proj`
- `o_proj`
- `gate_proj`
- `up_proj`
- `down_proj`

resolve from checkpoint metadata, not hard-coded placeholders:

### Raw BF16 side

Record at least:

- exact tensor name;
- decoder layer;
- semantic role;
- source shard;
- dtype;
- exact stored shape;
- exact tensor bytes;
- logical `in_features` / `out_features` when proven from config/tensor convention;
- receipt identity.

### AWQ side

For the matching semantic module, resolve all checkpoint tensors that materially define the quantized linear representation, where present, including at least:

- `qweight`;
- `qzeros` / zero-point tensor;
- `scales`;
- `g_idx` or equivalent metadata if present;
- bias if present;
- any other exact checkpoint tensor required by this archived AWQ representation.

Record:

- exact tensor names;
- source shard;
- dtype;
- exact stored shape;
- exact bytes;
- aggregate quantized checkpoint bytes for the semantic linear;
- logical dense operator dimensions only when independently proven from config/module metadata;
- explicit encoding/layout basis.

Do not infer packed-qweight orientation merely from a visually plausible shape. If an exact logical dimension cannot be proven from archived config/source/runtime metadata, record `UNRESOLVED` and the missing proof.

## P1 — Static storage comparison

For each matched semantic linear, compute only checkpoint/static quantities that are legitimately comparable, such as:

- BF16 weight bytes;
- AWQ qweight bytes;
- AWQ qzero bytes;
- AWQ scale bytes;
- other quant metadata bytes;
- total AWQ checkpoint bytes for the semantic linear;
- raw/AWQ static-storage ratio.

This is **not** runtime memory traffic, GPU memory residency, cache traffic, or a performance claim.

Output a clear scope label:

`CHECKPOINT_STATIC_STORAGE_ONLY`

## P2 — Semantic anchor lookup for node109 output

Prepare a deterministic lookup table that maps any producer-proven semantic anchor of the form:

`decoder layer + linear role`

to:

- raw BF16 tensor identity;
- AWQ checkpoint tensor identities;
- proven logical operator dimensions;
- static storage summary;
- whether a one-to-one semantic pair is closed.

Do not claim the current V6 AWQ formal target belongs to any layer/role until node109 V8 proves it.

Current status must remain:

`AWQ_FORMAL_SEMANTIC_ANCHOR_PRODUCER_PREREQUISITE`

## P3 — Pair comparator V2

Replace the ambiguous V8 comparator semantics with explicit side-specific fields.

The comparator must fail closed unless all required pair gates are present and valid.

At minimum require:

### Common identity

- model family identity;
- exact common token-sequence SHA;
- exact semantic layer id;
- exact semantic linear role;
- logical operator dimensions / runtime shape identity required by the pair contract;
- phase scope.

### Raw side

- raw revision;
- raw target-layer-state identity;
- raw replay equivalence = `PASS`;
- raw kernel-signature equivalence = `PASS`;
- raw formal path coverage = `ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL`.

### AWQ side

- AWQ revision;
- producer-proven semantic anchor = `PASS`;
- AWQ deployment identity;
- AWQ formal path coverage = `ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL`.

### NCU comparison

NCU values are optional for pair admissibility, but if both sides provide NCU evidence, reject metric-level comparison when their semantic descriptors differ, including at least:

- cache-control;
- replay mode;
- target semantic operator identity;
- metric definition/unit.

Never invent missing numeric values.

### Tests

Tests must explicitly cover and PASS rejection for:

- missing token identity;
- token mismatch;
- layer mismatch;
- role mismatch;
- logical operator/shape mismatch;
- missing raw replay equivalence;
- raw replay equivalence != PASS;
- missing raw kernel-signature equivalence;
- missing AWQ producer semantic anchor;
- missing/invalid raw coverage;
- missing/invalid AWQ coverage;
- incompatible NCU semantics;
- deterministic identical-input result.

The V8 `replay_missing=FAIL` must not remain as an unexplained passing artifact.

## P4 — Bounded target recommendation

Use only static semantics to rank ordinary decoder-layer MLP linears (`gate_proj`, `up_proj`, `down_proj`) as potential future pair candidates.

The recommendation may use:

- one-to-one semantic clarity;
- checkpoint shape/storage clarity;
- expected ease of node109 semantic anchoring;
- absence of architecture-specific ambiguity.

Do **not** freeze a layer id or role before node109 proves the AWQ formal semantic anchor.

The final recommendation must remain conditional, for example:

`SELECT_MATCHED_MLP_LINEAR_AFTER_PRODUCER_ANCHOR`

## Existing evidence boundaries to preserve

AWQ same-process address contexts remain valid, but without a lossless event-to-range join do not promote per-event object attribution. Preserve `UNKNOWN_RUNTIME`.

Do not create:

- cross-shard absolute VA union;
- cross-deployment absolute VA comparison;
- temporal ordering across shards;
- reuse distance;
- runtime cache/TLB claims from checkpoint storage;
- raw7B-vs-AWQ causal conclusions before node109 pair qualification.

## Implementation

Prefer reusable CPU-only helpers under:

`util/vm_tlb/c16/analysis/`

or another clearly scoped C16 directory.

Fail closed on:

- missing indexed tensor;
- duplicate tensor;
- unexpected archived tensor role;
- unresolved revision;
- shape/dtype inconsistency;
- ambiguous AWQ quant representation that cannot be proven.

Large model bytes remain on node164; Git gets compact deterministic evidence only.

## Review pack

Create:

`docs/vm_tlb/review_packs/C16_PAIR_STATIC_SEMANTICS_174NEW_LANEA_V9/`

Include at least:

- `README.md`
- `FINAL_DECISION.json`
- `RAW7B_AWQ_SEMANTIC_TENSOR_INVENTORY.tsv`
- `RAW7B_AWQ_STATIC_STORAGE_COMPARISON.tsv`
- `PAIR_SEMANTIC_ANCHOR_LOOKUP.tsv`
- `PAIR_COMPARATOR_V2_CONTRACT.json`
- `PAIR_COMPARATOR_V2_TEST_RESULTS.tsv`
- `TARGET_RECOMMENDATION.md`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Expected success label:

`C16_PAIR_STATIC_SEMANTICS_174NEW_LANEA_V9_PASS`

Use `PASS_WITH_GAPS` if some AWQ logical dimension/encoding cannot be proven from the canonical archived authorities. Do not guess to obtain PASS.

Commit/push and STOP.