# CODEX 174-new Goal — C16 Asset Readiness + Qwen2.5-7B Raw Layer-Replay Preparation V6

## Goal mode

Fresh branch/worktree on node174-new.

Suggested branch:

`hrl/c16-asset-readiness-174new-v6`

Base from the accepted 174-new state:

`1447bf9bb19bd249c116f53287a1f768170848c7`

Read first:

`docs/vm_tlb/chatgpt_handoff/c16/asset_readiness_v6/CURRENT_SCOPE_AND_GUARDRAILS.md`

This is a CPU-only waiting-time preparation goal. Node109 V5 is the active capture mainline; do not wait for it and do not touch its live producer directories.

## Primary objective

Make future C16 execution faster and safer by closing reusable asset metadata, with Qwen2.5-7B raw exact layer-replay preparation as the highest-value item.

Do not run any model inference. Do not run CUDA. Do not create new scientific conclusions.

---

## P0 — Qwen2.5-7B raw exact layer-replay readiness

Use the canonical model asset under node164. Resolve the exact full revision from the archive receipt/authority; never expand the abbreviated revision from memory.

### P0.1 Checkpoint inventory

Read only lightweight metadata where possible:

- `config.json`
- tokenizer/config metadata
- checkpoint index (`*.safetensors.index.json` when present)
- safetensors headers/index metadata
- archive receipt/manifest

Do not load the full ~15 GB model into RAM merely to inventory it.

Produce a deterministic inventory that maps at least:

- tensor name
- logical role
- decoder layer id when applicable
- source safetensors shard
- dtype
- shape
- exact tensor byte count
- source file identity/SHA from canonical archive receipt

Classify major groups:

- embeddings
- each decoder layer
- final norm
- lm_head/output
- tied/shared storage when proven by model config/metadata
- other tensors

### P0.2 Per-layer residency/readiness report

For every decoder layer, compute from metadata:

- total parameter bytes
- attention bytes
- MLP bytes
- norm/other bytes
- list/count of required source shards

Also report:

- maximum single-layer parameter bytes
- median layer parameter bytes
- embedding bytes
- lm_head/output bytes
- whether embedding/output tying is configured

This is a planning estimate from exact tensor metadata, not a runtime CUDA-memory claim.

### P0.3 Deterministic selective loader

Implement a CPU-side deterministic helper that can resolve the exact tensor set needed for one decoder layer without loading unrelated shards.

Requirements:

- index-driven; no glob-order assumptions;
- fail closed on missing tensor, duplicate tensor, unexpected dtype/shape when checked against config-derived expectations;
- use `safetensors.safe_open`/mmap or equivalent metadata-efficient access;
- do not instantiate the full model;
- provide a dry-run mode that emits the exact files/tensors/bytes that a future layer replay would need;
- no GPU copy in this V6 goal.

The helper should be reusable by a later node109 semantic-layer-streaming implementation.

### P0.4 Bind existing frozen S2 authority

Locate the existing exact Qwen2.5-7B raw `S2_TEXT B1/T2048/D32` historical binding from the 21 hash-closed Qwen bindings.

Create a compact readiness record that binds:

- model id
- exact raw7B revision
- scenario `S2_TEXT`
- exact token binding/payload SHA
- token count
- canonical input path
- model archive receipt SHA
- checkpoint inventory SHA

Do not retokenize and do not copy token payloads unnecessarily.

### P0.5 Future replay contract — metadata only

Write a machine-readable prospective contract for a future `SEMANTICALLY_EXACT_LAYER_REPLAY` qualification stage.

It should require, but not claim yet:

1. exact original raw7B weights/dtype;
2. exact frozen input binding;
3. semantic layer streaming with original runtime semantics;
4. target-layer-state snapshot hash closure;
5. full target-layer replay;
6. output equivalence against the semantic streaming reference;
7. kernel signature equivalence before profiling;
8. direct GLOBAL MREF + qualified special global path capture once node109 V5 is accepted;
9. explicit layer-local claim boundary.

Status in V6 must be `READY_FOR_FUTURE_QUALIFICATION`, not `FORMAL_ACCEPTED`.

---

## P1 — Canonical reusable asset readiness index

Audit the six existing canonical model archives under:

`/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/`

Use existing archive receipts/manifests as primary closure evidence.

Do not bulk rehash every model unless a receipt is absent, malformed, or inconsistent.

Produce `MODEL_ASSET_READINESS.tsv` with at least:

- canonical slug
- model id
- exact revision
- canonical path
- archive receipt path/SHA
- expected model payload size
- config present
- tokenizer authority present
- checkpoint index present/not-applicable
- shard count
- archive closure status
- input authority status
- execution readiness note

Preserve:

- Qwen3-8B: `NO_HISTORICAL_FROZEN_BINDING`
- DeepSeek-V2-Lite: `NO_HISTORICAL_FROZEN_BINDING`

Do not generate new bindings.

### P1.1 Canonical input authority index

Consolidate existing small metadata into `MODEL_INPUT_AUTHORITY_INDEX.tsv`.

Must cover at least:

