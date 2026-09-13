# C16 Recovery V3 — Asset Recovery and Transfer Handoff

## Purpose

Complete exact model/input/package preparation without treating GPU-host network failure as a final blocker.

## Host roles

- **Local/control host**: preferred place for metadata search, upstream fetch, package construction, hashing, and final raw-artifact retention.
- **GPU host**: execution/capture only; it may have no outbound internet.

Reuse the existing working two-host copyback/SSH machinery already proven by Llama. Do not invent a new transfer path if the existing one works.

## Asset workflow per model

1. Resolve exact identity/revision from current repo/history/retained manifests.
2. Search existing local/control-host caches and package roots.
3. Search bounded GPU-host caches/roots.
4. If absent and identity is exact, fetch immutable revision on local/control host.
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

1. local/control-host authoritative upstream fetch;
2. already cached exact revision;
3. exact package from retained previous campaign assets;
4. alternate official distribution only when content identity/equivalence can be proven.

Then transfer to GPU host.

A final network blocker is valid only when no authorized host/path can obtain the exact asset.

## Large-model storage discipline

Before fetch/transfer:

- record free local and remote bytes;
- estimate complete package bytes + temporary transfer overhead;
- avoid duplicate caches where a single immutable package can be referenced;
- never delete a validated source package until destination hashes pass.

## Input/token contracts

For TEXT/CODE/STRUCTURED scenarios:

- preserve frozen raw input hash;
- tokenize with the exact deployment tokenizer;
- record actual token IDs/length/hash;
- do not assume the same text gives the same token count across models.

If an authoritative existing token receipt exists, reuse it after hash validation.

## Acceptance

Asset preparation is complete only when the R1/R2 gates in `C16_FULL_AUTHORITY_RECOVERY_V3_STAGE_ACCEPTANCE.md` pass.
