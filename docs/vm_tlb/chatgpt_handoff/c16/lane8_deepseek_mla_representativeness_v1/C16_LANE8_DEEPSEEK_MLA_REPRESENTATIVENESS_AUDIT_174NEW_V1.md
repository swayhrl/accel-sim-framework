# C16 Lane 8 Handoff — DeepSeek-V2-Lite MLA Representation Audit V1

**Date:** 2026-09-28  
**Execution node:** `174-new`  
**Lane:** `Lane 8`  
**Role:** CPU-only source + accepted-evidence audit  
**GPU:** forbidden  
**GPU lock:** forbidden  
**Can run in parallel with:** Lane 4@174-new, Lane 6@174-new, Lane 7@109  
**Goal:** `C16_DEEPSEEK_MLA_REPRESENTATIVENESS_AUDIT_174NEW_V1`

This Goal is motivated by the just-completed Qwen3 result: an apparently architectural long-context memory behavior turned out to be implementation/backend-specific. Before spending more effort on DeepSeek MLA cache/TLB questions, determine whether our accepted DeepSeek persistent-cache evidence actually reflects **compressed MLA KV storage** or a HuggingFace implementation that materializes/caches expanded per-head K/V.

Do not run a new model. This is an evidence and source audit.

---

## 1. Existing accepted authorities

Model:
`deepseek-ai/DeepSeek-V2-Lite`

Revision:
`604d5664dddd88a0433dbae533b7fe9472482de0`

### V26 S2 persistent MLA producer

Branch:
`hrl/c16-deepseek-v2-lite-persistent-mla-109-v26`

Read:
`docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_PERSISTENT_MLA_109_V26/`

Key accepted facts:

- no clean single-object direct-read target was found;
- QK target is a mixed consumer of persistent prefix + current appended position;
- S2 QK formal: 20 selected direct-GLOBAL paths, 16 executed/4 zero, 7,116,816 active-lane events;
- cache objects recorded around decode:
  - key: `[1,16,T,192]` BF16;
  - value: `[1,16,T,128]` BF16;
- cache update replaces storage while preserving prior content as prefix.

### V27 S3 extension

Branch:
`hrl/c16-deepseek-v2-lite-s3-mixed-qk-109-v27`

Read:
`docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_S3_MIXED_QK_109_V27/`

Key accepted facts:

- same mixed QK semantic class;
- S3 persistent positions = 8192;
- S3 QK key operand: `[1,16,8193,192]`;
- total active-lane events scale to 113,785,872;
- producer-reported S3/S2 event ratio ≈ `15.9883`;
- S3 kernel implementation differs from S2.

### V30 CPU consumer

Branch:
`hrl/c16-deepseek-s2-s3-consumer-174new-v30`

Read:
`docs/vm_tlb/review_packs/C16_DEEPSEEK_S2_S3_CONSUMER_174NEW_V30/`

It closes the existing mixed-QK lineage but does **not** settle whether the cached representation corresponds to the intended compressed-MLA representation.

---

## 2. Exact model-source question

Audit the exact model revision:

`deepseek-ai/DeepSeek-V2-Lite@604d5664dddd88a0433dbae533b7fe9472482de0`

Obtain and hash, at minimum:

- `config.json`
- `modeling_deepseek.py`

Use the exact revision, not current main.

Record:
- source SHA256;
- retrieval path/URL or local authority;
- relevant line/function anchors.

From exact config bind:
- num_attention_heads;
- num_key_value_heads;
- kv_lora_rank;
- qk_nope_head_dim;
- qk_rope_head_dim;
- v_head_dim;
- use_cache.

Then answer from source:

1. Is `compressed_kv` produced first?
2. Is it immediately expanded by `kv_b_proj` into per-head K/V before cache update?
3. What exact tensors are passed to `past_key_value.update(...)`?
4. Are the cached tensors full per-head key/value or compressed latent objects?
5. Does the exact accepted runtime therefore retain the canonical MLA compressed-cache advantage, or not?

Do not infer from names; bind source statements to exact tensor shapes and V26/V27 receipts.

---

## 3. Compare three representation levels

Create a table with:

### A. Model-semantic latent representation

From exact config/source:
- `kv_lora_rank`
- decoupled RoPE component if separately retained by the architecture
- theoretical per-token latent dimensions implied by the exact source

Do not use paper-level formulas unless they are directly matched to this source/config.

### B. Accepted runtime cache representation

