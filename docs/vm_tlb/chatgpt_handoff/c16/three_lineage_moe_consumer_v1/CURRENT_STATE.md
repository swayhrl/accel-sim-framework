# C16 Three-Lineage MoE Consumer — Current State V1

## Purpose

This stage begins only after three independent model-lineage MoE expert `down_proj` anchors are accepted.

The task is **not new GPU capture**. It is a CPU-side, node164-authority consumer analysis on 174-new.

Goal:

> Recompute Qwen3-30B, DeepSeek-V2-Lite, and OLMoE from their accepted raw evidence using one common analysis contract; determine which observed memory-behavior patterns are shared across all three model lineages, which are only two-lineage patterns, and which are implementation/model-specific.

Do not design a new TLB/cache mechanism in this Goal.

---

## Node roles

- node109: producer only; no new work required for this consumer
- 174-new: independent consumer / analysis coordinator
- node164: accepted raw/catalog authority

Node164 root visible on 174-new:

`/root/share/mnt164/huangrulin/c16_ai_workload`

Do not copy model weights to 174-new.

---

## Accepted lineage 1 — Qwen3-30B-A3B

Producer authority:

`hrl/c16-qwen3-30b-s2-formal-capture-109-v3@28620a89d55fd9230103a31d31d14757b57e1e0f`

Accepted raw RUN_ID:

`C16R_qwen3-30b-a3b_s2-text_decode_nvbit-warp-mref-shard_s2-dec3-natural-expert21-down_20260917T034400Z_e210c0de5678`

Node164 raw root:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen3-30b-a3b_s2-text_decode_nvbit-warp-mref-shard_s2-dec3-natural-expert21-down_20260917T034400Z_e210c0de5678`

Authority audit facts from accepted V25 consumer:
- source manifest SHA: `259b34c75ed8adbd8132d56e23a41fc02da97338f8510027f7da77ccb52dcd83`
- catalog entry SHA: `80c9d1309fb8d3f15514c9668ac00a6d8839cb6858aca7e347755eed58d2e434`
- transfer ACK SHA: `f59c9181eb5a6371d93cf648ff15aa771f4af6de04bd9121c9bf2090fb2731f4`
- semantic scope: S2 Decode3, Layer24, natural Expert21 `down_proj`
- natural top-8: `[21,89,108,62,111,23,125,8]`
- routing topology: top-8 / 128 experts
- input width: 768
- output width: 2048
- weight shape: `[2048,768]`
- weight bytes: 3,145,728
- static selected GLOBAL-MREF paths: 243
- executed / zero: 41 / 202
- warp records: 100,352
- active-lane events: 3,147,776
- function family: BF16 cuBLAS internal gemvx; accepted V25 relation identifies template parameter variant `...,false,true,true,false,7,...`
- accepted V25 grid/block: `512x1x1 / 32x4x1`

Historical V25 typed fractions:
- weight: 0.4996746909564086
- input: 0.4996746909564086
- output: 0.0006506180871828237
- other: 0

Historical V25 executed-shard distributions:
- active-lane events min/max/median: 2048 / 131072 / 65536
- 4K pages min/max/median: 1 / 768 / 2
- 64K pages min/max/median: 1 / 48 / 1
- 2M pages min/max/median: 1 / 2 / 1
- 128B lines min/max/median: 12 / 24576 / 32

These are historical expectations, not input truth for the new recompute.

---

## Accepted lineage 2 — DeepSeek-V2-Lite

Producer authority:

`hrl/c16-deepseek-v2-lite-s2-producer-109-v23r1@baf892ced6d66cbacabb995caf095e5280995097`

Accepted raw RUN_ID:

`C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23`

Node164 raw root:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23`

Authority facts:
- source manifest SHA: `d98b4a077afe9e7f2ce32479484e9c1148548b1ef1802c9b002dd70250b7b638`
- catalog entry SHA: `9ece3f570fbdaa8e026da39bee94c7f15b2c60bf14e292a66f6026104d18d81d`
- transfer ACK SHA: `fe4768a91606bbbf89f1b28a897f0a6648fb8e83d3d621093313e03743ec1acf`
- semantic scope: S2 selected decode state, Layer1, natural Expert4 `down_proj`
- natural top-6: `[4,24,25,55,60,26]`
- routing topology: top-6 / 64 routed experts + 2 shared experts
- selected expert: 4
- input width: 1408
- output width: 2048
- weight shape: `[2048,1408]`
- weight bytes: 5,767,168
- static selected paths: 243
- executed / zero: 169 / 74
- warp records: 362,496
- active-lane events: 11,538,432
- function family: BF16 cuBLAS internal gemvx; V25 relation identifies template `...,false,true,true,false,6,...`

Historical V25 typed fractions:
- weight: 0.4998225062122826
- input: 0.4998225062122826
- output: 0.0003549875754348598
- other: 0

Historical V25 executed-shard distributions:
- active-lane events min/max/median: 4096 / 131072 / 65536
- 4K pages min/max/median: 1 / 1408 / 2
- 64K pages min/max/median: 1 / 88 / 1
- 2M pages min/max/median: 1 / 3 / 1
- 128B lines min/max/median: 1 / 4096 / 32

