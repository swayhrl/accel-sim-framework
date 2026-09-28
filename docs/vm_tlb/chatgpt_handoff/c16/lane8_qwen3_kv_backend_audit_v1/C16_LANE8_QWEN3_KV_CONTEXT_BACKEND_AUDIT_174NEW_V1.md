# C16 Lane 8 Handoff — Qwen3 KV Context Scaling + Backend Representativeness Audit V1

**Date:** 2026-09-28  
**Execution node:** `174-new`  
**Lane:** `Lane 8`  
**Role:** CPU-only independent consumer / source audit  
**GPU:** forbidden  
**GPU lock:** forbidden  
**Can run in parallel with:** Lane 4@174-new, Lane 7@109  
**Goal:** `C16_QWEN3_KV_CONTEXT_BACKEND_AUDIT_174NEW_V1`

---

# 0. Why this is worth doing

Lane 8's prior MoE warp-geometry screen is accepted and closed:

- branch: `hrl/c16-moe-warp-request-geometry-screen-174new-v1`
- commit: `2afdf832273f31df496d7424ec6b426c6aabdfc3`
- final scoped result: `FAMILIAR_BROADCAST_WITH_NO_NEW_OPPORTUNITY`

Do not keep mining that same MoE trace for another mechanism.

A different, already-collected C16 dataset contains a stronger unresolved scientific question: Qwen3 long-context KV `repeat_kv(K)` behavior.

The producer already captured exact S2 and S3 full-scope formal raw:

- S2: T2048
- S3: T8192
- exact target: `layer0.self_attn.repeat_kv(K)`
- evidence class: `KV_STORAGE_DIRECT_READ`

Producer status is PASS, but the final independent S2+S3 consumer closure was designed and apparently never published. More importantly, the accepted runtime used `attention_backend=eager`, so before treating the measured 4x KV expansion as an architectural property we must determine whether it is model-intrinsic or backend-specific.

This Goal therefore combines two CPU-only tasks in one pass:

1. finish the independent S2→S3 raw-data closure from node164;
2. audit the exact Transformers 4.51.0 Qwen3 attention backends to classify whether explicit `repeat_kv` materialization is backend-dependent.

This is useful even if the final answer is negative: it prevents building a TLB/cache mechanism around an eager-backend artifact.

---

# 1. Immutable producer authority

Framework producer:

`hrl/c16-qwen3-s3-kv-scaling-109-v20`

HEAD:

`c94825dab9b114e468a83cdad009181f23add608`

Producer decision:

`C16_QWEN3_S3_KV_SCALING_109_V20_PASS`

Producer review pack:

`docs/vm_tlb/review_packs/C16_QWEN3_S3_KV_SCALING_109_V20/`

Exact model:

`Qwen/Qwen3-8B`

Revision:

`b968826d9c46dd6066d109eabc6255188de91218`

Runtime in accepted producer:

- torch 2.5.1+cu124
- transformers 4.51.0
- BF16
- `attention_backend=eager`
- RTX4080 / SM89

Do not run the model again.

---

# 2. Exact accepted raw authorities

## S2

RUN_ID:

`C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v20-s2-repeat-k_20260916T162000Z_202020202020`

Node164 raw:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v20-s2-repeat-k_20260916T162000Z_202020202020`

Catalog:

`/root/share/mnt164/huangrulin/c16_ai_workload/catalog/entries/C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v20-s2-repeat-k_20260916T162000Z_202020202020.json`

Expected catalog SHA256:

`aabeb406523d55355432b3367c6089b43a8c7b4821b97a100717a1b37480a2c8`

Expected source manifest SHA256:

`f52fcdf0e281407f106f4f478fa1072a4ec299dde30df7c32abb089e8b7c6116`

Expected producer facts to independently audit:

- K-post shape `[1,8,2049,128]`
- repeat-K shape `[1,32,2049,128]`
- K-post bytes `4,196,352`
- repeat-K bytes `16,785,408`
- grid_x `16,392`
- direct-GLOBAL static set count `8`
- executed 8 / zero 0
- active-lane events `16,785,408`
- CTA x `0..16391`
- overflow 0

## S3

RUN_ID:

`C16R_qwen3-8b_s3-text_decode_nvbit-warp-mref-shard_v20-s3-repeat-k_20260916T163000Z_303030303030`

Node164 raw:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen3-8b_s3-text_decode_nvbit-warp-mref-shard_v20-s3-repeat-k_20260916T163000Z_303030303030`

