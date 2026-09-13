# Phase A — identity and asset recovery handoff

## Purpose

Recover exact, authoritative model identities and assets for the four remaining campaign models before any GPU/model execution.

This phase is metadata-only until an exact identity is frozen.

## Models

```text
qwen_0p5
qwen_7b_awq
deepseek
glm
```

The generic labels are not exact identities.

## Evidence search order

Search, in this order:

1. current active repository documents/configs/manifests/receipts;
2. git history on the active repository for model IDs/revisions/package names;
3. prior retained campaign packages and manifests;
4. local server model/cache roots;
5. only after exact identity is known, authoritative upstream availability.

### Bounded local roots

Inspect metadata under known roots when present:

```text
/root/autodl-tmp
/root/autodl-fs
/root/.cache/huggingface
$HF_HOME
$TRANSFORMERS_CACHE
$HUGGINGFACE_HUB_CACHE
/workspace
/data
```

Do not run an unbounded `find /`.

Do not read shell history, credentials, access tokens, SSH keys, or unrelated user secrets.

## Exact identity requirements

A model may advance from Phase A only if the following are frozen:

```text
model_key
exact_model_id_or_local_package_id
revision_or_content_manifest
architecture/model_type
quantization
weight format
dtype expectation
tokenizer/input contract
batch
input length
decode/generation length
backend/device-map/offload contract
asset root
config hash
weight/index manifest hash
```

If authoritative project evidence resolves an exact model ID + revision but the local asset is absent, downloading that exact revision from its authoritative upstream is permitted under the recovery authorization, subject to disk-space and access controls.

No approximate replacements.

## Special model rules

### Qwen 0.5

Do not assume a particular Qwen generation (`Qwen`, `Qwen1.5`, `Qwen2`, `Qwen2.5`) from the `0.5` label alone. Recover the exact historical project identity.

### Qwen 7B AWQ

AWQ is part of the scientific identity. Do not replace it with FP16/BF16/GPTQ/GGUF or a different parameter scale.

### DeepSeek

Do not guess between V2/V3/R1/distill/coder/chat/base variants. Freeze the exact historical project target.

### GLM

Do not guess between ChatGLM/GLM-4/GLM-4.x variants. Freeze the exact historical project target.

## Download/fetch rules

If an exact identity is recovered but missing locally:

1. estimate asset size and verify storage safety;
2. create an isolated destination, never overwrite existing assets;
3. fetch only the exact model/revision;
4. record source, revision, file list, sizes and SHA256/content hashes;
5. validate config/architecture/quantization against the frozen identity;
6. mark `IDENTITY_AND_LOCAL_ASSET_RECOVERED` only after closure.

If access is gated and credentials are unavailable, stop only that model with:

```text
BLOCKED_ASSET_FETCH_AUTH_REQUIRED
```

If authoritative identity itself cannot be recovered, use:

```text
BLOCKED_IDENTITY_UNRESOLVED_REQUIRES_USER
```

Do not call a model `ASSET_UNAVAILABLE` just because one directory does not contain `config.json`.

## Required output

Produce:

```text
POST_LLAMA_MODEL_IDENTITY_MATRIX.tsv
POST_LLAMA_ASSET_INVENTORY.json
```

For each model include one of:

```text
IDENTITY_AND_LOCAL_ASSET_RECOVERED
IDENTITY_RECOVERED_ASSET_MISSING
BLOCKED_ASSET_FETCH_AUTH_REQUIRED
BLOCKED_IDENTITY_UNRESOLVED_REQUIRES_USER
```

No GPU run is authorized by Phase A itself.
