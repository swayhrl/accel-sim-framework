# Qwen3-30B-A3B exact-revision authority recovery and archive completion V1

## Status

Recovery stage following the blocked asset-archive execution at:

```text
branch: hrl/c16-qwen3-30b-asset-archive-exec-v2
commit: 6c98e6f70c7eb6240c90e49cf84875e56b9aaa9f
```

The previous execution correctly failed closed because the local source root contained the 16 verified weight shards and download receipts, but did not contain enough exact-revision repository metadata to reconstruct the Hugging Face model locally.

This recovery stage is authorized to retrieve only the missing **non-weight authority files** from the official Hugging Face repository at the already-frozen exact revision. It must not redownload, replace, modify, or silently substitute the 16 existing weight shards.

## Frozen model identity

```text
repo_id: Qwen/Qwen3-30B-A3B
revision: ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Never use `main`, `latest`, another tag, or a different commit as a substitute.

## Existing weight authority

The blocked review pack already proves all 16 local weight shards have:

- whole-file SHA256 matching their existing receipts;
- readable safetensors headers;
- non-zero sizes;
- no incomplete `.partial` admission;
- deterministic local tensor-key enumeration from each safetensors header.

Treat those 16 local weight files as frozen source evidence. Do not rewrite them.

Primary source root:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/
```

Known weight/receipt subtree:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/metadata/
Qwen__Qwen3-30B-A3B__ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

## Objective

Recover the missing exact-revision repository authority files from the official `Qwen/Qwen3-30B-A3B` Hugging Face revision, independently hash-close them, then resume the canonical node164 archive until the existing V2 archive acceptance criteria can reach:

```text
QWEN3_30B_A3B_CANONICAL_ARCHIVE_PASS
```

This remains an asset-only stage. Do not run the model or create new inputs.

---

# A. Retrieve exact-revision non-weight repository files

Preferred recovery root:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/
metadata_recovery/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Keep recovered files separate from the original 37-file download tree so provenance remains explicit.

Use an exact-revision Hugging Face operation, for example `huggingface_hub.snapshot_download`, with:

```text
repo_id = Qwen/Qwen3-30B-A3B
revision = ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

and exclude the large weight shards:

```text
model-*.safetensors
```

The goal is to retrieve the complete set of non-weight repository files at the exact revision, not just three hand-picked files. This prevents another incomplete reconstruction later.

At minimum the recovered exact-revision authority is expected to contain, if present in that revision:

```text
model.safetensors.index.json
config.json
generation_config.json
tokenizer.json
tokenizer_config.json
vocab.json
merges.txt
```

Also preserve other small exact-revision repository files such as README/LICENSE or repository metadata if returned by the pinned snapshot operation. They are provenance, not model-weight substitutes.

Do not infer missing file contents from another Qwen model. Do not reconstruct official config/tokenizer files manually.

## Retrieval receipt

Create a deterministic receipt for every recovered file with at least:

```text
repo_id
revision
relative_path
size
sha256
retrieval_method
retrieved_at_utc
```

Record the exact command/library version used for the retrieval.

If the local machine cannot reach Hugging Face:

1. diagnose network/proxy/authentication;
2. retry boundedly;
3. if necessary, retrieve the same pinned non-weight files on another already-authorized node and copy them with source/destination SHA closure;
4. never fall back to a different revision.

A network problem is operationally recoverable and should not by itself redefine the model authority.

---

# B. Exact revision and repository-structure checks

After retrieval, require:

1. `config.json` parses successfully.
2. The model identity is consistent with Qwen3 MoE / Qwen3-30B-A3B.
3. `model.safetensors.index.json` parses successfully.
4. Every filename referenced by the weight index exists among the 16 frozen local weight shards.
5. No unexpected seventeenth weight shard or alternative filename is referenced.
6. Every tensor key in the index maps to exactly one existing weight shard.
7. Every indexed tensor key exists in the corresponding safetensors header.
8. Every non-metadata tensor key observed in the frozen safetensors headers is reconciled against the official index; unexplained mismatches fail closed.
9. Tokenizer authority is locally reconstructible from the recovered exact-revision files.
10. No exact-revision file was sourced from `main` or from a different commit.

Produce explicit counts:

```text
index tensor-key count
safetensors-header tensor-key count
matched count
missing-from-header count
unindexed-header-key count
referenced shard count
```

The index/header closure must be deterministic and reviewable.

---

# C. Reconcile the 16 existing local shards against recovered authority

Do not redownload the 16 weight shards.

Re-use the previously verified local shard SHA evidence from:

```text
docs/vm_tlb/review_packs/C16_QWEN3_30B_A3B_ASSET_ARCHIVE_V2/
WEIGHT_SHARD_STATUS.tsv
```

Recompute any shard hash only if needed to close the final canonical archive or if prior evidence is ambiguous. The final review pack must reference the exact prior evidence commit and show that the same local files are being admitted.

The known aggregate shard-byte figure is approximately 61.07 GB; use the actual per-file inventories as authority rather than a rounded total.

---

# D. Complete the canonical node164 archive

Canonical destination remains:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

The canonical directory must contain the exact locally reconstructible revision:

- the 16 frozen verified weight shards;
- official exact-revision weight index;
- config;
- tokenizer authority files;
- generation config and any other small runtime files needed by the exact revision.

Construct/update only through an unambiguous `.partial` workflow. Never overwrite an existing final canonical directory in place.

If a `.partial` tree exists from the blocked V2 attempt:

- inventory it first;
- prove its provenance;
- resume only if unambiguous;
- otherwise quarantine or create a fresh unique partial tree.

After copying, independently rebuild destination inventories and require exact source/destination equality for every admitted canonical file by:

```text
relative path
size
SHA256
```

Then rerun the official-index-to-shard/header closure against the destination copy, not only the source copy.

Only after all checks pass may the canonical directory be promoted.

---

# E. Historical provenance snapshot

The provenance snapshot must preserve:

1. original download receipts/state/logs;
2. the blocked V2 archive evidence;
3. the exact-revision metadata-recovery receipts;
4. canonical redirects for weight payloads / authority files as appropriate.

Destination namespace:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/historical_snapshots/
qwen3_30b_a3b_download_v1/
```