Catalog:

`/root/share/mnt164/huangrulin/c16_ai_workload/catalog/entries/C16R_qwen3-8b_s3-text_decode_nvbit-warp-mref-shard_v20-s3-repeat-k_20260916T163000Z_303030303030.json`

Expected catalog SHA256:

`b85430200f520506bc2abf3165af018b628c11626d47b7c77e00eb2b03c79082`

Expected source manifest SHA256:

`d986397b7b32dafd7efe3cfcbfaae71dd367d4c8ce0587aa8ea8e35a0acb339b`

Expected producer facts:

- K-post shape `[1,8,8193,128]`
- repeat-K shape `[1,32,8193,128]`
- K-post bytes `16,779,264`
- repeat-K bytes `67,117,056`
- grid_x `65,544`
- static set count 8
- executed 8 / zero 0
- active-lane events `67,117,056`
- CTA x `0..65543`
- overflow 0

Producer-reported S3/S2 grid/event ratio:

`3.998535871156662`

Do not call this exactly 4x without noting the 2049→8193 endpoint effect.

---

# 3. Historical unclosed consumer intent

Read these historical coordination handoffs:

`docs/vm_tlb/chatgpt_handoff/c16/qwen3_s3_kv_consumer_v21/CODEX_174NEW_QWEN3_S3_KV_CONSUMER_V21.md`

`docs/vm_tlb/chatgpt_handoff/c16/qwen3_s3_kv_consumer_v21r1/CODEX_174NEW_QWEN3_S3_KV_CONSUMER_V21R1.md`

The V21R1 contract already identified that a prior V21 attempt was insufficient and required a final S2+S3 independent closure.

Do not merely reproduce its text. Recompute from accepted node164 raw.

---

# 4. Stage A — independent raw closure

Use C16WARP1:

- header `<8sIIQQQ`
- record `<6I32Q`

The accepted tracer correction must be independently checked.

Source LDG static indices:

- 237 → source address from R4:R5
- 475 → R4:R5
- 713 → R4:R5
- 950 → R2:R3

Destination STG:

- 241
- 479
- 717
- 953

For every shard in S2 and S3 recompute:

- static index
- record count
- active-lane events
- overflow
- terminal/classification
- unique CTA coords
- cta_x min/max
- warp IDs
- per-shard 128B lines
- per-shard 4K / 64K / 2M pages
- address min/max

Use only each replay's own ADDRESS_CONTEXT.

Required typed object join:

- 237/475/713/950: all active source addresses join `KV_POST_UPDATE_K`
- 241/479/717/953: all active destination addresses join `KV_DERIVED_REPEAT_K`
- no active address may require cross-process VA joining

Fail closed if the typed split does not hold.

Full-scope gate:

S2:
- each executed shard starts cta_x=0
- reaches 16391
- unique CTA union=16392

S3:
- starts 0
- reaches 65543
- union=65544

No cross-replay VA union.
No cross-shard chronology.
No reconstructed reuse distance.

---

# 5. Stage B — context-scaling and amplification decomposition

After Stage A PASS, recompute S2 vs S3.

Report separately:

## 5.1 Model-semantic storage

For each scenario:

- original KV K-post bytes
- derived repeat-K bytes
- expansion ratio `repeat_K / K_post`

