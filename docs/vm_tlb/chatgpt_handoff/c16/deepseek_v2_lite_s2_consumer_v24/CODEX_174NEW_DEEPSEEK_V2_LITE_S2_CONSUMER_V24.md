# C16 DeepSeek-V2-Lite S2 MLA+MoE independent consumer — 174-new V24

## Execution mode

Execute this task in **GOAL MODE**.

This is a CPU-only independent consumer/closure Goal for the accepted node109 V23R1 producer results. Do not run GPU work and do not mutate accepted raw/catalog.

Use:

- local repo: `/root/workspace/accel-sim-framework`
- node164 mount: `/root/share/mnt164`
- existing `gh auth` + HTTPS Git credential integration
- no SSH fallback
- if Codex stdout/stderr capture is unexpectedly empty, redirect decisive output to `/tmp/...` files and read those files; empty captured stdout is not evidence of absence.

Canonical repository:

`https://github.com/swayhrl/accel-sim-framework.git`

## Exact producer authority

Producer branch:

`hrl/c16-deepseek-v2-lite-s2-producer-109-v23r1`

Producer HEAD:

`baf892ced6d66cbacabb995caf095e5280995097`

Producer decision:

`C16_DEEPSEEK_V2_LITE_S2_PRODUCER_109_V23R1_PASS_WITH_MLA_AND_MOE_ANCHORS`

Producer review pack:

`docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_S2_PRODUCER_109_V23R1/`

### Exact accepted MLA run

Run ID:

`C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-mla-kvb_20260917T022000Z_a23a23a23a23`

Raw:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-mla-kvb_20260917T022000Z_a23a23a23a23`

Expected source-manifest SHA256:

`d658def0bd626aa9ca5662853695e26faaba503edab7360b63d244385c97e9b4`

Expected catalog-entry SHA256:

`66d9740d432115e8877edcc81abbaedb2055f548c25bc841fa3b81d06dc28b85`

Producer target:

`layer0.self_attn.kv_b_proj`

Producer evidence class:

`KV_B_EXPANSION_LATENT_READ`

Producer-reported static/direct-GLOBAL count:

`31`

Producer-reported partition/events:

`11 executed / 20 zero / 271360 active-lane events`

Important scope boundary: this is **not** a persistent-KV-cache direct-read claim.

### Exact accepted MoE run

Run ID:

`C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23`

Raw:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23`

Expected source-manifest SHA256:

`d98b4a077afe9e7f2ce32479484e9c1148548b1ef1802c9b002dd70250b7b638`

Expected catalog-entry SHA256:

`9ece3f570fbdaa8e026da39bee94c7f15b2c60bf14e292a66f6026104d18d81d`

Producer target:

`layer1.mlp.experts.4.down_proj`

Natural routing authority:

- first MoE layer: `1`
- natural top-k expert IDs: `[4,24,25,55,60,26]`
- selected expert: `4`
- selected expert route weight: `0.07594462484121323`
- shared experts: `2`

Producer-reported static/direct-GLOBAL count:

`243`

Producer-reported partition/events:

`169 executed / 74 zero / 11538432 active-lane events`

## Goal

Independently determine whether the two V23R1 accepted S2 anchors are valid, evidence-bounded semantic anchors and whether they are sufficient to authorize the next DeepSeek step.

Do not merely summarize producer JSON. Consume accepted node164 raw and recompute core evidence.

---

# 1. Authority / admission audit

For both exact run IDs:

- read the exact catalog entry;
- verify expected catalog SHA where possible;
- verify source manifest SHA;
- verify raw manifest and shard manifest readability;
- verify verification/admission/ACK are positive;
- confirm MLA admission/ACK preceded MoE admission/ACK;
- verify accepted raw/catalog are treated read-only.

Do not enumerate/search alternative DeepSeek runs.

Also verify producer HEAD/review-pack `SHA256SUMS` and final decision.

---

# 2. Independent static/path typing

For each target independently audit producer static evidence and raw metadata:

## MLA

Confirm:

- semantic operator is exactly `layer0.self_attn.kv_b_proj`;
- 31 direct-GLOBAL address-bearing static MREFs unless exact evidence proves otherwise;
- LDGSTS/GLOBAL_TO_SHARED and other address-bearing paths are typed explicitly;
- source-vs-weight-vs-output roles are not collapsed into one generic MREF class.

