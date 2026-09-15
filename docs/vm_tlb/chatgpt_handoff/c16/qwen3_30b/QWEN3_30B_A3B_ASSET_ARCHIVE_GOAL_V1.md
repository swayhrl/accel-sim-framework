# Qwen3-30B-A3B Asset Archive Goal V1

## Status

Execution-ready asset task. This stage only closes and archives the completed Qwen3-30B-A3B download. It does **not** run the model, tokenize new inputs, profile kernels, or start layer streaming.

## Objective

Turn the completed download rooted at:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/
```

into a hash-closed canonical C16 model asset on node164, while preserving all download receipts/state/metadata as provenance.

The exact model identity is:

```text
Qwen/Qwen3-30B-A3B
revision: ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

The known model-specific source subtree is currently expected at:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/metadata/
Qwen__Qwen3-30B-A3B__ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

However, **the whole root** `/root/share/huangrulin/c16_qwen3_30b_a3b/` is the source scope for inventory. Do not assume that every authoritative payload/receipt lives under the `metadata/...` subtree.

## Destination

Canonical reusable model asset:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Historical download/provenance snapshot:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/historical_snapshots/
qwen3_30b_a3b_download_v1/
```

The canonical asset and provenance snapshot must remain separate from current Pipeline V1 `captures/raw` and catalog namespaces.

---

# A. Source discovery and closure

Before copying anything, recursively inventory:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/
```

Produce a deterministic source inventory containing at least:

```text
relative_path
file_type
size
sha256
classification
```

Classify each regular file into one of:

```text
MODEL_PAYLOAD
MODEL_CONFIG_TOKENIZER
DOWNLOAD_RECEIPT
DOWNLOAD_STATE
DOWNLOAD_LOG
AUXILIARY_METADATA
UNKNOWN_REVIEW_REQUIRED
```

Do not follow symlinks outside the source root.

## Required model payload checks

Identify the exact Hugging Face payload required to reconstruct the revision locally, including as applicable:

- all model weight shards;
- `model.safetensors.index.json` or equivalent weight index;
- `config.json`;
- generation config;
- tokenizer files;
- special-token/tokenizer configs;
- custom config/modeling files if the exact revision requires them.

The historical download plan expected 16 weight shards. Verify this from the actual completed directory and receipts; do not infer completion solely from file names.

The previously tracked total for the 16 weight-shard payload was approximately:

```text
61,066,575,648 bytes
```

Treat this only as a reconciliation anchor. The actual source inventory and receipts are authoritative. Any difference must be explained rather than silently accepted.

For every weight shard require:

```text
regular file
non-zero size
whole-file SHA256
no .partial suffix
no active download lock/state indicating incomplete content
```

If existing per-shard receipts contain expected SHA256 values, independently recompute each whole-file SHA and compare.

## Completion decision

The source may be promoted to canonical asset only if the exact revision is reconstructible and all required payload/config/tokenizer files are closed.

Allowed source decisions:

```text
QWEN3_30B_SOURCE_COMPLETE
QWEN3_30B_SOURCE_INCOMPLETE
QWEN3_30B_SOURCE_AMBIGUOUS
```

Only `QWEN3_30B_SOURCE_COMPLETE` permits canonical archive promotion.

---

# B. Canonical model archive on node164

Construct through:

```text
.../qwen3-30b-a3b/ad44e777...partial/
```

Never write directly into the final canonical directory.

Copy only the files required for an exact local reconstruction of the model revision into the canonical model directory. Preserve logical Hugging Face-relative names; do not invent new shard names.

After copy, independently rebuild the destination inventory and require exact equality for every canonical payload file:

```text
relative path
size
SHA256
```

Also require exact equality of:

```text
canonical file count
canonical total bytes
canonical inventory digest
```

Only after PASS may the `.partial` directory be promoted to:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Generate inside the canonical directory:

```text
SOURCE_INVENTORY.tsv
DESTINATION_INVENTORY.tsv
MODEL_ARCHIVE_RECEIPT.json
```

`MODEL_ARCHIVE_RECEIPT.json` must bind at least:

```text
model_id
revision
source_root
source_payload_root
canonical_path
file_count
total_bytes
inventory_sha256
model_weight_shard_count
model_weight_total_bytes
config_sha256
weight_index_sha256 (if present)
created_at_utc
verification = EXACT_FILE_SET_SIZE_SHA256_PASS
```

