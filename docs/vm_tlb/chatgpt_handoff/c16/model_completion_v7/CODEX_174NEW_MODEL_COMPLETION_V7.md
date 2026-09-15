# CODEX 174-new Goal — C16 Missing-Model Completion + Prospective Input Readiness V7

## Goal mode

CPU-only parallel preparation on node174-new.

Fetch/pull:

`hrl/c16-model-completion-v7-coordination`

Read first:

`docs/vm_tlb/chatgpt_handoff/c16/model_completion_v7/CURRENT_GAPS_AND_GUARDRAILS.md`

Suggested work branch:

`hrl/c16-model-completion-174new-v7`

Base asset authority:

`1d64cd3b996592916e9e34e15c152cbf5a468fa9`

Accepted LDGSTS result is read-only context only:

`cff4b238c5c98c09b5eda96f3e1df4e1d78b57d3`

Do not touch node109 GPU work. Do not mutate formal raw/catalog data.

---

## Primary objective

Close reusable CPU-side gaps for the model set that is still incomplete, so future GPU time is spent on execution/qualification rather than discovering tokenizer, config, layer, MoE/MLA, or input-authority details.

Priority order:

1. Qwen3-8B
2. DeepSeek-V2-Lite
3. Llama-3.2-1B missing prospective non-S0 scenarios
4. Qwen3-30B-A3B if its local/canonical metadata is already available

Qwen2.5-0.5B / Qwen2.5-7B raw / Qwen2.5-7B AWQ already have seven historical scenario bindings; audit only, do not regenerate them.

---

# P0 — Fold in minor V6-R1 helper fixes

Do this as part of normal implementation; do not create a separate repair decision.

### P0.1 Selective-layer dry-run

Update the reusable layer resolver so dry-run emits, for every selected tensor:

- tensor name
- source shard
- dtype
- shape
- exact tensor bytes

and emits:

- selected tensor count
- source shard list
- total selected parameter bytes

Continue to read only index/header metadata in dry-run.

Where architecture/config-derived expectations are available, validate expected dtype/shape and fail closed on mismatch. Do not silently accept a different tensor layout.

### P0.2 Explicit fail-closed checks

Replace correctness-critical `assert` use in the C16 asset helpers with explicit `InventoryError`/`RuntimeError` or equivalent. Behavior must remain fail closed even under `python -O`.

### P0.3 AutoAWQ source closure hygiene

Without modifying or refetching the canonical source tree:

- recursively include all C++ extension sources as well as CUDA sources;
- ensure nested files such as `awq_ext/exllama/exllama_ext.cpp` and `awq_ext/exllamav2/ext.cpp` are included;
- record exact HEAD;
- record `HEAD^{tree}`;
- require/report clean worktree;
- preserve recorded archive SHA `49304506a87ef74c3a3dd07ddc839d796c25432d2cdd721e1b968977fa78f398` from the receipt;
- explicitly label the archive blob itself `NOT_REHASHED_ARCHIVE_BYTES` if no separate archive file is exposed.

Do not fetch a second source tree just to close this cosmetic gap.

### P0.4 Deterministic capture-path audit generation

Make the generator produce the complete committed read-only audit deterministically, including old/new path existence, overlap status, migration/redirect observation, catalog physical consistency and recommendation.

No path migration in V7.

---

# P1 — Missing-model static architecture inventory

Use only canonical asset receipts/config/checkpoint indexes/safetensors headers. Do not bulk rehash model payloads that are already receipt-closed.

Mandatory models:

- `Qwen/Qwen3-8B`
- `deepseek-ai/DeepSeek-V2-Lite`

Conditional model:

- `Qwen/Qwen3-30B-A3B@ad44e777bcd18fa416d9da3bd8f70d33ebb85d39` only if exact local/canonical authority is discoverable

Produce a machine-readable `MODEL_STATIC_ARCHITECTURE_V7.tsv` plus per-model JSON detail.

At minimum record:

- model id and exact revision
- architecture/model_type
- checkpoint dtype(s)
- number of decoder layers
- hidden size
- attention heads
- KV heads where applicable
- intermediate sizes
- vocabulary size
- max position/context configuration
- RoPE-related config relevant to address/shape behavior
- tie-word-embedding state
- checkpoint shard count
- exact total tensor bytes from metadata

For Qwen3-8B also record exact dense-layer attention/MLP/norm parameter bytes.

For DeepSeek-V2-Lite additionally extract, only when present in archived config:

- dense-vs-MoE layer arrangement
- `n_routed_experts`
- `n_shared_experts`
- experts-per-token/top-k settings
- MoE intermediate size
- router/gate-related configuration
- `q_lora_rank`
- `kv_lora_rank`
- `qk_nope_head_dim`
- `qk_rope_head_dim`
- `v_head_dim`
- any other config field necessary to understand the MLA/KV representation

