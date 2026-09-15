# Qwen3-30B-A3B Asset Archive Goal V2

## Status

Execution-ready **asset closure / archive** stage for a fresh Codex window.

This stage closes the completed Qwen3-30B-A3B download and archives it as a canonical C16 model asset on node164. It does not run or profile the model.

Read first:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/CURRENT_STATE_BEFORE_Q30_ARCHIVE.md
```

Previous V1 spec remains useful background, but this V2 document is the authoritative execution contract for this round.

---

# 1. Goal

Starting from the completed download root:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/
```

produce:

1. a deterministic, independently hash-closed canonical model archive for exactly
   `Qwen/Qwen3-30B-A3B@ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`;
2. a complete historical snapshot of non-model download receipts/state/logs/metadata;
3. explicit evidence that the model revision is reconstructible from the canonical archive;
4. a cleanup-readiness recommendation for the source, but **no deletion**;
5. a future node109 provisioning plan only, with no mutation of node109 in this round.

Final success state:

```text
QWEN3_30B_A3B_CANONICAL_ARCHIVE_PASS
```

---

# 2. Source scope and exact identity

Inventory the entire root recursively:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/
```

Known model-specific subtree:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/metadata/
Qwen__Qwen3-30B-A3B__ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Exact identity:

```text
model_id = Qwen/Qwen3-30B-A3B
revision = ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Do not silently substitute:

- another Qwen3-30B-A3B revision;
- a quantized checkpoint;
- a merged/repacked checkpoint;
- a tokenizer/config from another revision.

No network re-download is allowed unless the user separately authorizes it. This task must first determine whether the completed local source is sufficient.

---

# 3. Fresh-window preflight

Before copying any payload:

## 3.1 Repository/worktree isolation

Create a fresh execution branch/worktree. Do not modify any active experiment worktree.

Suggested execution branch:

```text
hrl/c16-qwen3-30b-asset-archive-exec-v2
```

Record:

```text
framework git SHA
git status
hostname
source filesystem path
destination filesystem path
UTC start timestamp
```

## 3.2 Filesystem preflight

Confirm:

- source root exists and is readable;
- node164 C16 root is mounted and writable;
- destination parent exists or can be created;
- sufficient free space exists with a conservative margin;
- no unexpected existing final canonical directory is present;
- no unexpected stale `.partial` destination exists.

If a final canonical destination already exists:

1. do not overwrite it;
2. independently inventory/hash it;
3. compare against source;
4. if byte-identical, report `ALREADY_PRESENT_EXACT_MATCH` and continue closure without recopying;
5. if any difference exists, fail closed and preserve both states for review.

If a stale `.partial` exists, do not delete blindly. Inspect whether it belongs to this exact task/revision. Resume only if its provenance is unambiguous; otherwise quarantine/rename it outside the final namespace and document the action.

## 3.3 Source immutability check

Before the expensive copy starts, verify there is no active downloader process or lock/state indicating that the model payload is still changing.

Perform at least two lightweight source observations separated by a short interval for payload file size/mtime stability, in addition to later whole-file hashing.

Do not assume "download command exited" equals scientific closure.

---

# 4. Deterministic source inventory and classification

Build a deterministic recursive inventory of all regular files under the whole source root.

Required fields:

```text
relative_path
file_type
size
sha256
classification
source_role
```

Classify every regular file into one of:

```text
MODEL_WEIGHT_SHARD
MODEL_WEIGHT_INDEX
MODEL_CONFIG
MODEL_TOKENIZER
MODEL_GENERATION_CONFIG
MODEL_CODE_OR_AUX_REQUIRED
DOWNLOAD_RECEIPT
DOWNLOAD_STATE
DOWNLOAD_LOG
AUXILIARY_METADATA
UNKNOWN_PRESERVE_FOR_REVIEW
```

Symlink rules:

- do not follow symlinks outside the source root;
- record symlinks separately;
- canonical model payload should consist of regular files unless an exact-revision local reconstruction demonstrably requires a symlink, in which case document and preserve its target semantics explicitly.

Unknown non-model files do not automatically block canonical model closure if they are preserved in historical provenance and cannot affect exact model reconstruction. Unknown files that may be required model payload/config **do block** until resolved.