From V26/V27 receipts:
- actual cached key shape/bytes;
- actual cached value shape/bytes;
- bytes per sequence position;
- S2 and S3 total cache bytes.

### C. Immediate QK consumer representation

From accepted QK replay:
- query shape;
- key-transposed operand shape;
- output shape;
- persistent-prefix and current-position composition.

The goal is to state clearly whether A, B and C are the same representation or different materializations.

---

## 4. Quantify representation amplification

If source + receipts support it, compute:

- accepted runtime cached bytes per token;
- source-level latent bytes per token for the exact revision;
- runtime-cache / latent-cache ratio.

Keep key/value and any RoPE component accounting explicit.

Do not silently count the same component twice.

If the exact source cannot justify a clean latent-cache byte count, report `UNRESOLVED` instead of inventing one.

Also report:
- S2→S3 context scaling of runtime cache bytes;
- S2→S3 event scaling from accepted consumer;
- whether the ~16x event increase is explained by context ratio, launch/implementation change, or remains mixed.

Do **not** label lane events as DRAM bytes.

---

## 5. Implementation-history check

This is a source audit, not a performance experiment.

Check whether a later public Transformers DeepSeek-V2 implementation has changed cache semantics to retain compressed latent K/V before expansion.

If you inspect a later implementation:
- pin exact release/commit;
- record it as **later implementation context only**;
- never substitute it for the accepted V26/V27 runtime;
- do not claim performance superiority from source structure.

The only purpose is to answer whether the accepted 2026 C16 measurement represents an implementation choice that later frameworks can avoid.

If exact later source identity cannot be closed, omit this section.

---

## 6. Scientific interpretation

The final Chinese interpretation must answer:

1. What exactly did V26/V27 measure?
2. Is the persistent cache in that runtime compressed MLA state, or expanded per-head K/V?
3. Which observed context-scaling behavior is model-semantic?
4. Which observed behavior is implementation-specific?
5. Does any existing DeepSeek result still justify a cache/TLB mechanism?
6. Is a future matched implementation comparison worth GPU time?

Use plain Chinese in the report.

Possible evidence-bounded outcomes:

- the accepted HF runtime expands K/V before caching, so V26/V27 characterize a **full per-head cache implementation**, not the intended compressed MLA cache;
- the accepted runtime genuinely caches compressed latent state, in which case preserve that result and explain how QK materialization occurs;
- mixed/ambiguous source/runtime evidence, in which case keep the question open.

Do not use a machine label as the user-facing conclusion.

---

## 7. Required outputs

Create:

`docs/vm_tlb/review_packs/C16_DEEPSEEK_MLA_REPRESENTATIVENESS_AUDIT_174NEW_V1/`

At minimum:

- `AUTHORITY_AUDIT.json`
- `EXACT_SOURCE_AUDIT.tsv`
- `CONFIG_BINDING.json`
- `V26_V27_CACHE_OBJECTS.tsv`
- `REPRESENTATION_CHAIN.md`
- `REPRESENTATION_BYTES.tsv`
- `S2_S3_SCALING_REINTERPRETATION.json`
- `IMPLEMENTATION_HISTORY.md` if exact later source is audited
- `SCIENTIFIC_INTERPRETATION.md`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

No raw mutation.

---

## 8. Branch

Base:

`b2975f163f319b5e339808877246c49cbf8a64cd`

Suggested branch:

`hrl/c16-deepseek-mla-representativeness-audit-174new-v1`

---

## 9. Absolute prohibitions

Do not:
- use GPU;
- request GPU lock;
- run DeepSeek model inference;
- run NVBit/NCU/NSYS;
- read Lane4 partial results;
- invent compressed-cache byte counts;
- infer TLB miss rate from page counts;
- infer DRAM traffic from active-lane events;
- design a cache/TLB mechanism in this Goal;
- modify V26/V27/V30 accepted artifacts.

---

## 10. Solve-and-continue / STOP

Ordinary path/source parsing issues may be solved automatically.

STOP only if:
- exact accepted model revision source cannot be obtained/bound;
- accepted V26/V27 source/runtime identity is inconsistent;
- cached object semantics cannot be reconciled with source;
- required review pack cannot be hash-closed.

Otherwise complete in one Goal.

Finish:

`validate -> git diff --check -> SHA256SUMS -> commit -> push -> fetch-back verify -> clean -> report -> STOP`

User-facing report must use clear Chinese, not internal shorthand as the main conclusion.
