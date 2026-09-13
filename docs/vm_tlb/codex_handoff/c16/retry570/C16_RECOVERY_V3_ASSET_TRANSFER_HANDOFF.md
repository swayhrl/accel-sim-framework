# C16 Recovery V3 — Asset Recovery and Transfer Handoff

## Purpose

Complete exact model/input/package preparation without treating GPU-host network failure as a final blocker.

## Host roles

- **Local/control host**: preferred place for metadata search, upstream fetch, package construction, hashing, and final raw-artifact retention.
- **GPU host**: execution/capture only; it may have no outbound internet.

Reuse the existing working two-host copyback/SSH machinery already proven by Llama. Do not invent a new transfer path if the existing one works.

## Local/control-host bulk-storage contract

The local root filesystem has only about 65 GiB free, while `/root/share` has about 494 GiB free at authorization time. Large campaign data must use `/root/share`.

Read and obey:

```text
docs/vm_tlb/codex_handoff/c16/retry570/C16_RECOVERY_V3_LOCAL_STORAGE_LAYOUT.md
```

Required local roots:

```text
LOCAL_BULK_ROOT=/root/share/c16_recovery_v3
LOCAL_MODEL_ROOT=/root/share/c16_recovery_v3/models
LOCAL_HF_CACHE_ROOT=/root/share/c16_recovery_v3/hf-cache
LOCAL_TRANSFER_STAGING=/root/share/c16_recovery_v3/staging
```

The Git worktree may remain under `/workspace`, but model weights, large archives, model download caches and transfer staging payloads must not be placed there.

Before the first upstream fetch, verify `/root/share` filesystem identity/free bytes/writability and create the required directory tree. Never silently fall back to the constrained root filesystem.

For local/control-host Hugging Face/model fetches, set process-local cache variables under `/root/share/c16_recovery_v3/hf-cache`, e.g. `HF_HOME`, `HUGGINGFACE_HUB_CACHE`, and `TRANSFORMERS_CACHE`.

## Asset workflow per model

1. Resolve exact identity/revision from current repo/history/retained manifests.
2. Search existing local/control-host caches and package roots.
3. Search bounded GPU-host caches/roots.
4. If absent and identity is exact, fetch immutable revision on local/control host into `/root/share/c16_recovery_v3`.
5. Build package manifest:
   - source/provider;
   - exact model ID;
   - immutable revision/content identifier;
   - file list;
   - per-file bytes;
   - per-file SHA256 where practical/required;
   - total bytes;
   - config/tokenizer/index hashes;
   - quantization/weight format.
6. Transfer to an isolated GPU-host destination.
7. Rehash and compare.
8. Register the GPU-host asset root only after all required hashes/identity checks pass.

## Search roots

Use bounded metadata scans under existing roots when present, including:

```text
/root/share/c16_recovery_v3
local/control host project asset roots
local HF/model caches
/root/autodl-tmp
/root/autodl-fs
/root/.cache/huggingface
/workspace
/data
```

Honor `$HF_HOME`, `$TRANSFORMERS_CACHE`, `$HUGGINGFACE_HUB_CACHE` when defined.

Never scan shell history, tokens, SSH keys, browser credential stores, or unrelated user secrets.

## Network recovery

If the GPU host reports `NETWORK_UNREACHABLE`, do not stop.

Try in order:

1. local/control-host authoritative upstream fetch into `/root/share/c16_recovery_v3`;
2. already cached exact revision;
3. exact package from retained previous campaign assets;
4. alternate official distribution only when content identity/equivalence can be proven.

Then transfer to GPU host.

A final network blocker is valid only when no authorized host/path can obtain the exact asset.

## Large-model storage discipline

Before fetch/transfer:

- record free bytes for `/`, `/workspace`, and `/root/share` on the local/control host;
- record free remote bytes;
- estimate complete package bytes + temporary transfer overhead;
- require the local large-file destination to be under `/root/share/c16_recovery_v3`;
- avoid duplicate caches where a single immutable package can be referenced;
- never delete a validated source package until destination hashes pass.

Recommended local guards are defined in `C16_RECOVERY_V3_LOCAL_STORAGE_LAYOUT.md`. If `/root/share` becomes tight, clean duplicate/staging/cache copies that already have final hash-closed counterparts; never redirect a large package to `/workspace` as a workaround.

## Input/token contracts

For TEXT/CODE/STRUCTURED scenarios:

- preserve frozen raw input hash;
- tokenize with the exact deployment tokenizer;
- record actual token IDs/length/hash;
- do not assume the same text gives the same token count across models.

If an authoritative existing token receipt exists, reuse it after hash validation.

## Acceptance

Asset preparation is complete only when the R1/R2 gates in `C16_FULL_AUTHORITY_RECOVERY_V3_STAGE_ACCEPTANCE.md` pass, including the local bulk-storage placement checks.