---

# 5. Weight-shard closure

Historical download tracking expected 16 weight shards and approximately:

```text
61,066,575,648 bytes
```

of weight-shard payload.

This is a reconciliation anchor only.

Derive the authoritative shard set from the actual completed checkpoint and its weight index/receipts.

For every expected shard require:

```text
regular file
non-zero size
stable size
no .partial/incomplete naming
whole-file SHA256 recomputed independently
receipt agreement when receipt exists
readable safetensors header
```

Generate:

```text
WEIGHT_SHARD_STATUS.tsv
```

with at least:

```text
shard_name
size
sha256
receipt_expected_sha256
receipt_match
safetensors_header_readable
index_referenced
status
```

All expected model shards must reach `PASS` for canonical archive promotion.

---

# 6. Hugging Face index / tensor-map closure

Do more than "16 files exist".

If `model.safetensors.index.json` is present, parse it and prove:

1. every `weight_map` referenced shard exists;
2. every referenced shard is in the canonical payload set;
3. every referenced tensor key can be found in the referenced safetensors shard header;
4. no tensor is mapped to a missing shard;
5. no duplicate tensor-key ownership exists across shards where it should be unique;
6. all weight shards expected by the index are accounted for;
7. any extra `.safetensors` file not referenced by the index is explicitly explained;
8. `metadata.total_size`, if present, is recorded and reconciled against the tensor metadata / checkpoint structure rather than confused with on-disk file bytes.

This is a metadata/header validation only; do not load the full model tensors into RAM/GPU.

Generate:

```text
HF_INDEX_CLOSURE.tsv
TENSOR_MAP_CLOSURE.json
```

A malformed or internally inconsistent index is a blocking asset failure.

---

# 7. Config/tokenizer/revision closure

Identify all files needed for a local offline reconstruction of the exact revision, including as present:

```text
config.json
generation_config.json
tokenizer.json
tokenizer_config.json
special_tokens_map.json
merges/vocab files if applicable
added token files
remote-code/config/modeling files if actually required by this revision
model.safetensors.index.json
```

Do not import config/tokenizer files from another cached revision merely to make the set look complete.

Parse `config.json` and record a derived structural summary for later Qwen3-30B execution planning, without running the model.

Generate:

```text
MODEL_STRUCTURE_SUMMARY.json
```

Record actual config-derived values where present, for example:

```text
architectures
model_type
hidden_size
num_hidden_layers
num_attention_heads
num_key_value_heads
num_experts
num_experts_per_tok
moe_intermediate_size / equivalent
vocab_size
torch_dtype
transformers_version
```

Do not hard-code expected architecture values if the config says otherwise. The source config is authoritative.

Optionally instantiate only lightweight config/tokenizer objects offline to prove parseability, but do not instantiate/load model weights and do not run inference.

---

# 8. Canonical payload definition

Define one exact canonical payload set sufficient to reconstruct the model revision offline.

The canonical archive must preserve the original logical filenames and relative layout required by Hugging Face loading. Do not rename shards.

Canonical destination:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Build through:

```text
.../ad44e777bcd18fa416d9da3bd8f70d33ebb85d39.partial/
```

Use content-oriented copy semantics suitable for the accepted SSHFS-backed data root:

- recursive regular-file copy;
- resumable/partial transfer where useful;
- no source deletion;
- do not rely on UID/GID/mode preservation as scientific identity;
- never overwrite an existing final canonical directory.

For a large transfer, avoid a fragile single monolithic command if per-file/shard progress with restartability is safer.

---

# 9. Independent destination verification

After copy, independently rebuild the canonical destination payload inventory.

Require exact source/destination equality for every source-derived canonical file:

```text
relative_path
size
SHA256
```

Also require equality of:

```text
payload file count
payload total bytes
canonical inventory digest
weight shard count
weight shard total bytes
```

Important: generated closure files such as receipts/manifests must **not** be included in the source-derived payload equality comparison, otherwise the inventory becomes self-referential.

Generate inside the final canonical archive (or an adjacent provenance metadata directory if cleaner):

