# CODEX 174-new Asset/Readiness V6-r1 — Canonical Assets + Qwen2.5-7B Raw Exact Layer-Replay Preparation

## 0. Execution mode and isolation

This is a **fresh-window, fresh-worktree, CPU-only preparation Goal** on node174-new.

It is deliberately separate from the LDGSTS scientific-analysis window. Do not share implementation branches or worktrees.

Do not resume the previous asset-readiness Codex window. Do not reuse a dirty worktree.

Accepted 174-new base:

`1447bf9bb19bd249c116f53287a1f768170848c7`

Suggested implementation branch:

`hrl/c16-asset-readiness-174new-v6-r1`

Suggested worktree:

`/root/workspace/accel-sim-framework-c16-asset-readiness-174new-v6-r1`

Recommended bootstrap:

```bash
cd /root/workspace/accel-sim-framework
git fetch origin --prune

git worktree add \
  /root/workspace/accel-sim-framework-c16-asset-readiness-174new-v6-r1 \
  -b hrl/c16-asset-readiness-174new-v6-r1 \
  1447bf9bb19bd249c116f53287a1f768170848c7
```

If the name already exists from a failed attempt, create an `-r2` branch/worktree from the same accepted base rather than continuing unknown local state.

No CUDA. No model inference. No NVBit/NCU/NSYS. No new scientific performance claims.

---

# 1. Goal and boundary

Use the idle CPU/IO capacity on 174-new to prepare reusable C16 assets so the next producer stages do not spend GPU time on bookkeeping.

Priority order:

1. Qwen2.5-7B raw exact layer-replay readiness metadata and CPU-side selective-loader tooling.
2. Canonical model/input authority indexes.
3. Read-only audit of current node164 capture/catalog path layout.
4. AutoAWQ kernels source/build-readiness manifest for future node109 isolated build.

This Goal does **not** authorize:

- Qwen7 semantic streaming execution;
- Qwen7 target layer replay;
- AWQ CUDA compilation;
- Qwen3/DeepSeek new input bindings;
- simulator/TLB/Cache inheritance;
- any model retokenization;
- any formal raw mutation or node164 migration.

---

# 2. Node164 authority root and asset rules

Long-term C16 root:

`/root/share/mnt164/huangrulin/c16_ai_workload/`

Current long-term taxonomy includes:

```text
assets/models/
assets/sources/
provenance/historical_snapshots/
captures/
derived/
catalog/
```

However, already-admitted Pipeline runs may still be cataloged under the older:

`<root>/raw/<RUN_ID>`

layout. Existing run catalog/manifest paths are authoritative. Do not silently relocate or reinterpret them.

### Canonical reusable model assets expected

Audit the six existing canonical model families, discovering exact revisions from receipts rather than memory:

- Llama-3.2-1B
- Qwen2.5-0.5B-Instruct
- Qwen2.5-7B-Instruct raw
- Qwen2.5-7B-Instruct AWQ
- Qwen3-8B
- DeepSeek-V2-Lite

Do not include Qwen3-30B-A3B in this six-model readiness closure unless a separately complete canonical archive/receipt is already present and can be listed as `OUT_OF_SCOPE_OBSERVED`. Do not start its archival workflow here.

### Rehash policy

Existing archive receipt/manifest is primary authority.

Do not reread/rehash tens of GB by default.

Full payload rehash is justified only when:

- receipt missing;
- receipt malformed;
- receipt points to absent payload;
- size/inventory mismatch;
- explicit corruption suspicion.

Otherwise validate lightweight receipt structure, file presence, metadata and sampled/reference hashes as already defined by the archive scheme.

---

# 3. P0 — Qwen2.5-7B raw checkpoint inventory

This is the highest-value subgoal.

Resolve exact model identity/revision from canonical receipt. Never reconstruct an abbreviated revision from memory.

Read only metadata-efficient sources where possible:

- `config.json`;
- generation config if relevant;
- tokenizer/config metadata;
- `model.safetensors.index.json` or equivalent checkpoint index;
- safetensors headers;
- archive receipt/manifest.

Do not instantiate the full Transformers model.
Do not load the entire checkpoint into RAM.
Do not deserialize unrelated shards simply to discover tensor names.

## 3.1 Tensor inventory