The producer formal summary indicates some executed loads join `MLA_KV_A_LATENT_NORM` and some join `MLA_KV_B_WEIGHT`. Preserve this distinction.

Do **not** upgrade the whole `kv_b_proj` formal run into a pure latent-read claim simply because the evidence class is `KV_B_EXPANSION_LATENT_READ`; report exact per-shard object composition.

## MoE

Confirm:

- target is exactly natural-routed `layer1.mlp.experts.4.down_proj`;
- 243 direct-GLOBAL MREFs unless exact evidence proves otherwise;
- source activation and expert-weight reads are distinguished;
- any output stores are typed separately;
- no grouped/fused ambiguity contradicts expert-4-specific attribution.

---

# 3. Decode every formal shard

Use the validated C16WARP1 parser contract already used in accepted consumers.

For all MLA and MoE shards independently recompute:

- static index;
- classification;
- record count;
- active-lane events;
- overflow;
- terminal consistency;
- unique CTA coordinates;
- CTA min/max;
- warp IDs;
- per-shard 4K/64K/2M pages;
- per-shard 128B lines;
- active-address min/max.

Recompute the executed/zero partition and total active-lane-event count from raw, not producer summaries.

Do not create cross-shard chronology or reuse distance.

---

# 4. Same-process semantic object joins

Use only each shard's own `ADDRESS_CONTEXT` / same-process runtime ranges.

## MLA

Classify every active address, where ranges exist, against exact typed objects such as:

- `MLA_KV_A_LATENT_NORM` / equivalent exact latent source range;
- `MLA_KV_B_WEIGHT`;
- `MLA_KV_B_OUTPUT` or exact output range if present;
- neither/unknown.

Required conclusion must be object-composition aware.

The safe producer claim to test is:

`kv_b_proj performs expansion from the exact latent representation and its formal memory stream contains losslessly attributable latent/weight/output behavior as supported by same-process ranges.`

Do not call this persistent-cache direct read.

## MoE

Classify active addresses against:

- expert-4 down-proj weight storage;
- exact routed expert down-proj input activation;
- exact output storage if present;
- neither/unknown.

Require expert-specific attribution to be supported by same-process ranges and the frozen natural-routing receipt.

Do not compare absolute VA across replays/processes.

---

# 5. Full-scope / occurrence audit

For both targets independently determine whether the accepted traces cover the intended selected launch without hidden CTA slicing or wrong occurrence.

Use:

- CTA coordinate coverage;
- target grid/block from signature evidence;
- occurrence/function identity;
- object-membership consistency;
- drop/overflow/terminal state.

Do not infer full scope from label alone.

If full scope cannot be established, classify the gap precisely instead of repeating the producer PASS.

---

# 6. Natural MoE routing audit

Independently verify the producer routing receipt from frozen state/provenance:

- layer 1 is the first actual MoE layer under the exact runtime/config;
- top-k IDs are `[4,24,25,55,60,26]` for the exact frozen state;
- expert 4 is genuinely naturally selected;
- recorded route weight for expert 4 is `0.07594462484121323` under the same receipt;
- no forced routing was used to create the expert-4 semantic replay.

If rerunning routing on CPU is not bitwise-equivalent due backend/runtime constraints, do not synthesize evidence; instead verify the frozen routing receipt/hash chain and state authority.

---

# 7. Producer NCU evidence audit

Audit the preserved bounded NCU reports/logs for MLA and MoE.

Only report numeric values when explicit values, units, and collection conditions are comparable.

Preserve any uncontrolled-cache warnings.

Never infer bytes from ambiguous units or claim cache/TLB causality.

---

# 8. Independent S2 scientific interpretation

Produce a concise comparison of the two DeepSeek S2 anchors:

- MLA `kv_b_proj` is an MLA-specific latent expansion path, not yet a persistent-cache-read anchor;
- MoE expert-4 `down_proj` is a natural-routing routed-expert memory anchor if expert-specific attribution closes;
- compare event counts and per-shard spatial-footprint distributions descriptively;
- do not cross-union addresses;
- do not treat either target as an unbiased whole-model estimator.

Explicitly separate:

1. what V23R1 proves;
2. what it does not prove;
3. which next experiment has the highest information gain.

---

# 9. CPU-only persistent-MLA-cache qualification plan