```text
SOURCE_PAYLOAD_INVENTORY.tsv
DESTINATION_PAYLOAD_INVENTORY.tsv
MODEL_ARCHIVE_RECEIPT.json
MODEL_STRUCTURE_SUMMARY.json
```

`MODEL_ARCHIVE_RECEIPT.json` must bind at least:

```text
schema_version
model_id
revision
source_root
resolved_source_payload_root
canonical_path
payload_file_count
payload_total_bytes
payload_inventory_sha256
weight_shard_count
weight_shard_total_bytes
weight_index_sha256
config_sha256
tokenizer_authority_files and SHA256 values
hf_index_closure_status
created_at_utc
verification = EXACT_FILE_SET_SIZE_SHA256_PASS
```

Promote `.partial` only after all canonical payload checks pass.

Use a checked single-writer promotion. If atomic no-replace is unsupported by the backing filesystem, use the already accepted checked-rename fallback and document that filesystem limitation; do not overwrite a final path.

---

# 10. Complete download provenance snapshot

Preserve every non-canonical regular file from the source root under:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/historical_snapshots/
qwen3_30b_a3b_download_v1/
```

Use a `.partial` construction path and independently hash-close the copied provenance files.

Preserve relative paths.

Do not duplicate the ~61GB canonical model payload in the historical snapshot.

Instead generate:

```text
CANONICAL_MODEL_REDIRECT.tsv
```

mapping each excluded canonical payload file/subtree from the historical source to:

```text
canonical path
canonical archive receipt SHA256
source relative path
payload SHA256
```

Generate:

```text
DOWNLOAD_SOURCE_MANIFEST.tsv
DOWNLOAD_SNAPSHOT_MANIFEST.tsv
DOWNLOAD_SNAPSHOT_SUMMARY.json
CANONICAL_MODEL_REDIRECT.tsv
```

Classification:

```text
HISTORICAL_DOWNLOAD_PROVENANCE_ONLY
```

This namespace must never be registered as a Pipeline scientific run.

---

# 11. Source/canonical reconciliation and duplicate handling

Before final PASS, prove that every regular file under the whole source root is represented by exactly one of:

```text
A. canonical model payload on node164;
B. copied historical provenance file on node164;
C. explicit documented redirect to A;
```

No regular file may silently disappear from the archive accounting.

If a source file is byte-identical to some already-existing node164 object outside this new archive, record the overlap but do not mutate the existing object. Prefer explicit provenance over deduplicating by ad-hoc deletion during this task.

---

# 12. Node109 planning only

Do not copy the model to node109 in this asset Goal.

Do not interfere with ongoing node109 capture work.

Report only:

```text
proposed future node109 path:
/data/c16/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

and, if obtainable read-only without disturbing work:

```text
free space
existing partial/copy status
recommended provisioning method
```

Recommended future provisioning must use node164 canonical archive as source authority, copied locally to node109 through `.partial` + independent hash closure before layer-streaming/replay work.

---

# 13. No input binding in this round

Qwen3-30B-A3B has no accepted historical frozen input binding in the current C16 authority.

Do not create one here.

After canonical asset closure is accepted, a separate stage will create a prospective, explicit Qwen3-30B input binding for the later layer-streaming / exact-layer-replay campaign.

Do not retokenize or borrow Qwen2.5 token IDs in this asset stage.

---

# 14. Failure handling

This is an asset-closure Goal, so fail closed on model identity/payload corruption, but do not stop for trivial operational issues without attempting repair.

Recoverable examples:

```text
copy interrupted
→ resume same .partial transfer

SSHFS transient I/O/transport issue
→ retry transfer/readback; do not re-download model

stale unambiguous .partial from this exact task
→ verify and resume

non-model unknown file
→ preserve in provenance + classify UNKNOWN_PRESERVE_FOR_REVIEW
```

Blocking examples:

```text
required shard missing
required shard hash disagrees with trustworthy receipt
weight index references missing/inconsistent tensor/shard
exact revision cannot be reconstructed
source continues changing during closure
canonical destination differs from source after retry
ambiguous existing final canonical directory with mismatched bytes
```