Produce deterministic rows containing at least:

```text
tensor_name
logical_group
decoder_layer_id
submodule_role
source_shard
source_shard_sha256_or_receipt_identity
dtype
shape
numel
exact_tensor_bytes
```

Logical groups should include:

- embeddings;
- decoder layer N attention;
- decoder layer N MLP;
- decoder layer N norms/other;
- final norm;
- lm_head/output;
- other;
- tied/shared relationship only if proven.

Use config/index/header evidence. Do not infer tensor tying merely because dimensions match.

Expected output:

`QWEN25_7B_RAW_CHECKPOINT_INVENTORY.tsv`

If tensor-level rows are unexpectedly huge, store the full deterministic inventory under node164 `derived/asset_readiness/...` and put a compact SHA-bound summary in Git. Prefer Git TSV if reasonably small.

---

# 4. P0 — per-layer residency planning metadata

For every decoder layer compute exact parameter bytes from the tensor inventory:

- attention bytes;
- MLP bytes;
- norm/other bytes;
- total decoder-layer bytes;
- number/list of source shards touched.

Also report model-level groups:

- embedding parameter bytes;
- final norm bytes;
- lm_head/output bytes;
- tied embedding/output configured? yes/no/proven-unresolved;
- maximum decoder-layer parameter bytes;
- minimum/median/maximum layer parameter bytes;
- number of decoder layers.

These are **parameter-residency planning numbers only**. They are not CUDA peak-memory predictions because activations, KV, workspace, allocator fragmentation and kernels are not included.

Expected output:

`QWEN25_7B_RAW_LAYER_RESIDENCY.tsv`

and a machine-readable summary:

`QWEN25_7B_RAW_LAYER_RESIDENCY_SUMMARY.json`

---

# 5. P0 — deterministic selective layer loader helper

Implement a reusable CPU-side helper under a clearly scoped location, recommended:

`util/vm_tlb/c16/assets/qwen7_layer_inventory.py`

or equivalent.

The helper is preparation for a future node109 `SEMANTICALLY_EXACT_LAYER_REPLAY` implementation.

## Requirements

It must:

1. load the exact checkpoint index;
2. resolve all tensors belonging to one requested decoder layer;
3. resolve the exact safetensors shard(s) needed;
4. use deterministic tensor ordering;
5. expose `--dry-run` that performs no tensor payload load unless explicitly requested;
6. optionally validate safetensors header dtype/shape;
7. fail closed on missing/duplicate/unexpected tensor mapping;
8. avoid reading unrelated checkpoint shards;
9. never instantiate the full model;
10. emit deterministic JSON/TSV describing selected tensors/files/bytes.

A CPU-only bounded functional test may open one representative layer's tensors via `safetensors.safe_open`/mmap to prove selective access works. Do not materialize all layers simultaneously.

If a single layer spans multiple files, that is valid; record it exactly.

## Suggested validation layers

Select at least:

- first decoder layer;
- middle decoder layer;
- last decoder layer.

Only validate checkpoint resolution/bytes; do not execute layer math.

Expected test artifact:

`QWEN25_7B_RAW_SELECTIVE_LOADER_TEST.tsv`

---

# 6. P0 — join exact historical S2_TEXT authority

Find the exact historical binding for **Qwen2.5-7B raw**:

`S2_TEXT B1/T2048/D32`

from the existing 21 hash-closed Qwen2.5 bindings.

Authority may reside under current provenance/catalog metadata and historical snapshot payload paths. Follow the already accepted authority seed/index rather than guessing a path.

Do not retokenize.
Do not generate replacement token IDs.
Do not reuse Qwen0 token payload unless the historical binding itself proves that payload identity.

Create:

`QWEN25_7B_RAW_S2_REPLAY_READINESS.json`

with at least:

```text
status
model_id
exact_model_revision
canonical_model_path
model_archive_receipt_path
model_archive_receipt_sha256
checkpoint_index_path
checkpoint_inventory_sha256
scenario = S2_TEXT
batch = 1
context_tokens = 2048
decode_steps = 32
input_authority_status
input_binding_path
input_binding_sha256
token_payload_path
token_payload_sha256
token_count
tokenizer_identity_if_recorded
```

Expected status after successful metadata closure:

`READY_FOR_FUTURE_QUALIFICATION`

Not `FORMAL_ACCEPTED`.

Missing raw7B exact model receipt or missing S2 binding is blocking for this subgoal. Do not substitute another model variant.

---

# 7. P0 — future semantically exact layer-replay contract

Create a machine-readable future contract:

`QWEN25_7B_RAW_FUTURE_REPLAY_CONTRACT.json`

It must state that later GPU qualification requires all of:

1. exact canonical raw7B revision;
2. exact original dtype/runtime semantics;
3. exact frozen S2 input authority;
4. semantic layer streaming that reconstructs original hidden states/KV;
5. hash-closed target-layer-state snapshots;
6. exact target layer weights loaded from canonical checkpoint;
7. full-layer replay, not synthetic standalone GEMM;
8. output equivalence against the semantic-streaming reference;
9. kernel-signature equivalence;
10. formal capture of direct GLOBAL MREF plus the now-qualified LDGSTS GLOBAL SOURCE path as required by exact SASS;
11. same-process ADDRESS_CONTEXT for every replay;
12. explicit layer-local claim boundary.

It must also explicitly forbid treating layer replay as evidence for:

- full-model RTX4080 throughput;
- full-model global cache/TLB history;
- cross-layer physical reuse distance;
- full-resident absolute VA placement.

Do not implement Mode A/Mode B execution in this CPU-only Goal.

---

# 8. P1 — canonical model asset readiness index

Produce:

`MODEL_ASSET_READINESS.tsv`

One row per canonical model variant with at least:

```text
canonical_slug
model_id
exact_revision
canonical_path
archive_receipt_path
archive_receipt_sha256
payload_bytes
config_present
tokenizer_files_present
checkpoint_index_status
weight_shard_count
archive_closure_status
input_authority_status
execution_readiness_note
```

For Qwen3-8B and DeepSeek-V2-Lite preserve exactly:

`NO_HISTORICAL_FROZEN_BINDING`

Do not create a prospective binding in this Goal.

For Llama adopted S0 input, preserve its accepted semantics as FUTURE/adopted authority and do not mislabel it as recovered historical R5 input.

For Qwen2.5 variants, record that the 21 historical bindings are existing authority, not newly created inputs.

---

# 9. P1 — canonical input authority index

Consolidate small existing authority metadata into:

`MODEL_INPUT_AUTHORITY_INDEX.tsv`

Must cover:

- all 21 historical Qwen2.5 exact bindings;
- Llama adopted S0 authority with correct status;
- explicit Qwen3-8B no-historical-binding status;
- explicit DeepSeek-V2-Lite no-historical-binding status.

Recommended columns:

```text
model_variant
model_id
model_revision
scenario
input_class
batch
context_tokens
decode_steps
token_count
token_payload_sha256
binding_sha256
authority_path
authority_status
notes
```

This is a derived index over existing authority. Do not rewrite original authority files.

Validate deterministic ordering.

---

# 10. P2 — current capture/catalog path audit, strictly read-only

There is a known taxonomy mismatch:

- intended newer taxonomy includes `<root>/captures/raw/`;
- accepted Pipeline V1 runs currently appear in catalog/review evidence under `<root>/raw/<RUN_ID>`.

Audit the current reality without changing it.

Inspect:

1. catalog entry raw paths for accepted C16 runs;
2. existence/status of `<root>/raw`;
3. existence/status of `<root>/captures/raw`;
4. overlapping RUN_ID names between the two if both exist;
5. whether any redirect or migration receipt exists;
6. whether current receiver scripts still write/admit to the old path;
7. whether catalog is internally consistent with the physical admitted runs.

Do not:

- move;
- copy;
- delete;
- rename;
- symlink;
- rewrite catalog entries;
- change receiver configuration.

Output:

`CURRENT_CAPTURE_PATH_AUDIT.tsv`

and choose exactly one recommendation:

- `NO_ACTION_REQUIRED`
- `DOCUMENTATION_ONLY`
- `POST_CAMPAIGN_MIGRATION_RECOMMENDED`
- `INCONSISTENCY_REQUIRES_REVIEW`

If existing catalog paths are internally consistent, current operation remains authoritative even if taxonomy naming is older.

---

# 11. P3 — AutoAWQ kernels source/build readiness

