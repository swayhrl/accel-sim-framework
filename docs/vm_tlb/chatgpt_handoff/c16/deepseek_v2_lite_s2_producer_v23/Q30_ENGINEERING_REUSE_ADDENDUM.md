# DeepSeek V23 addendum — reuse Qwen3-30B engineering, not Qwen3-30B scientific assumptions

This addendum is part of the DeepSeek-V2-Lite node109 V23 producer Goal.

## Why this addendum exists

A parallel C16 Qwen3-30B-A3B line has already solved much of the engineering problem of executing a model substantially larger than RTX4080 memory without changing model semantics.

DeepSeek V23 should reuse that proven engineering pattern instead of independently rebuilding another large-model streaming framework.

However, Qwen3-30B and DeepSeek-V2-Lite remain **independent scientific lineages**. Do not inherit Q30 kernel identities, target semantics, launch ordinals, static MREF sets, attention behavior, router behavior, expert IDs, or cache representation assumptions.

## Accepted Q30 engineering/scientific upstream references

Model:

`Qwen/Qwen3-30B-A3B@ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`

Useful accepted commits:

- S0 exact semantic layer streaming + replay: `ba4358b8059be4fb5756f49852e50ecfe7dea9a3`
- S0 target qualification: `acbda39f5714cedb0e8b88ec32b07b4db2845885`
- S2/T2048 exact semantic state + replay: `ee67225edc8fc5868de585d38e0391cbeb755d9f`

The currently prepared but **not yet executed** Q30 S2 target requalification launcher is:

- branch: `hrl/c16-qwen3-30b-s2-target-requalification-v1`
- HEAD: `832949ec633de67b1b95343cc6e98be9bcb33b19`

DeepSeek V23 must not depend on an unexecuted Q30 requalification result.

## Q30 engineering pattern already proven on RTX4080

The Q30 line demonstrated the following useful pattern:

1. canonical large-model asset authority and verified node109 working copy;
2. shard-aware exact safetensors loading;
3. per-layer materialization rather than full-model residency;
4. strict state_dict key/shape/dtype injection;
5. explicit release of inactive layer weights back to meta / non-resident state;
6. sequential exact semantic layer streaming through the full model;
7. frozen `TARGET_LAYER_STATE` authority;
8. fresh-process exact complete-layer replay;
9. source-state/router bitwise-equivalence checks;
10. preservation of original BF16/runtime/backend/routing semantics;
11. layer-local NSYS/NCU/NVBit qualification rather than pretending streamed execution is full-model performance evidence;
12. normal ownership of `/data/c16/locks/c16_gpu_campaign.lock` for GPU actions.

Q30 reached exact S2/T2048 Layer-24 states and replay without full BF16 residency. This is direct evidence that the general layer-streaming/replay strategy is operationally viable on the RTX4080 for a much larger model.

## Reusable code references

Inspect the accepted Q30 implementation under:

`util/vm_tlb/c16/qwen3_30b/`

especially the architecture-neutral ideas in:

- `authority.py`
- `materializer.py`
- `provision.py`
- `state.py`
- `streaming.py`
- `q30_s0_executor.py`

Reuse or factor shared helpers only when semantics remain exact. Do not copy Q30 model-specific parameter names, cache logic, layer signatures, routing rules, or expert-layout assumptions into DeepSeek.

## What DeepSeek may reuse directly as methodology

DeepSeek V23 should prefer the Q30 pattern for:

`checkpoint/index authority -> exact selective layer load -> execute true layer -> release -> next layer -> freeze target state -> fresh-process full-layer/operator replay -> equivalence gate -> profiler/trace target qualification`

Also reuse the discipline of preserving:

- exact hidden-state hashes;
- exact position/cache state;
- exact router outputs and selected experts;
- exact runtime/backend identity;
- exact target-layer replay state;
- peak/residual allocation measurements;
- no full-model performance claims from the streaming pass.

## What must remain DeepSeek-specific

DeepSeek must independently establish from its actual runtime:

- MLA cache representation and cache API;
- whether persistent storage is compressed latent, expanded K/V, or another representation;
- `kv_a` / `kv_b` runtime dataflow;
- RoPE/nope split and reconstructed attention operands;
- exact first usable MLA formal target;
- actual first MoE layer used for the canonical S2 path;
- natural router top-k selected expert IDs and weights;
- shared-expert behavior if present in the exact runtime/config;
- grouped/fused vs per-expert execution path;
- exact expert-specific or grouped-MoE object attribution;
- DeepSeek-specific SASS/static address paths.

No Q30 attention or expert kernel identity may be treated as evidence for DeepSeek.

## Cross-lineage strategy

Keep Q30 and DeepSeek as separate producer lines through their first accepted S2 MoE anchors.

Only after both sides have accepted, independently consumed MoE evidence should 174-new create a cross-model MoE comparison. The first cross-model comparison should use matched semantic classes where supportable, for example:

- natural router / assignment statistics;
- selected routed-expert projection memory path;
- expert working-set / assignment scaling;
- per-shard page/line footprint distributions;
- static path structure;
- grouped-vs-per-expert execution differences.

Do not force a matched target when runtime implementations are semantically different.

Q30 attention remains a Qwen-specific/GQA-attention line; DeepSeek MLA remains a DeepSeek-specific attention line. They should not be collapsed merely because both models are MoE.

## Scheduling rule

The two scientific lines may progress independently in Git and CPU-side analysis, but node109 GPU campaigns are serialized by the existing GPU lock and formal admissions remain serialized by `FORMAL_ADMISSION_CONCURRENCY=1`.

For V23, prioritize DeepSeek S2 MLA+MoE producer as currently planned. Do not execute the pending Q30 `832949...` Goal concurrently on the same GPU.
