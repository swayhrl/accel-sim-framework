# C16 Model Completion V7 — Current Gaps and Guardrails

## Accepted state

This CPU-only parallel goal starts from the accepted asset-readiness result:

- base commit: `1d64cd3b996592916e9e34e15c152cbf5a468fa9`
- decision: `C16_ASSET_READINESS_174NEW_V6_R1_PASS_WITH_GAPS`
- Qwen2.5-7B raw: `READY_FOR_FUTURE_QUALIFICATION`, never `FORMAL_ACCEPTED`

The independent LDGSTS consumer-analysis result is also accepted as a read-only scientific reference:

- commit: `cff4b238c5c98c09b5eda96f3e1df4e1d78b57d3`
- decision: `C16_LDGSTS_ANALYSIS_174NEW_V6_R1_PASS`

Do not merge or modify the LDGSTS branch in this goal. It is not needed for the asset work.

Node109 is the active GPU producer line. This goal must not compete with it, modify its environment, or mutate formal capture data.

## Known model/input gaps

The currently canonical six-model asset index contains:

- Llama-3.2-1B
- Qwen2.5-0.5B-Instruct
- Qwen2.5-7B-Instruct raw
- Qwen2.5-7B-Instruct-AWQ
- Qwen3-8B
- DeepSeek-V2-Lite

Current input-authority state:

- Qwen2.5 variants: 21 historical bindings = 3 deployments × 7 scenarios; preserve exactly.
- Llama-3.2-1B: only adopted future S0 authority is currently closed; it is not reconstructed historical R5 authority.
- Qwen3-8B: `NO_HISTORICAL_FROZEN_BINDING`.
- DeepSeek-V2-Lite: `NO_HISTORICAL_FROZEN_BINDING`.

A prospective Qwen3-30B-A3B plan exists for:

- `Qwen/Qwen3-30B-A3B`
- planned exact revision `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`

but V7 must discover the actual local/canonical asset state from receipts and files. Do not assume the large model finished archival merely because the planning document names a path/revision.

## Authority semantics for new inputs

Historical authority and future/prospective authority are different dimensions.

Creating a new future binding must never erase or rewrite:

- `NO_HISTORICAL_FROZEN_BINDING`, or
- `FUTURE_ADOPTED_S0_AUTHORITY_NOT_HISTORICAL_RECOVERY`.

Any newly created binding in V7 must be explicitly classified as prospective, for example:

`PROSPECTIVE_FROZEN_INPUT_AUTHORITY_V1`

and must preserve a separate historical-status field.

Do not borrow Qwen2 token IDs for another tokenizer.
Do not reverse-decode historical token IDs and call the reconstructed text historical authority.
Do not invent a truncation/padding/source-generation rule if the existing source-text authority does not specify one.

## Existing source text first

Before creating any new token binding, locate the original hash-closed C16 source-text authority for TEXT/CODE/STRUCTURED if it exists.

If exact source text plus its generation/truncation policy is available, reuse it and tokenize with the exact archived tokenizer for the target model.

If the source text or policy is missing:

- preserve the gap;
- do not synthesize historical authority;
- do not silently create a new scientific input suite in this goal.

A future common-source campaign may be designed separately if necessary.

## Qwen3-30B large-asset boundary

V7 is metadata-first and low-I/O.

Allowed:

- discover existing source/canonical paths;
- read config/tokenizer/checkpoint index/safetensors headers;
- verify small receipts/manifests;
- report whether the asset is already canonical, source-complete, or archival-blocked.

Not allowed in V7:

- network download;
- a new ~61 GB bulk copy/migration to node164;
- execution from SSHFS;
- GPU layer replay.

If a fully closed canonical Qwen3-30B asset already exists, consume it. Otherwise produce a precise archival-readiness/gap record and stop there.

## Minor R1 fixes are folded into this goal

Do not create a separate repair round. While touching the asset helpers, fix the following small issues:

1. `qwen7_layer_inventory.py` selective dry-run should report per-tensor dtype/shape/exact bytes and total selected parameter bytes, not only tensor/shard names.
2. Replace correctness-critical Python `assert` checks in asset helpers with explicit fail-closed exceptions.
3. AutoAWQ source inventory must include nested C++ sources such as `awq_ext/exllama/exllama_ext.cpp` and `awq_ext/exllamav2/ext.cpp`.
4. AutoAWQ source closure should record `git rev-parse HEAD^{tree}` and require a clean worktree. The missing archive blob remains nonblocking; do not refetch it merely to recompute the recorded archive SHA.
5. Make the capture-path audit generator reproduce the final committed audit rows deterministically rather than relying on manual post-generation edits.

These are engineering hygiene fixes only. They must not change prior scientific decisions.

## Non-negotiable boundaries

CPU-only. No CUDA inference. No NCU/NVBit. No simulator inheritance.

Do not mutate:

- node164 formal raw data;
- catalog admission state;
- accepted Qwen2 historical bindings;
- accepted Llama S0 adopted authority;
- AutoAWQ canonical source tree;
- node109 producer directories or environments.

Large payloads stay on node164. Git contains only code and compact review evidence.
