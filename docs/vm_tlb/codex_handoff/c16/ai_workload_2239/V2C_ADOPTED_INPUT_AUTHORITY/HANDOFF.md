# C16 AI Workload V2C — Adopted Input Authority

## Purpose

V2A correctly concluded `HISTORICAL_FROZEN_INPUT_NOT_RECOVERED`: the exact historical five-file bundle and its historical binding receipts were not recovered. That conclusion remains immutable.

However, V2A did recover three byte-exact historical payloads whose hashes close the full content-level input contract:

- raw text SHA256: `bae0b908106146659663fa04f44bc03ec0da18cadb08c9ec357c140afc4d8208`
- token receipt payload SHA256: `0b5a86fdee44452e74e5d80e8043ebd97054fbbe29a6232a4f5cf5d06568c7dd`
- canonical 128 token IDs SHA256: `f9cf1ea6dca7956c740b3aa0af59acadd17be014df2aaffb75d240383502e3a7`
- derived token-ID payload SHA256: `fc712eb0a158f0fe62231f7826feec3eaabfea51906ca6b1588a55ee81ae3624`

V2C authorizes creation of a **new future-use adopted input authority** from those exact bytes. It does not recreate, rename, or claim recovery of any missing historical receipt.

## Authority boundary

Historical statement remains:

`HISTORICAL_FROZEN_INPUT_NOT_RECOVERED`

New future-use statement may become:

`ADOPTED_INPUT_AUTHORITY_V1_PASS`

only if the three recovered payloads are copied byte-for-byte into Git, all expected hashes are revalidated, semantic identity is explicitly bound, and a new adoption receipt is created with a current provenance statement.

The adoption receipt must state that it is newly authored after V2A and is **not** the missing historical `LLAMA_S0_TEXT_BINDING_RECEIPT.json` or `C16_FIND_AND_TRANSFER_LLAMA_S5_FROZEN_INPUT_BINDING_RECEIPT.json`.

## Required identity

```text
scenario_id: S0
batch_size: 1
prefill_tokens: 128
decode_tokens: 4
input_class: TEXT
model_id: meta-llama/Llama-3.2-1B
model_revision: 4e20de362430cd3b72f300e6b0f18e50e7166e08
```

## Historical source payloads

```text
TEXT.txt
/workspace/c16_exchange/autodl_wave1/P0_20260912T2225/a_assets/inputs/TEXT.txt

TEXT_T128.json
/workspace/c16_exchange/autodl_wave1/P0_20260912T2225/a_assets/TOKEN_RECEIPTS/c16_llama32_1b_frozen_compatible/TEXT_T128.json

frozen_token_ids.json
/workspace/c16_exchange/autodl_wave1/returned/llama_s0_g1_formal_5bfbe62b-6140-4f94-8a91-2e433000572c/frozen_token_ids.json
```

Use only these V2A-selected payloads unless a byte-identical alternative is needed because the listed source path is unavailable. Any alternative must match the exact same SHA256 and must be recorded.

## Git publication layout

Publish only after all checks pass:

```text
docs/vm_tlb/assets/c16/ai_workload_inputs/ADOPTED_LLAMA_S0_T128_V1/
├── TEXT.txt
├── TEXT_T128.json
├── frozen_token_ids.json
├── ADOPTED_INPUT_RECEIPT.json
├── SHA256SUMS
└── PROVENANCE.md
```

Do **not** rename `frozen_token_ids.json` to the missing historical `LLAMA_S0_TEXT_TOKEN_IDS.json`.

## Required validation

1. Recompute SHA256 for all three payloads.
2. Parse `TEXT_T128.json` and require exactly 128 target token IDs.
3. Compute compact JSON SHA256 of those 128 IDs and require `f9cf...e3a7`.
4. Parse `frozen_token_ids.json`; require exact list equality with `TEXT_T128.json` target IDs.
5. Require `frozen_token_ids.json` SHA256 `fc712...3624`.
6. Create a new validator for the adopted bundle. Do not weaken or modify the historical `c16_frozen_input_admission.py` fail-closed behavior.
7. Run the new validator only on the newly published adopted bundle.

## Adoption receipt

`ADOPTED_INPUT_RECEIPT.json` must include:

- schema version and creation UTC
- `authority_type = FUTURE_USE_ADOPTED_INPUT_NOT_HISTORICAL_RECOVERY`
- the semantic identity tuple above
- source V2A commit `4b5c2bb79b9e2e79bed8bef10365bf34be6f6cdd`
- original source paths for each payload
- copied Git path for each payload
- source SHA256 and Git-copy SHA256 equality
- all four expected contract hashes
- statement that tokenizer was not invoked
- statement that no historical receipt was recreated or renamed
- statement that this authority is for future 109/2239 work only and does not retroactively alter RTX3090 or RTX4080 R5 evidence

## Optional locator follow-up

No further historical receipt hunting is required in V2C. Do not spend time searching again for the missing historical two receipts.

R5/N1/U8 raw provenance is out of scope for V2C and will be handled on node 109, where `/data/c16` may be visible.

## Hard prohibitions

- NO tokenizer invocation.
- NO regeneration of token IDs.
- NO synthetic recreation of missing historical receipts.
- NO renaming a nearby receipt to a historical missing filename.
- NO editing the three recovered payload bytes.
- NO GPU/CUDA/Llama/NVBit/NCU execution.
- NO RTX3090/RTX4080 authority reinterpretation.
- NO large raw/model/profiler files in Git.

## Required result

Create:

```text
docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V2C_ADOPTED_INPUT_AUTHORITY/RESULTS/
```

with at least:

- `V2C_DECISION.json`
- `ADOPTED_INPUT_VALIDATION.json`
- `OPEN_ISSUES.md`

Decision must be one of:

- `ADOPTED_INPUT_AUTHORITY_V1_PASS`
- `ADOPTED_INPUT_AUTHORITY_V1_BLOCKED_SOURCE_PAYLOAD_MISSING`
- `ADOPTED_INPUT_AUTHORITY_V1_BLOCKED_HASH_MISMATCH`
- `ADOPTED_INPUT_AUTHORITY_V1_BLOCKED_SEMANTIC_MISMATCH`
- `ADOPTED_INPUT_AUTHORITY_V1_BLOCKED_OTHER`

After commit and push, stop. Do not begin node-109 execution or 164 storage import in this branch.