These are historical expectations, not input truth for the new recompute.

---

## Accepted lineage 3 — OLMoE

Final authority commit:

`hrl/c16-olmoe-v40-formal-admission-174new-v1@85563ec6f55a0ad743d21483aa49c24fdb5cf3bf`

Accepted RUN_ID:

`C16R_olmoe-1b-7b-0125-instruct_s2-t2048-d32_decode32_nvbit1771-c16warp1_expert58-down-proj-actual-a_20260922T100810Z_fc0f3cf67edf`

Node164 immutable raw path:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_olmoe-1b-7b-0125-instruct_s2-t2048-d32_decode32_nvbit1771-c16warp1_expert58-down-proj-actual-a_20260922T100810Z_fc0f3cf67edf`

Authority facts:
- manifest SHA: `8f3e5e338166a2ebc4da6b9a55986980d31227f3d0e383ca5a1f24d0d924f31b`
- raw selector SHA: `d70035debd62f0821f7b4b0c802ecdd3ca101b7213eafb591b3cc56438a271eb`
- canonical selector V1 SHA: `cb20c01619acf563de69776a7a098b21c31c6ce6d836ea0bc0beab9fe42c979b`
- catalog entry SHA: `676422708f865c6b3287998dcde3dd126a469e83d3245bcf00fe11d07b9c1637`
- admission receipt SHA: `33646fd106ea3773aca68d62d3fb0d24f32f3598aa711722e38e5b54cd9f5c81`
- positive ACK SHA: `9c4d08a960f53acece00dbb3143cba460c22bc638ff4a879833c0e4460b98e39`
- semantic scope: S2_TEXT B1/T2048/D32, Layer1 decode32, natural Expert58 `down_proj`
- natural top-8: `[58,59,47,51,25,15,12,48]`
- routing topology: top-8 / 64 experts
- input width: 1024
- output width: 2048
- weight shape: `[2048,1024]`
- weight bytes: 4,194,304
- evidence condition: actual-JIT variant A
- selected static paths: 243
- executed / zero: 129 / 114
- warp records: 132,096
- active-lane events: 4,196,352
- typed role events:
  - input: 2,097,152
  - weight: 2,097,152
  - output: 2,048
  - other: 0
- typed fractions:
  - input: 0.4997559785261103
  - weight: 0.4997559785261103
  - output: 0.0004880429477794046
- SUM_OF_PER_SHARD_UNIQUES:
  - 128B lines: 131,168
  - 4K pages: 65,602
  - 64K pages: 4,161
  - 2M pages: 193

OLMoE variant B remains unformalized. Do not claim OLMoE implementation-variant invariance.

---

## Existing two-lineage baseline

Accepted two-lineage consumer:

`hrl/c16-cross-model-moe-q30-deepseek-174new-v25@2538feb8862cd9b1828e9c805cb88ee46a4741ce`

V25 already established:
- Q30 and DeepSeek accepted authority audit PASS
- both are natural-routed BF16 expert `down_proj` anchors
- both have complete 243-shard accepted scope
- page/line/membership results are descriptive footprints only
- static indices were not compared across models
- no cross-process VA relation, chronology, reuse distance, cache/TLB causality, or population-routing claim
- conclusion was only a two-lineage MoE-family pattern
- explicit next step was to wait for a third independent MoE lineage

The new consumer must reproduce the Q30/DeepSeek numbers from raw evidence before extending V25 to three lineages.

---

## Important implementation-coupling caveat

The three models are independent **model lineages**, but the GPU implementation anchors are not necessarily independent implementation lineages.

Accepted evidence indicates:
- Q30 uses the BF16 internal gemvx family with template variant ending in `...,7,...`
- DeepSeek uses the same broad BF16 internal gemvx family with template variant ending in `...,6,...`
- OLMoE actual-JIT variant A is also the BF16 internal gemvx family with variant `...,6,...`

Therefore the final interpretation must explicitly distinguish:

1. model-lineage independence
2. operator-semantic similarity
3. runtime/kernel-family coupling

If DeepSeek and OLMoE resolve to the same/sufficiently identical internal gemvx implementation family, a three-model common pattern must **not** be presented as three independent implementation confirmations.

Preferred wording when supported:

> three-independent-model-lineage MoE expert-down-proj pattern within the observed cuBLAS gemvx deployment anchors

The previously permitted short phrase `three-independent-lineage MoE-family pattern` remains acceptable only with the implementation-coupling caveat nearby.

---

## Global analysis prohibitions

Do not compute or infer:
- cross-shard absolute VA union
- cross-shard global chronology
- cross-shard reuse distance
- fresh-process absolute VA relationship
- real global L2 arrival order from shard order
- cache/TLB causality from these address traces alone
- static-index equality across models as instruction equivalence
- routing-population statistics from one frozen natural state per model
- matched-input causality across Q30 / DeepSeek / OLMoE

No new GPU capture is authorized in this Goal.