The producer recommendation is:

`BOUNDED_DEEPSEEK_MLA_PERSISTENT_CACHE_READ_QUALIFICATION_BEFORE_S3`

Before authorizing new GPU work, use the exact canonical DeepSeek revision and exact modeling source available on node164 / producer evidence to reconstruct the runtime cache semantics at source/API level.

Determine, without GPU execution:

- what tensor/object is appended to or persisted across decode for MLA;
- whether compressed latent, RoPE component, reconstructed K/V, or another representation is the actual persistent cache storage;
- the exact cache update API/data structure;
- which downstream semantic operator directly consumes the persisted representation;
- which candidate operator could support a same-process direct-read object join;
- whether one isolated replay can preserve the exact semantic source and avoid launch-order inference.

Produce a bounded target plan for node109, not a speculative formal target.

Classify one of:

- `PERSISTENT_MLA_CACHE_DIRECT_READ_TARGET_IDENTIFIED_CPU_SIDE_PENDING_GPU_QUALIFICATION`
- `PERSISTENT_MLA_CACHE_IS_MULTI_OBJECT_OR_DERIVED_TARGET_REQUIRES_GPU_TYPED_DATAFLOW`
- `NO_CLEAN_PERSISTENT_DIRECT_READ_TARGET_VISIBLE_IN_CURRENT_RUNTIME`
- `BLOCKED_INSUFFICIENT_SOURCE_AUTHORITY`

Do not invent a direct-read target merely to enable S3.

---

# 10. Next-step decision

PASS-side final decision for the independent consumer should be scoped, e.g.:

`C16_DEEPSEEK_V2_LITE_S2_CONSUMER_174NEW_V24_PASS`

and must include a typed next-step authorization.

If both accepted anchors independently close and the persistent-cache source-level plan is viable, prefer:

`AUTHORIZE_BOUNDED_DEEPSEEK_MLA_PERSISTENT_CACHE_GPU_QUALIFICATION`

Do not authorize DeepSeek S3 yet unless the persistent-cache question is resolved or you explicitly justify why S3 on the existing `kv_b_proj` anchor has independent scientific value.

Do not recommend more operators merely for coverage density.

---

# Required review pack

Create:

`docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_S2_CONSUMER_174NEW_V24/`

Include at minimum:

- `AUTHORITY_AUDIT.json`
- `MLA_STATIC_PATH_AUDIT.json`
- `MLA_SHARD_FINGERPRINTS.tsv`
- `MLA_OBJECT_JOIN.tsv`
- `MLA_FULL_SCOPE_AUDIT.json`
- `MOE_STATIC_PATH_AUDIT.json`
- `MOE_SHARD_FINGERPRINTS.tsv`
- `MOE_OBJECT_JOIN.tsv`
- `MOE_FULL_SCOPE_AUDIT.json`
- `MOE_ROUTING_AUDIT.json`
- `NCU_EVIDENCE_AUDIT.json`
- `S2_MLA_VS_MOE_INTERPRETATION.md`
- `MLA_PERSISTENT_CACHE_SOURCE_AUDIT.md`
- `MLA_PERSISTENT_CACHE_NEXT_TARGET.json`
- `NEXT_STEP_AUTHORIZATION.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preserve strict evidence boundaries:

- no cross-process absolute VA comparison;
- no cross-replay VA union;
- no cross-shard chronology;
- no reconstructed reuse distance;
- no cache/TLB causality from event counts.

---

# Git closure

Suggested implementation branch:

`hrl/c16-deepseek-v2-lite-s2-consumer-174new-v24`

Use existing 174-new GitHub CLI + HTTPS credentials.

After scientific closure:

1. commit only V24 Goal-owned changes;
2. push actual `HEAD:refs/heads/hrl/c16-deepseek-v2-lite-s2-consumer-174new-v24`;
3. verify repository identity `swayhrl/accel-sim-framework`;
4. verify nonempty `git ls-remote` SHA;
5. verify the same ref via authenticated `gh api`;
6. require `LOCAL == LS_REMOTE_SHA == GH_API_SHA`;
7. working tree clean.

Do not ask the user to do routine Git closure.

## Stop

On a real evidence blocker, preserve valid evidence, hash-close a typed partial review pack, commit/push/verify and STOP.

Otherwise complete the entire Goal and STOP only after final transport verification.
