# C16 Recovery V3 — Prelaunch Asset Consolidation Delta

This delta supersedes v8 where it conflicts.

## User-authorized scope change

For this Recovery V3 task, **do not execute Qwen3-30B-A3B**. The model is being downloaded separately under `/root/share/huangrulin`; do not wait for it, move it, validate it, profile it, trace it, or include it in completion denominators for this task.

Mark its current-campaign status:

```text
EXCLUDED_BY_USER_CURRENT_CAMPAIGN
```

This is not `BLOCKED`, `SKIPPED_RESOURCE`, or a failed scientific row. Preserve its authority in project metadata for a future campaign.

All other planned models remain in scope:

- Llama-3.2-1B
- Qwen2.5-0.5B-Instruct
- Qwen2.5-7B-Instruct raw
- Qwen2.5-7B-Instruct-AWQ
- Qwen3-8B
- DeepSeek-V2-Lite
- GLM historical project extension after exact identity recovery

## Immediate first action: consolidate existing assets onto /root/share

Before continuing network downloads for any model other than the already-running Qwen0.5 exact fetch, perform one bounded inventory/consolidation pass for all in-scope models.

Search only authorized known roots and retained packages/caches. For each exact model/revision asset already present outside `/root/share/c16_recovery_v3`, migrate it into the v3 bulk layout rather than redownloading it.

Preferred destination:

```text
/root/share/c16_recovery_v3/models/<deployment>/<revision>/
```

For Hugging Face cache assets, either copy the complete relevant repo cache (`blobs/`, `snapshots/`, `refs/`) or materialize a self-contained model directory. Never copy only a snapshot with broken relative blob links.

## Migration protocol

Do not destructively `mv` the only copy first. Use:

```text
source inventory
 -> exact identity/revision verification
 -> rsync/cp/reflink to /root/share staging/final destination
 -> source file count/bytes/hash manifest
 -> destination file count/bytes/hash manifest
 -> equality PASS
 -> register /root/share asset
 -> only then delete old duplicate if safe and useful
```

If source and destination are on the same filesystem and an atomic rename is proven safe, rename is allowed only after confirming no active process/cache contract depends on the old path. Otherwise use copy/rsync then remove the redundant source after closure.

Do not interrupt the currently-running Qwen0.5 download that is already correctly writing to `/root/share`; let it continue. For every other in-scope model, prefer recovered existing assets over new downloads.

## Required consolidation receipt

Publish a compact receipt with one row per in-scope deployment:

```text
model_key
exact_identity/revision
source_path(s)
destination_path
migration_method
source_bytes
destination_bytes
hash_closure
old_duplicate_removed?
status
```

Allowed statuses:

```text
EXISTING_ASSET_CONSOLIDATED
ALREADY_UNDER_BULK_ROOT
EXACT_FETCH_IN_PROGRESS
EXACT_ASSET_NOT_FOUND_CONTINUE_RECOVERY
IDENTITY_NOT_YET_RESOLVED
```

Qwen3-30B-A3B must be listed separately as `EXCLUDED_BY_USER_CURRENT_CAMPAIGN` and otherwise untouched.

## Acceptance before normal R0-R9 continues

- `/root/share/c16_recovery_v3` remains the primary bulk root.
- No in-scope exact asset is needlessly redownloaded if a complete local copy already exists.
- Any removed old copy has a hash-closed replacement under `/root/share`.
- Qwen3-30B-A3B work is absent from this campaign.
- Then continue normal Recovery V3 R0-R9 for all remaining in-scope rows without asking for approval.