---

# C. Preserve the complete download provenance

The whole download root may contain receipts/state/logs that should not be mixed into the canonical model payload.

Copy every non-canonical regular file from:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/
```

into:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/historical_snapshots/
qwen3_30b_a3b_download_v1/
```

Preserve relative paths.

Do not duplicate the ~61 GB canonical model payload inside the provenance snapshot. Instead write:

```text
CANONICAL_MODEL_REDIRECT.tsv
```

mapping source payload paths/subtrees to the canonical model archive and its receipt SHA.

Generate:

```text
DOWNLOAD_SOURCE_MANIFEST.tsv
DOWNLOAD_SNAPSHOT_SUMMARY.json
CANONICAL_MODEL_REDIRECT.tsv
```

Classify this namespace:

```text
HISTORICAL_DOWNLOAD_PROVENANCE_ONLY
```

It must not become a current scientific run or a Pipeline catalog entry.

---

# D. Do not delete the source in this stage

This Goal is copy + verification only.

Do not delete, move, truncate, or rewrite anything under:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/
```

The final report may mark source objects as:

```text
SAFE_TO_DELETE_AFTER_SEPARATE_CLEANUP
RETAIN_SOURCE
UNKNOWN_DO_NOT_DELETE
```

but no deletion is authorized here.

---

# E. Node109 working-copy planning

Do not bulk-copy the 61 GB model to node109 during this archive Goal if node109 is actively running another formal capture campaign.

Instead report whether node109 currently has sufficient free local storage and propose the future working-copy destination:

```text
/data/c16/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

The later Qwen3-30B execution stage should use a local node109 working copy, not repeatedly load 61 GB of weights over SSHFS from node164.

If node109 is demonstrably idle and the user explicitly authorizes provisioning in the same run, copy may be performed through `.partial` + independent SHA closure. Otherwise leave it as a later provisioning action.

---

# F. Explicitly out of scope

Do not in this stage:

- run Qwen3-30B on GPU;
- create/freeze prospective token inputs;
- change precision or quantize the model;
- use CPU/GPU offload to test inference;
- start semantic layer streaming;
- start exact target-layer replay;
- run NSYS/NCU/NVBit;
- register model files as Pipeline V1 capture data;
- delete the completed source download.

Those begin only after asset closure is accepted.

---

# G. Acceptance criteria

PASS requires all of the following:

1. Whole download root is deterministically inventoried.
2. Exact model revision `ad44e777...` is independently proven complete.
3. All required model payload/config/tokenizer files are identified.
4. Every canonical destination regular file independently matches source path/size/SHA256.
5. The expected 16 weight shards are reconciled against actual files and receipts.
6. No `.partial` or incompletely downloaded weight shard is admitted.
7. Canonical model archive is promoted only after full verification.
8. Non-model receipts/state/logs are preserved as a separate historical provenance snapshot.
9. Model payload is not duplicated inside the provenance snapshot; redirect metadata is explicit and hash-bound.
10. No source file is deleted or modified.
11. Current Pipeline V1 namespaces remain untouched.
12. Review pack SHA256SUMS passes and Git worktree is clean.

Final accepted state:

```text
QWEN3_30B_A3B_CANONICAL_ARCHIVE_PASS
```

---

# H. Required review pack

Create:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_A3B_ASSET_ARCHIVE_V1/
```

Include at least:

```text
README.md
SOURCE_ROOT_INVENTORY.tsv
MODEL_PAYLOAD_CLASSIFICATION.tsv
WEIGHT_SHARD_STATUS.tsv
MODEL_ARCHIVE_STATUS.tsv
MODEL_ARCHIVE_RECEIPT.json
DOWNLOAD_SOURCE_MANIFEST.tsv
DOWNLOAD_SNAPSHOT_SUMMARY.json
CANONICAL_MODEL_REDIRECT.tsv
NODE109_PROVISIONING_STATUS.tsv
CLEANUP_READINESS.tsv
FINAL_DECISION.json
SHA256SUMS
```

The report must explicitly state:

- actual source root and actual payload root;
- actual number and total bytes of weight shards;
- exact revision;
- canonical node164 destination;
- whether all existing download receipts agree with independent hashes;
- whether any unknown/unclassified files remain;
- whether source is safe for a later separately authorized cleanup;
- whether node109 working-copy provisioning is ready.

Commit/push and STOP after archive verification.