Do not infer missing fields from general DeepSeek knowledge.

For Qwen3-30B-A3B, if exact asset metadata is available, audit the planning assumptions against actual config and report discrepancies explicitly rather than silently updating the plan.

---

# P2 — Per-layer / expert residency metadata

Using checkpoint index + safetensors headers only, produce deterministic residency summaries.

For each applicable model/layer record:

- layer id
- attention bytes
- dense MLP bytes
- norm/other bytes
- router/gate bytes
- routed-expert bytes
- shared-expert bytes
- total layer parameter bytes
- number/list of source shards

For MoE models also report where metadata permits:

- expert count represented in a layer
- per-expert parameter bytes (min/median/max if nonuniform)
- all-routed-experts bytes per layer
- shared-expert bytes per layer
- router bytes per layer

Produce summaries with min/median/max decoder-layer parameter bytes and exact largest single layer.

This is static parameter-residency evidence only. Do not claim runtime CUDA memory, allocator footprint, or 16 GB fit merely from parameter bytes.

Recommended output:

`MODEL_LAYER_RESIDENCY_V7.tsv`

`MODEL_LAYER_RESIDENCY_SUMMARY_V7.json`

---

# P3 — Static tensor semantic-role inventory

Prepare a reusable tensor-role map for future object attribution and exact layer replay.

Classify only from exact tensor names/config structure, with fail-closed `UNKNOWN_STATIC_ROLE` when uncertain.

Useful classes include:

- EMBEDDING_WEIGHT
- LM_HEAD_WEIGHT
- ATTENTION_WEIGHT
- NORM_WEIGHT
- DENSE_MLP_WEIGHT
- ROUTER_WEIGHT
- MOE_ROUTED_EXPERT_WEIGHT
- MOE_SHARED_EXPERT_WEIGHT
- OTHER_WEIGHT
- UNKNOWN_STATIC_ROLE

For DeepSeek, do not label something as KV cache merely because it contains `kv` in a parameter name. This is a static weight-role inventory, not runtime object attribution.

Output:

`MODEL_STATIC_TENSOR_ROLE_V7.tsv`

---

# P4 — Recover common source-text authority before creating new bindings

Audit existing C16 input/provenance assets for the exact source text used to create the existing TEXT/CODE/STRUCTURED scenario family.

Required distinction:

- source text authority
- tokenizer-specific token payload authority

Do not use token decoding as a substitute for missing source text.

Produce:

`C16_SOURCE_TEXT_AUTHORITY_AUDIT_V7.tsv`

For every relevant source/scenario report:

- source class
- source path
- source SHA256
- generation/truncation policy identity if recorded
- whether it is safe for prospective cross-model retokenization

If exact source-text authority or the deterministic token-length policy is missing, mark that scenario `SOURCE_AUTHORITY_GAP` and do not invent a replacement in V7.

---

# P5 — Prospective missing-model input bindings

Only execute P5 for scenarios whose source authority is closed in P4.

Target missing deployments:

### Llama-3.2-1B

Preserve the existing adopted S0 authority exactly.
Create only missing prospective scenarios when the common source authority closes them.

### Qwen3-8B

Create prospective bindings from the exact archived Qwen3 tokenizer.
Historical status must remain `NO_HISTORICAL_FROZEN_BINDING`.

### DeepSeek-V2-Lite

Create prospective bindings from the exact archived tokenizer.
Historical status must remain `NO_HISTORICAL_FROZEN_BINDING`.

### Qwen3-30B-A3B

Create prospective bindings only if exact tokenizer/model revision authority is available locally. If the tokenizer is byte-identical to the canonical Qwen3-8B tokenizer, prove that by relevant tokenizer/config file hashes before reusing a token payload; otherwise tokenize independently.

Preferred scenario coverage, when source authority permits, is the same seven-scenario family already used by the Qwen2.5 variants:

- S0_TEXT B1/T128/D4
- S1_CODE B1/T256/D16
- S2_CODE B1/T2048/D32
- S2_STRUCTURED B1/T2048/D32
- S2_TEXT B1/T2048/D32
- S3_TEXT B1/T8192/D16
- S4_STRUCTURED B4/T2048/D16

For each new binding freeze:

- model id/revision
- tokenizer identity
- relevant tokenizer file hashes
- source text SHA
- exact token IDs or compact hash-closed payload
- actual token count
- scenario/batch/context/decode definition
- binding SHA
- explicit prospective status

Use local assets only. `local_files_only=True` or equivalent is required.

If tokenizer execution requires archived custom code/`trust_remote_code`, do not fetch network code. Either:

1. execute only the hash-closed archived code in an isolated CPU environment and bind its file hashes; or
2. mark `TOKENIZER_RUNTIME_BLOCKED` if that cannot be done safely/reproducibly.