- 21 exact historical Qwen2.5 bindings
- adopted Llama S0 authority with its correct FUTURE_ONLY semantics
- explicit no-historical-binding rows for Qwen3-8B and DeepSeek-V2-Lite

Recommended columns:

`model_id revision scenario input_class token_count token_payload_sha256 binding_sha256 canonical_or_provenance_path authority_status notes`

This is an index over existing authority, not a rewrite of authority.

---

## P2 — Read-only current-capture path/catalog audit

There is a layout discrepancy worth documenting:

- the long-term taxonomy introduced `captures/raw/`;
- recent formal producer indexes/catalog entries have used `<root>/raw/<RUN_ID>`.

Perform a read-only audit of:

- catalog entry `raw_path` values;
- whether `<root>/raw`, `<root>/captures/raw`, or both exist;
- whether both contain overlapping RUN_IDs;
- whether any redirect/documentation explains the layout;
- which location current accepted catalog entries actually authorize.

Do not move, delete, rename, copy, or symlink formal run directories.
Do not update live catalog paths in this goal.

Output:

`CURRENT_CAPTURE_PATH_AUDIT.tsv`

and a short recommendation classified as one of:

- `NO_ACTION_REQUIRED`
- `DOCUMENTATION_ONLY`
- `POST_V5_MIGRATION_RECOMMENDED`
- `INCONSISTENCY_REQUIRES_REVIEW`

Never perform the migration itself in V6.

---

## P3 — AutoAWQ source offline build readiness

Use the already frozen canonical AutoAWQ kernels source on node164.

Authority:

- canonical source receipt under `assets/sources/autoawq_kernels/`
- reported archive SHA256 `49304506a87ef74c3a3dd07ddc839d796c25432d2cdd721e1b968977fa78f398`

Verify the archive/receipt relationship without fetching a second source tree.

Prepare `AUTOAWQ_KERNELS_BUILD_MANIFEST.json` containing, where available:

- source identity/commit/tag
- source archive SHA
- source receipt SHA
- build system (`setup.py`, `pyproject.toml`, etc.)
- CUDA/C++ extension source files
- package/import name expected by current AutoAWQ (`awq_ext` or exact observed name)
- known build dependencies
- SM89 architecture/build flag required
- expected output wheel/extension artifact naming
- notes about PyTorch/CUDA ABI that node109 must freeze before build

Do not compile CUDA on 174-new.
Do not install into the accepted Qwen0 environment.

---

## Implementation requirements

Prefer reusable scripts under:

`util/vm_tlb/c16/assets/`

or another clearly scoped C16 asset-prep directory.

All outputs must be deterministic and hash-closed.

Large artifacts stay on node164; Git contains only code, compact manifests/indexes/receipts/review evidence.

Do not create duplicate model copies.

If some canonical path differs from the expected taxonomy, discover it from receipts/catalog rather than guessing.

## Tests

CPU-only tests should cover at least:

- checkpoint index exact tensor resolution;
- duplicate/missing tensor fail closed;
- per-layer byte accounting deterministic;
- tied embedding/output metadata handling;
- raw7B S2 binding join exact;
- no retokenization path invoked;
- model readiness index deterministic;
- no-historical-binding preservation;
- capture-path audit is read-only;
- AutoAWQ source receipt SHA mismatch fails closed;
- repeat run produces byte-identical compact indexes/receipts where timestamps are excluded from deterministic content.

Keep RTX3090 Q2 parser regression untouched unless shared code is modified; if shared analysis code is modified, rerun the exact regression.

## Review pack

Create:

`docs/vm_tlb/review_packs/C16_ASSET_READINESS_174NEW_V6/`

Include at least:

- `README.md`
- `FINAL_DECISION.json`
- `MODEL_ASSET_READINESS.tsv`
- `MODEL_INPUT_AUTHORITY_INDEX.tsv`
- `QWEN25_7B_RAW_CHECKPOINT_INVENTORY.tsv`
- `QWEN25_7B_RAW_LAYER_RESIDENCY.tsv`
- `QWEN25_7B_RAW_S2_REPLAY_READINESS.json`
- `QWEN25_7B_RAW_FUTURE_REPLAY_CONTRACT.json`
- `CURRENT_CAPTURE_PATH_AUDIT.tsv`
- `AUTOAWQ_KERNELS_BUILD_MANIFEST.json`
- test results
- `SHA256SUMS`

Any very large tensor inventory can live under node164 derived/provenance with a compact SHA-bound summary in Git, but the expected Qwen7 tensor inventory should normally be small enough for TSV review evidence.

## Final decision

Expected success label:

`C16_ASSET_READINESS_174NEW_V6_PASS`

Possible scoped success:

`C16_ASSET_READINESS_174NEW_V6_PASS_WITH_GAPS`

Use scoped success only if a nonblocking asset lacks metadata that cannot be reconstructed without unsafe mutation/download.

A missing/invalid Qwen2.5-7B raw canonical model receipt or missing exact S2 binding is blocking for the Qwen7 replay-readiness subgoal; fail closed rather than inventing authority.

Commit/push the implementation and review pack, report branch/HEAD/decision, then STOP.
