# C16 Cross-Model MoE Q30↔DeepSeek Independent Consumer — 174-new V25

## Execution mode

Execute this task in **GOAL MODE**. This is one autonomous CPU-only cross-model MoE consumer/closure Goal on 174-new.

Use:

- repo: `/root/workspace/accel-sim-framework`
- node164: `/root/share/mnt164`
- existing `gh auth` + HTTPS credential integration
- do **not** switch to SSH
- known stdout-capture issue: if decisive stdout/stderr is empty, redirect to `/tmp/...` files and read them

Do not run GPU work. Do not mutate accepted raw/catalog.

## Exact producer authorities

### Qwen3-30B-A3B

Producer branch/head:

`hrl/c16-qwen3-30b-s2-formal-capture-109-v3`

`28620a89d55fd9230103a31d31d14757b57e1e0f`

Exact formal run:

`C16R_qwen3-30b-a3b_s2-text_decode_nvbit-warp-mref-shard_s2-dec3-natural-expert21-down_20260917T034400Z_e210c0de5678`

Semantic anchor:

`model.layers.24.mlp.experts.21.down_proj`

Natural top-8 expert IDs:

`[21,89,108,62,111,23,125,8]`

Replay shape:

- input `[1,768]` BF16
- output `[1,2048]` BF16
- bitwise replay PASS

Expected static set:

- 243 direct-GLOBAL MREF shards
- producer summary: 41 executed / 202 `ZERO_EXECUTION_PROVEN`

Accepted transfer/catalog authority:

- source manifest SHA256: `259b34c75ed8adbd8132d56e23a41fc02da97338f8510027f7da77ccb52dcd83`
- destination verification SHA256: `eaed44afdfe1d7bf5c6986b87713c6300f3c7c97258018768e1ac77bdc82fa41`
- catalog entry SHA256: `80c9d1309fb8d3f15514c9668ac00a6d8839cb6858aca7e347755eed58d2e434`

Exact raw:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen3-30b-a3b_s2-text_decode_nvbit-warp-mref-shard_s2-dec3-natural-expert21-down_20260917T034400Z_e210c0de5678`

### DeepSeek-V2-Lite

Producer branch/head:

`hrl/c16-deepseek-v2-lite-s2-producer-109-v23r1`

`baf892ced6d66cbacabb995caf095e5280995097`

Exact formal run:

`C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23`

Semantic anchor:

`layer1.mlp.experts.4.down_proj`

Natural top-6 expert IDs:

`[4,24,25,55,60,26]`

Selected route weight:

`0.07594462484121323`

Shared experts: `2`

Replay shape:

- input `[1,1408]` BF16
- weight `[2048,1408]` BF16
- output `[1,2048]` BF16
- bitwise replay PASS

Expected static set:

- 243 direct-GLOBAL MREF shards
- producer summary: 169 executed / 74 `ZERO_EXECUTION_PROVEN`
- active-lane events: `11538432`

Accepted transfer/catalog authority:

- source manifest SHA256: `d98b4a077afe9e7f2ce32479484e9c1148548b1ef1802c9b002dd70250b7b638`
- destination verification SHA256: `aa57f40ca04c3f611d17ca0f7150ef0e9e80664151cec288a24110b4c9b2d9b7`
- catalog entry SHA256: `9ece3f570fbdaa8e026da39bee94c7f15b2c60bf14e292a66f6026104d18d81d`

Exact raw:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23`

## Important comparability boundary

These are intentionally matched at the **semantic operator family** level:

`natural-routed expert down_proj under S2/T2048 decode`

They are **not** fully matched execution states:

- Q30 anchor is Decode step 3 at Layer24
- DeepSeek anchor is the V23R1 selected S2 decode state at Layer1
- routing topology differs (Q30 top-8/128 experts; DeepSeek top-6/64 routed experts + 2 shared experts)
- expert intermediate width differs (`768` vs `1408`)

Therefore do not claim causal differences due to vendor/model architecture from one pair. The purpose is a scoped two-lineage MoE-family comparison.

## Goal

Independently determine which memory-behavior properties of a natural-routed expert `down_proj` are common across these two MoE lineages, which differ, and which differences are explainable by exact operator dimensions/runtime implementation rather than by unsupported cache/TLB speculation.

## 1. Immutable authority audit

For both exact run IDs only:

- verify catalog entry and expected hash
- verify source/destination manifest/verification hashes
- verify positive admission/ACK
- verify raw root identity
- do not enumerate alternative runs
- verify accepted raw/catalog are not modified

Also fetch/read producer semantic receipts from the exact producer heads above. Do not rely on a branch name without checking exact head.

## 2. Independent C16WARP1 decode

Decode all 243 Q30 shards and all 243 DeepSeek shards independently from node164 raw.

Use the validated C16WARP1 layout where applicable:

- header `'<8sIIQQQ'`
- WRec `'<6I32Q'`

For every shard recompute:

- static index
- executed / `ZERO_EXECUTION_PROVEN`
- record count
- active-lane events
- overflow/drop/terminal integrity
- unique CTA coordinates
- CTA min/max
- warp IDs
- 4K / 64K / 2M pages
- 128B lines
- address min/max

Do not trust producer totals until independently reproduced.

## 3. Same-process typed object joins

Use only each shard/replay's own `ADDRESS_CONTEXT`.

For both models, normalize semantic membership into:

- `EXPERT_DOWN_WEIGHT`
- `EXPERT_DOWN_INPUT`
- `EXPERT_DOWN_OUTPUT`
- `OTHER_OR_UNCLASSIFIED`

Preserve the producer's original labels in a separate column; normalization is for comparison only.

For every active address count membership and fraction. Require no cross-process VA join.

Do not require every static MREF to touch the expert weight; activation/output paths are valid distinct classes.

## 4. Full-scope / occurrence audit

For each model independently verify:

- exact semantic replay identity
- expected function/kernel signature from producer evidence
- no inherited CTA slicing
- no wrong occurrence
- drop/overflow/terminal closure
- executed/zero partition consistency

Q30 isolated semantic replay is the formal harness authority for Expert21. Do not reinterpret it as full-layer chronology.

## 5. Normalized operator comparison

Build one authoritative comparison table with at least:

- model/revision
- layer/expert ID
- decode-step/state scope
- routing topology and selected expert
- down_proj input width
- down_proj output width
- weight shape/bytes where proven
- exact kernel/function family
- grid/block
- static GLOBAL-MREF count
- executed/zero partition
- total active-lane events
- per-executed-shard event distribution
- per-shard 4K/64K/2M page distributions
- per-shard 128B-line distributions
- weight/input/output membership fractions
- full-scope result
- typed NCU status

Useful derived quantities are allowed only if clearly defined, e.g. active-lane events per MiB of proven weight storage. Do not use them as causal metrics.

Primary comparison must remain per-shard distributions + exact semantic dimensions.

## 6. Static-set / implementation relation

Determine whether the two down_proj anchors use:

- exact same function/code object
- same function family but different template/shape
- different function implementations

If static indices or code objects differ, do not compare static-index numbers directly.

If both happen to have 243 static MREFs, treat equal count as descriptive evidence only; do not infer identical static sets without a valid code-object/function comparison.

## 7. Routing interpretation

Compare routing facts only at the level supported by one frozen canonical state:

- Q30: top-8/128, selected expert21
- DeepSeek: top-6/64 routed + 2 shared, selected expert4

Do not infer population-level load balance, expert popularity, or routing entropy from one token/state.

## 8. NCU evidence

Audit existing bounded NCU evidence only.

If native metrics, units, collection conditions, and target identity are not directly comparable, mark `NOT_COMPARABLE` or `SCOPED`.

Never infer bytes from ambiguous units and do not claim cache/TLB causality.

## 9. Scientific interpretation

Answer explicitly:

1. Which properties are common to both natural-routed `down_proj` anchors?
2. Which differences track operator dimensions (`768→2048` vs `1408→2048`) or routing/runtime structure?
3. Which memory footprint differences remain descriptive only?
4. Does the evidence support a **two-lineage MoE-family memory-behavior pattern**, without promoting it to a general cross-model universal?
5. What third independent MoE lineage or scenario dimension would provide the highest information gain if broader MoE commonality is later needed?

Global C16 rule applies:

- broad cross-model "common" requires >=3 independent lineages
- family-level evidence may use >=2 within the family

So the strongest PASS wording should remain two-lineage/family-scoped.

## 10. Final decision

Preferred PASS-side decision if both raw authorities independently close:

`C16_Q30_DEEPSEEK_TWO_LINEAGE_MOE_FAMILY_COMPARISON_174NEW_V25_PASS`

Also emit one typed next-step recommendation, choosing based on evidence rather than coverage density, for example:

- preserve current two-lineage MoE anchor set and wait for a third MoE lineage;
- add a matched routing/batch dimension if routing diversity is the dominant unresolved axis;
- add a matched decode-step only if the Q30 Decode3 vs DeepSeek decode-state mismatch materially limits conclusions.

Do not automatically request new captures.

## Required review pack

Create:

`docs/vm_tlb/review_packs/C16_Q30_DEEPSEEK_TWO_LINEAGE_MOE_174NEW_V25/`

Include at minimum:

- `AUTHORITY_AUDIT.json`
- `Q30_SHARD_FINGERPRINTS.tsv`
- `DEEPSEEK_SHARD_FINGERPRINTS.tsv`
- `Q30_OBJECT_JOIN.tsv`
- `DEEPSEEK_OBJECT_JOIN.tsv`
- `Q30_SCOPE_AUDIT.json`
- `DEEPSEEK_SCOPE_AUDIT.json`
- `SEMANTIC_OPERATOR_COMPARISON.tsv`
- `STATIC_IMPLEMENTATION_RELATION.json`
- `ROUTING_SCOPE_COMPARISON.json`
- `NCU_TYPED_COMPARISON.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_AUTHORIZATION.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

## Evidence boundaries

Never construct:

- cross-process absolute-VA comparison
- cross-replay VA union
- cross-shard temporal chronology
- cross-shard reuse distance
- cache/TLB causality from event/page/line counts
- population routing conclusions from one canonical state

## Git closure

Suggested implementation branch:

`hrl/c16-cross-model-moe-q30-deepseek-174new-v25`

Use existing 174-new `gh auth` + HTTPS setup.

After completion:

- commit only Goal-owned V25 changes
- push actual HEAD
- verify canonical repo `swayhrl/accel-sim-framework`
- require `LOCAL_HEAD == git ls-remote SHA == authenticated gh api SHA`
- if stdout capture is empty, persist decisive SHA values to `/tmp` and read them
- clean worktree
- STOP

Fail closed only on a real evidence blocker; routine stdout/cwd/Git friction is not a scientific blocker.