Expected GQA expansion ratio from shapes:

`32 query heads / 8 KV heads = 4`

Treat this as the model/backend tensor-shape transformation, not measured traffic.

## 5.2 Dynamic source-read and destination-write events

Separate source LDG and destination STG static sets.

For each side report:

- active-lane events
- per-shard event counts
- event ratio S3/S2
- 128B/4K/64K/2M footprints
- qualified access widths where source evidence supports them

Answer:

- does source-read work scale approximately with context?
- does destination-write work scale approximately with context?
- does explicit repeat materialization cause source and destination dynamic work proportional to the expanded tensor?

Do not infer actual DRAM bytes from lane events.

## 5.3 Page-footprint descriptors

For source and destination separately:

- per-shard unique 4K/64K/2M pages
- SUM_OF_PER_SHARD_UNIQUES only when aggregated
- pages per MiB of the corresponding tensor
- S3/S2 scaling

This is a translation-footprint descriptor, not TLB miss rate.

Do not propose a page-size/TLB mechanism solely from these numbers.

---

# 6. Stage C — exact backend representativeness audit

This is mandatory.

The accepted producer used Transformers 4.51.0 and `attention_backend=eager`.

Audit the exact public source at tag `v4.51.0`.

Tag tree commit:

`0720e206c6ba28887e4d60ef60a6a089f6c1cc76`

Exact files and Git blob IDs:

- `src/transformers/models/qwen3/modeling_qwen3.py`
  - blob `5fec83d47888e44a0f3e0ffb2b067ce08e4712d3`
- `src/transformers/integrations/sdpa_attention.py`
  - blob `9c924c048ad52929a2d0f890a22295d5a56ef505`
- `src/transformers/integrations/flash_attention.py`
  - blob `a78166ed040b620c6e24a7e2c64c06c96f2d89d9`
- `src/transformers/integrations/flex_attention.py`
  - blob `1aa146e4a40737edd100059f05208da1a6d5e3dc`

Record the exact source locally in the audit via ref/path/blob, not by copying whole upstream files into our repo.

Determine, from source only:

### Eager
Does Qwen3 eager explicitly call `repeat_kv(key, num_key_value_groups)` and same for value?

### SDPA
Does Transformers 4.51.0 SDPA integration also explicitly call `repeat_kv` before PyTorch SDPA when `num_key_value_groups` exists?

### FlashAttention2
Does the integration pass original key/value head counts into FlashAttention without explicit HF `repeat_kv` materialization?

### FlexAttention
Does the exact integration use `enable_gqa=True` for normal power-of-two local query-head count and avoid explicit repeat unless its fallback condition fires?

For the accepted Qwen3-8B head configuration, bind actual:
- num_attention_heads
- num_key_value_heads
- num_key_value_groups

from exact model config/receipt where available.

Do not assume current main behaves identically to 4.51.0.

---

# 7. Stage D — scientific classification

The key question is:

> Is the measured `repeat_kv(K)` scaling a model-intrinsic KV-cache property, or a backend-specific implementation path?

Allowed final labels:

### `EAGER_REPEAT_KV_AMPLIFICATION_INDEPENDENTLY_CLOSED_BACKEND_SPECIFIC`

Use if:
- S2/S3 raw closure passes;
- explicit eager repeat materialization is confirmed;
- at least one supported alternative backend does not use the same explicit materialization path.

### `REPEAT_KV_MATERIALIZATION_SHARED_BY_EAGER_AND_SDPA_NOT_FLASH`

Can be a qualification if source audit supports it.

### `QWEN3_KV_CONTEXT_SCALING_CLOSED_NO_ARCHITECTURE_GENERALIZATION`

Use if the data are valid but backend dependence makes it unsuitable as a general architecture claim.

### `QWEN3_KV_CONTEXT_SCALING_HAS_BACKEND_INDEPENDENT_COMPONENT`

Use only if exact source supports an invariant component. State precisely what component.

