# C16 174-new Lane A — AWQ Consumer Analysis V7 Scope

Accepted Lane A base:

`cff4b238c5c98c09b5eda96f3e1df4e1d78b57d3`

Accepted node109 AWQ producer authority:

`2274ee94c86cac9d37f7ef60c8afee58f8fc74b8`

Lane B is independent and currently starts from:

`794b8426b64c9b0f142ff2e0ddb4e7ac198b7acb`

Do not modify Lane B work.

## Current accepted AWQ evidence

The accepted V6 decision is:

`C16_QWEN25_7B_AWQ_FUSED_V6_PASS_WITH_SCOPED_EVIDENCE`

Formal ACKed portfolio:

1. `PREFILL_AWQ_DEQUANT`
   - 11 direct GLOBAL static shards
   - 11 executed / 0 zero-proven
   - no LDGSTS or other detected address-bearing special path

2. `DECODE_FUSED_GEMM`
   - 43 direct GLOBAL static shards
   - 27 executed / 16 `ZERO_EXECUTION_PROVEN`
   - no LDGSTS or other detected address-bearing special path

Both are qualified only as:

`ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL`

The earlier phase-mislabeled prefill GEMM bundle is explicitly excluded from all coverage/scientific conclusions. Its raw data remains immutable.

## Scientific purpose of Lane A V7

Independently consume the accepted AWQ bundles and build the AWQ side of the future controlled:

`Qwen2.5-7B raw vs Qwen2.5-7B AWQ`

comparison.

Do not claim a quantization causal result yet because the raw7B exact runtime/replay side is not qualified.

Qwen0.5 evidence may be used only for clearly labelled cross-deployment descriptive context; Qwen0.5 vs Qwen7-AWQ confounds scale and quantization.

## Important input-hash audit

The prior asset index and the V6 runtime use multiple hash semantics for the AWQ S2 frozen input.

V6 runtime records:

- token file SHA256
- canonical token-sequence SHA256

The earlier authority index records its own `token_payload_sha256` from the historical receipt.

Lane A must determine exactly what byte/object each hash covers and prove that the executed 2048-token sequence is the intended frozen S2_TEXT authority. Different hashes are acceptable only when they are for different canonical objects/serializations and the relationship is explicitly proven.

Do not retokenize.
Do not normalize by guessing.
Fail closed on an actual token-sequence mismatch.

## Claim boundaries

Allowed:

- per-static/per-shard direct GLOBAL event counts;
- same-process address-context attribution;
- per-shard 4K/64K page and 128B line fingerprints;
- WEIGHT / QUANT_METADATA / UNKNOWN_RUNTIME attribution when directly proven;
- object-relative comparison across replays only for independently proven common semantic object identity;
- set-level static coverage inventories;
- descriptive comparison to other deployments with explicit confounders.

Not allowed:

- fabricated cross-shard temporal order;
- cross-replay absolute-VA union;
- whole-kernel physical footprint from replay-sharded traces unless separately justified;
- reuse distance across separately replayed shards;
- raw7B-vs-AWQ quantization causality before raw7B qualification;
- treating the excluded phase-mislabeled bundle as evidence.

## Existing minor issues

Do not open a separate repair round. If shared analysis code is touched for this goal, fold small correctness-preserving fixes into the same commit and rerun the exact RTX3090 Q2 CPU regression where applicable.