Never rewrite the existing 21 Qwen2.5 historical bindings.

Create a two-axis authority index so that, for Qwen3/DeepSeek, both can simultaneously be true:

- historical status = `NO_HISTORICAL_FROZEN_BINDING`
- prospective status = `PROSPECTIVE_FROZEN_INPUT_AUTHORITY_V1`

Recommended output:

`MODEL_INPUT_AUTHORITY_V7.tsv`

---

# P6 — Future exact-layer-replay readiness contracts

Prepare metadata-only prospective contracts; no GPU execution.

### Qwen3-8B

Record what a future exact dense-layer replay must bind:

- exact layer weights
- exact incoming hidden state
- position/attention state
- layer-local KV state
- runtime deployment identity
- output equivalence
- kernel signature equivalence
- full-function global-address-path audit before formal capture

### DeepSeek-V2-Lite

In addition to the above, require exact MLA/MoE state appropriate to the archived config, including exact router/expert decisions where present. Do not simplify MLA to ordinary K/V or MoE to a dense FFN.

### Qwen3-30B-A3B

If exact config is available, audit the existing planning document against actual config and emit a compact plan-assumption audit. Do not execute Mode A/Mode B in this goal.

Recommended outputs:

- `QWEN3_8B_FUTURE_REPLAY_CONTRACT_V1.json`
- `DEEPSEEK_V2_LITE_FUTURE_REPLAY_CONTRACT_V1.json`
- `QWEN3_30B_PLAN_ASSUMPTION_AUDIT_V1.tsv` when applicable

Status must remain planning/readiness only, never `FORMAL_ACCEPTED`.

---

# P7 — Qwen3-30B asset-state audit only

Discover, without network fetch or bulk migration:

- whether a complete source payload currently exists;
- whether a canonical node164 archive exists;
- whether archive/source receipts exist;
- exact revision actually present;
- shard count and receipt closure;
- tokenizer/config availability.

Classify one of:

- `CANONICAL_ASSET_CLOSED`
- `SOURCE_COMPLETE_READY_FOR_ARCHIVAL`
- `SOURCE_PARTIAL`
- `ASSET_NOT_FOUND`
- `AUTHORITY_INCONSISTENT`

Do not perform the ~61 GB archival copy in V7.

Output:

`QWEN3_30B_ASSET_STATE_V7.json`

---

# Tests

CPU-only tests must cover at least:

- selected-layer dry-run exact byte accounting;
- explicit fail-close under missing/duplicate tensor and shape/dtype mismatch;
- no correctness-critical `assert` dependence;
- deterministic per-layer and expert byte accounting;
- Qwen3/DeepSeek historical-status preservation;
- no rewriting of the 21 accepted Qwen2.5 bindings;
- no mutation of Llama adopted S0 authority;
- source-text gap fails closed instead of reverse-decoding tokens;
- prospective binding generation deterministic when source authority exists;
- no network tokenizer/model access;
- AutoAWQ nested C++ inventory present;
- AutoAWQ HEAD/tree/worktree-clean evidence;
- repeated compact outputs byte-identical when timestamps are excluded.

If shared RTX3090 Q2 parser code is not touched, do not rerun unrelated GPU/parser regressions merely for ceremony.

---

# Review pack

Create:

`docs/vm_tlb/review_packs/C16_MODEL_COMPLETION_174NEW_V7/`

Include at least:

- `README.md`
- `FINAL_DECISION.json`
- `MODEL_STATIC_ARCHITECTURE_V7.tsv`
- `MODEL_LAYER_RESIDENCY_V7.tsv`
- `MODEL_LAYER_RESIDENCY_SUMMARY_V7.json`
- `MODEL_STATIC_TENSOR_ROLE_V7.tsv`
- `C16_SOURCE_TEXT_AUTHORITY_AUDIT_V7.tsv`
- `MODEL_INPUT_AUTHORITY_V7.tsv`
- future replay contracts generated by P6
- `QWEN3_30B_ASSET_STATE_V7.json`
- updated compact AutoAWQ source-closure evidence
- test results
- `SHA256SUMS`

If some prospective inputs cannot be created because source-text authority is genuinely missing, preserve the gap explicitly; do not downgrade otherwise valid static model-readiness work.

Expected success labels:

`C16_MODEL_COMPLETION_174NEW_V7_PASS`

or, if nonblocking source/asset gaps remain:

`C16_MODEL_COMPLETION_174NEW_V7_PASS_WITH_GAPS`

Blocking only for claims actually made. Missing Qwen3-30B payload is not blocking for Qwen3-8B/DeepSeek/Llama completion.

Commit/push the implementation and review pack, report branch/HEAD/decision, then STOP.