### typed blocker
If raw closure or source identity fails.

Do NOT output:

- `LLM_KV_CACHE_ALWAYS_EXPANDS_4X`
- `TLB_PRESSURE_PROVEN`
- `CACHE_BOTTLENECK_PROVEN`
- `FLASH_ATTENTION_ELIMINATES_ALL_KV_TRAFFIC`
- any performance ranking without measurement

---

# 8. Why this matters for future experiments

If explicit repeat materialization is backend-specific, recommend:

- do not build a cache/TLB mechanism around repeat-K alone;
- preserve V20 as an eager/SDPA-style implementation anchor;
- if deployment relevance later matters, a minimal 109 backend-sensitivity experiment may compare exact eager vs a legal optimized backend, but this Goal does not authorize it.

If a backend-independent long-context property remains, formulate the exact property for future architecture study.

Do not automatically queue GPU work.

---

# 9. Required review pack

Create:

`docs/vm_tlb/review_packs/C16_QWEN3_KV_CONTEXT_BACKEND_AUDIT_174NEW_V1/`

At minimum:

- `AUTHORITY_AUDIT.json`
- `STATIC_PATH_AUDIT.json`
- `S2_SHARD_FINGERPRINTS.tsv`
- `S3_SHARD_FINGERPRINTS.tsv`
- `S2_OBJECT_JOIN.tsv`
- `S3_OBJECT_JOIN.tsv`
- `S2_FULL_SCOPE_AUDIT.json`
- `S3_FULL_SCOPE_AUDIT.json`
- `S2_VS_S3_CONTEXT_SCALING.json`
- `SOURCE_DESTINATION_AMPLIFICATION.tsv`
- `PAGE_FOOTPRINT_DESCRIPTORS.tsv`
- `BACKEND_SOURCE_AUDIT.tsv`
- `BACKEND_REPRESENTATIVENESS.md`
- `NCU_EVIDENCE_AUDIT.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Implement/reuse a CPU-only consumer under:

`util/vm_tlb/c16/`

Reuse valid Lane8 parsing helpers when appropriate, but do not force MoE-specific assumptions onto this dataset.

---

# 10. New branch

Base:

`2afdf832273f31df496d7424ec6b426c6aabdfc3`

Suggested branch:

`hrl/c16-qwen3-kv-context-backend-audit-174new-v1`

No GPU.
No GPU lock.
Single CPU worker is sufficient unless pure file hashing benefits safely from bounded parallelism.

---

# 11. Absolute prohibitions

Do not:

- use GPU;
- request GPU lock;
- run the Qwen3 model;
- run NVBit/NCU/NSYS;
- mutate node164 raw/catalog;
- use Lane4 partial results;
- build a TLB/cache mechanism;
- infer TLB misses from page counts;
- infer DRAM traffic from lane events;
- form cross-replay VA unions;
- infer chronology across shards;
- fetch a new Qwen3 model;
- substitute current Transformers main for exact 4.51.0 source.

---

# 12. Solve-and-continue / STOP

Ordinary file/path/parser issues may be solved automatically.

STOP only on:

- accepted authority hash mismatch;
- raw/parser integrity failure;
- typed source/destination object join failure;
- full-scope failure;
- exact Transformers 4.51.0 source identity unavailable;
- source behavior is ambiguous enough to invalidate backend classification;
- review pack cannot be hash-closed.

Otherwise complete the entire Goal.

---

# 13. Finish

`validate -> git diff --check -> SHA256SUMS -> commit -> push -> fetch-back verify -> clean -> report -> STOP`

Report:
- branch/HEAD/tree;
- S2/S3 independent closure status;
- source vs destination scaling;
- page-footprint scaling;
- exact eager/SDPA/FA2/Flex backend classification;
- final scientific label;
- whether any future GPU comparison is scientifically justified.

Do not automatically start that GPU comparison.