Do not duplicate the ~61 GB weight payload inside the historical snapshot when a canonical redirect is sufficient and hash-bound.

Keep classifications explicit:

```text
ORIGINAL_DOWNLOAD_EVIDENCE
EXACT_REVISION_METADATA_RECOVERY
CANONICAL_ASSET_REDIRECT
```

Do not register this historical snapshot as Pipeline V1 scientific raw data.

---

# F. Source cleanup remains out of scope

Do not delete or move:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/
```

in this recovery stage.

The final report may classify source files as safe for later cleanup, but deletion requires a separate explicit cleanup Goal after the canonical archive is accepted.

---

# G. Node109 remains out of scope

Do not provision the 61 GB working copy to node109 yet.

Do not run GPU work.

Do not create token bindings.

Do not start Semantic Layer Streaming, NSYS, NCU, or NVBit.

Node109 provisioning begins only after ChatGPT accepts the canonical archive.

---

# H. Recovery behavior and STOP policy

Recoverable issues are not immediate STOP conditions:

- transient Hugging Face/network failure;
- proxy configuration;
- interrupted small-file retrieval;
- resumable `.partial` copy;
- transient SSHFS I/O failure.

Diagnose and retry boundedly while preserving evidence.

Fail closed and STOP only if the exact revision cannot be established, for example:

- the pinned revision is unavailable;
- official index references a missing or differently named weight shard;
- index tensor map disagrees materially with the frozen safetensors headers;
- config/tokenizer authority cannot be obtained from the exact revision;
- recovered files are demonstrably from a different revision;
- destination independent SHA closure fails persistently.

Do not lower the revision or identity standard to obtain PASS.

---

# I. Required review pack

Create/update a new pack:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_A3B_AUTHORITY_RECOVERY_V1/
```

Include at least:

```text
README.md
BLOCKED_V2_AUTHORITY_REFERENCE.md
RECOVERED_EXACT_REVISION_FILES.tsv
RETRIEVAL_RECEIPT.json
WEIGHT_SHARD_REUSE_STATUS.tsv
HF_INDEX_CLOSURE.tsv
TENSOR_KEY_CLOSURE.tsv
TOKENIZER_AUTHORITY.tsv
CANONICAL_SOURCE_INVENTORY.tsv
CANONICAL_DESTINATION_INVENTORY.tsv
MODEL_ARCHIVE_RECEIPT.json
DOWNLOAD_PROVENANCE_STATUS.tsv
CLEANUP_READINESS.tsv
FINAL_DECISION.json
SHA256SUMS
```

`FINAL_DECISION.json` must explicitly state:

```text
exact repo_id
exact revision
16-shard status
weight total bytes
recovered non-weight file count
config SHA
weight-index SHA
tokenizer authority SHA set
index/header closure counts
canonical node164 path
source deletion status = NOT_DELETED
```

Successful final status:

```text
QWEN3_30B_A3B_CANONICAL_ARCHIVE_PASS
```

Commit, push, and STOP after canonical archive verification. Do not proceed to model execution in the same Goal.