Use the source already frozen under node164:

`/root/share/mnt164/huangrulin/c16_ai_workload/assets/sources/autoawq_kernels/`

Reported source archive SHA256:

`49304506a87ef74c3a3dd07ddc839d796c25432d2cdd721e1b968977fa78f398`

Verify the canonical acquisition receipt and archive relationship. Do not fetch another source tree from the network.

Produce:

`AUTOAWQ_KERNELS_BUILD_MANIFEST.json`

Include, when evidence is available:

```text
source_identity
source_commit_or_tag
archive_path
archive_sha256
source_receipt_path
source_receipt_sha256
build_system_files
extension_source_files
expected_python_import_name
known_compile_dependencies
SM89_arch_flag_or_expected_arch_configuration
expected_wheel_or_so_outputs
pytorch_cuda_abi_inputs_that_node109_must_freeze
notes_on_isolated_environment
```

Do not compile CUDA on 174-new.
Do not install into any accepted Qwen0/Llama runtime.

If source metadata does not expose a git commit/tag, record `UNKNOWN_FROM_ARCHIVE_METADATA` rather than inventing one.

---

# 12. Implementation location and deterministic outputs

Recommended reusable code location:

`util/vm_tlb/c16/assets/`

Do not put large weight payloads or copied model shards in Git.

Derived compact metadata can be stored in Git review pack. Larger deterministic inventories may live on node164 under a clearly namespaced `derived/asset_readiness/...` directory with a compact SHA-bound Git summary.

All generated TSV/JSON should have deterministic row/key ordering where practical.

Do not let timestamps alter the deterministic content SHA of core indexes. Put timestamps in a separate receipt field/file if needed.

---

# 13. Tests

CPU tests must cover at least:

1. checkpoint index exact tensor resolution;
2. first/middle/last layer selective resolution;
3. duplicate tensor mapping fails closed;
4. missing tensor mapping fails closed;
5. safetensors dtype/shape metadata extraction deterministic;
6. per-layer byte accounting deterministic;
7. embedding/lm_head tying only marked when proven;
8. raw7B S2 authority join exact;
9. no code path invokes tokenizer/retokenization;
10. Qwen3-8B/DeepSeek no-historical-binding statuses preserved;
11. model/input index row order deterministic;
12. capture-path audit performs no mutation;
13. AutoAWQ receipt/archive SHA mismatch fails closed;
14. repeated run produces byte-identical core TSV/JSON outputs.

If shared C16 analysis parser code is modified, rerun exact RTX3090 Q2 regression. Prefer not to modify shared parser code for this asset-prep goal.

---

# 14. Review pack

Create:

`docs/vm_tlb/review_packs/C16_ASSET_READINESS_174NEW_V6_R1/`

Include at least:

- `README.md`
- `FINAL_DECISION.json`
- `MODEL_ASSET_READINESS.tsv`
- `MODEL_INPUT_AUTHORITY_INDEX.tsv`
- `QWEN25_7B_RAW_CHECKPOINT_INVENTORY.tsv` or compact bound summary
- `QWEN25_7B_RAW_LAYER_RESIDENCY.tsv`
- `QWEN25_7B_RAW_LAYER_RESIDENCY_SUMMARY.json`
- `QWEN25_7B_RAW_SELECTIVE_LOADER_TEST.tsv`
- `QWEN25_7B_RAW_S2_REPLAY_READINESS.json`
- `QWEN25_7B_RAW_FUTURE_REPLAY_CONTRACT.json`
- `CURRENT_CAPTURE_PATH_AUDIT.tsv`
- `AUTOAWQ_KERNELS_BUILD_MANIFEST.json`
- `TEST_RESULTS.tsv`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Expected success:

`C16_ASSET_READINESS_174NEW_V6_R1_PASS`

Allowed scoped success:

`C16_ASSET_READINESS_174NEW_V6_R1_PASS_WITH_GAPS`

Scoped gaps are acceptable only for nonblocking metadata (for example missing source git tag when archive hash is valid). Missing raw7B model authority, checkpoint inventory authority, or exact S2 binding is blocking for the Qwen7 replay-readiness subgoal.

Commit/push the implementation branch, report branch + HEAD + decision + major readiness findings, then STOP.