A blocking model-identity/payload issue yields a final non-PASS decision with complete evidence. Do not "repair" corrupted model data by fetching another revision or modifying weights.

---

# 15. Explicitly forbidden actions

Do not:

- delete/move/truncate any source file;
- run Qwen3-30B inference;
- load the whole model into RAM/GPU just to test it;
- create prospective token bindings;
- start semantic layer streaming;
- start exact target-layer replay;
- run NSYS/NCU/NVBit;
- quantize/repack/merge weights;
- CPU/GPU offload the model for testing;
- write model payload into `captures/raw` or catalog it as a scientific run;
- mutate existing node164 canonical models/captures;
- mutate node109 model/capture state;
- silently ignore unknown required files or index inconsistencies.

---

# 16. Acceptance criteria

PASS requires all of the following:

1. Entire source root deterministically inventoried.
2. Exact intended model ID/revision bound.
3. Source shown stable/not actively downloading.
4. Actual weight-shard set reconciled; expected 16-shard history either confirmed or explicitly corrected from source/index evidence.
5. All required weight shards independently whole-file SHA256 closed.
6. Existing trustworthy shard receipts reconciled against independent hashes.
7. Safetensors headers readable for every admitted shard.
8. Weight-index → shard → tensor-key closure passes.
9. Required config/tokenizer/index files identified and hash-bound.
10. Actual architecture summary derived from source config.
11. Canonical payload copied through `.partial` or proven already byte-identical.
12. Destination source-derived payload file set/size/SHA exactly equals source canonical payload set.
13. Canonical archive receipt generated and hash-bound.
14. All non-canonical regular files preserved in historical provenance or explicitly redirected.
15. Model payload is not duplicated in the historical snapshot.
16. No source file modified/deleted.
17. No Pipeline V1 capture/catalog namespace pollution.
18. No node109 mutation.
19. Review pack `SHA256SUMS` passes.
20. Git worktree clean and execution branch pushed.

Final PASS status:

```text
QWEN3_30B_A3B_CANONICAL_ARCHIVE_PASS
```

---

# 17. Required review pack

Create:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_A3B_ASSET_ARCHIVE_V2/
```

Required files:

```text
README.md
SOURCE_ROOT_INVENTORY.tsv
SOURCE_CLASSIFICATION.tsv
SOURCE_STABILITY_CHECK.tsv
MODEL_PAYLOAD_CLASSIFICATION.tsv
WEIGHT_SHARD_STATUS.tsv
HF_INDEX_CLOSURE.tsv
TENSOR_MAP_CLOSURE.json
MODEL_STRUCTURE_SUMMARY.json
SOURCE_PAYLOAD_INVENTORY.tsv
DESTINATION_PAYLOAD_INVENTORY.tsv
MODEL_ARCHIVE_RECEIPT.json
DOWNLOAD_SOURCE_MANIFEST.tsv
DOWNLOAD_SNAPSHOT_MANIFEST.tsv
DOWNLOAD_SNAPSHOT_SUMMARY.json
CANONICAL_MODEL_REDIRECT.tsv
NODE109_PROVISIONING_PLAN.tsv
CLEANUP_READINESS.tsv
OPEN_ISSUES.md
FINAL_DECISION.json
SHA256SUMS
```

`README.md` must state succinctly:

- actual discovered source layout;
- actual resolved model payload root;
- exact model ID/revision;
- actual weight-shard count and total bytes;
- whether historical `61,066,575,648`-byte shard anchor matched;
- whether all download receipts agreed with independent hashes;
- HF index/tensor-map closure result;
- canonical node164 path;
- historical provenance path;
- canonical payload bytes/file count;
- provenance snapshot bytes/file count;
- any unknown files and why they do/do not affect reconstruction;
- source cleanup readiness recommendation;
- node109 future provisioning recommendation;
- final decision.

---

# 18. STOP boundary

Commit and push the execution branch/review pack, then STOP.

Do not continue into:

```text
prospective input binding
node109 61GB provisioning
semantic layer streaming
exact-layer replay
NSYS / NCU / NVBit
```

Those are the next separately reviewed stages after canonical archive acceptance.
