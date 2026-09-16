# CODEX GOAL MODE — C16 Qwen3 S2 Attention/KV Independent Consumer V19 (174-new)

## Mandatory execution mode

Execute this task in **GOAL MODE**. Do not merely read, summarize, plan, or review. Carry the complete CPU-side workflow through review-pack creation, hash closure, commit, push, and final report unless a genuine fail-closed blocker occurs.

Use local Git and the local node164 mount only. **Do not use SSH** for Git coordination or node164 data access.

## Mission

Independently consume and validate the accepted Qwen3-8B S2 Attention/KV-adjacent formal target produced by node109 V18R2, then establish its replay-local memory fingerprint and compare it against the already accepted Qwen3 S2 first-decode MLP anchor. Decide, from actual evidence, whether the next producer target should be the same KV materialization path under S3 long context.

CPU-only. Do not run GPU/model execution. Do not mutate accepted raw/catalog.

Producer evidence commit to audit:

`5d29ad8babe47226cbd25180a6db133e9526b6cf`

Producer review pack:

`docs/vm_tlb/review_packs/C16_QWEN3_S2_ATTENTION_KV_109_V18R2/`

Formal V18R2 run identity:

`C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v18r2-k-repeat_20260916T040000Z_ee18ee18ee18`

Exact node164 paths:

- catalog entry:
  `/root/share/mnt164/huangrulin/c16_ai_workload/catalog/entries/C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v18r2-k-repeat_20260916T040000Z_ee18ee18ee18.json`
- raw:
  `/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v18r2-k-repeat_20260916T040000Z_ee18ee18ee18`

Producer identities to verify, not blindly trust:

- source manifest SHA256: `3a189ae86864e723a7fc0b8fd739db8c3fe3befa33800ee2c444e799f0ad75b8`
- catalog entry SHA256: `a043d78b0069f1acd24d5fdc2fc75ccac32b1e1aa3fa1da55a137e26f24b19ad`
- file count: `483`
- producer claim: `160` direct-GLOBAL MREF shards, zero overflow, all terminal closed, same-process ADDRESS_CONTEXT for every shard
- producer claim: `152` ZERO_EXECUTION_PROVEN, therefore `8` EXECUTED_SHARD

Prior Qwen3 S2 MLP comparison authority:

- V15 producer evidence: `ac4420f81dfafbe03b96e1bda63b4af31fe77f6a`
- V17 independent consumer: `2405be223c4d55c0101f9700ea9b3ab1b19dd64f`
- MLP formal run:
  `C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v14-layer0-downproj_20260916T020000Z_dd14dd14dd14`

## P0 — Source/tool preflight

Before analysis:

1. verify the coordination commit/handoff locally with Git;
2. `stat` the exact V18R2 catalog and raw paths above;
3. record command exit codes and stderr for failed accesses;
4. empty stdout alone is not evidence of absence;
5. do not enumerate/search catalog to rediscover the already-known run.

If exact paths are unreadable, emit a typed source-access BLOCKED result with command evidence.

## P1 — Independent formal integrity audit

Independently parse node164 accepted raw/catalog. Do not copy producer counts into the result.

Verify:

- catalog entry identity and SHA;
- accepted run manifest identity and SHA;
- model/revision/scenario/phase/target descriptor;
- fresh static MREF map identity;
- exact address-bearing path classes;
- direct GLOBAL set size;
- LDGSTS GLOBAL_SOURCE set size;
- EXECUTED vs ZERO_EXECUTION_PROVEN partition;
- expected/present/terminal-closed shard counts;
- every C16WARP1 shard header/record-size consistency;
- per-shard fingerprint;
- drop/overflow totals;
- same-process ADDRESS_CONTEXT existence and binding;
- local-close/verification/admission/ACK receipts;
- catalog/raw destination identity;
- no evidence of duplicate/concurrent formal admission.

Required outputs:

- `V18R2_FORMAL_INDEPENDENT_AUDIT.json`
- `V18R2_STATIC_EXEC_ZERO.tsv`
- `V18R2_SHARD_FINGERPRINTS.tsv`
- `V18R2_PIPELINE_RECEIPT_AUDIT.json`

Fail closed if accepted raw is not self-consistent.

## P2 — Validate typed KV dataflow evidence

Audit the hash-closed producer evidence for:

`PREEXISTING_KV_STORAGE -> POST_UPDATE_KV_STORAGE -> KV_DERIVED_REPEAT_BUFFER -> ATTENTION_CORE_OPERAND`

Require evidence that the accepted formal target is only:

`KV_STORAGE_DIRECT_READ = layer0.self_attn.repeat_kv(K)`

and that:

- post-update K is `[1,8,2049,128]` BF16;
- repeated K is `[1,32,2049,128]` BF16;
- source/destination storage do not alias;
- repeat output is exact/bitwise qualified;
- QK/AV derived-buffer evidence is not mislabeled as direct KV-storage read.

Produce:

- `V18R2_KV_DATAFLOW_AUDIT.json`
- `V18R2_SEMANTIC_SCOPE.md`

Do not promote QK/AV to formal status merely from producer prose.

## P3 — Recompute replay-local memory fingerprint

Using the validated C16WARP1 decoder, independently compute for every executed V18R2 shard:

- records;
- active-lane dynamic memory events;
- unique VA count within that shard/process;
- 4K/64K/2M page footprint;
- 128B line footprint;
- static-PC-level distributions;
- load/store classification if provable from the static map;
- direct attribution to K storage only when ADDRESS_CONTEXT proves it.

Do not construct:

- cross-shard global chronology;
- reuse distance across shards;
- cross-process absolute-VA comparisons;
- a false global VA/page union if independent shards cannot be losslessly unioned.

Produce:

- `V18R2_MEMORY_FINGERPRINT.json`
- `V18R2_STATIC_PC_DYNAMIC_SUMMARY.tsv`
- `V18R2_OBJECT_ATTRIBUTION.tsv`

## P4 — Within-Qwen3 orthogonal-path comparison

Compare, with typed evidence status, the two accepted S2 first-decode paths:

1. MLP anchor: `layer0.mlp.down_proj`
2. KV materialization anchor: `layer0.self_attn.repeat_kv(K)`

This is a within-model semantic-path comparison, not a causal experiment.

Compare where provable:

- semantic role;
- kernel implementation family/signature;
- static direct-GLOBAL set size;
- LDGSTS/special-path presence;
- executed/zero partition;
- active-lane events;
- per-executed-shard event distribution;
- per-shard page/line footprint distributions;
- object-attribution strength (`UNKNOWN_RUNTIME` vs direct K-storage binding);
- NCU only if durable values and explicit comparable units exist.

Do not compare absolute VAs between independent captures.

Produce:

- `QWEN3_S2_MLP_VS_KV_REPEAT_COMPARISON.tsv`
- `QWEN3_S2_PATH_INTERPRETATION.md`

Every metric row must state `PROVEN`, `PENDING`, or `NOT_COMPARABLE`.

## P5 — Decide S3 readiness

Do not execute GPU work.

Decide whether S3 should reuse the **same semantic target** `layer0.self_attn.repeat_kv(K)` under the validated S3 V2 input to measure long-context scaling.

The recommendation must be evidence-derived and explicitly distinguish:

- what S2 proves;
- what S3 would test;
- what cannot be inferred before S3 runs.

A justified S3 plan should preserve:

- exact Qwen3 revision/BF16/eager backend;
- same semantic layer/operation;
- exact validated S3 V2 payload;
- fresh S3 replay/signature/static audit;
- no transfer of S2 static-set identity without proof;
- serial formal admission.

Produce:

`NEXT_QWEN3_S3_TARGET_RECOMMENDATION.json`

Do not authorize unrelated S3 targets merely to fill coverage.

## P6 — Final closure

Create:

`docs/vm_tlb/review_packs/C16_QWEN3_ATTENTION_KV_CONSUMER_174NEW_V19/`

Include at least:

- `FINAL_DECISION.json`
- formal independent audit outputs;
- KV dataflow audit;
- memory fingerprint outputs;
- S2 MLP-vs-KV comparison;
- S3 recommendation;
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Allowed decisions:

- `C16_QWEN3_ATTENTION_KV_CONSUMER_174NEW_V19_PASS`
- `..._PASS_WITH_TYPED_GAPS`
- `..._BLOCKED_FORMAL_INTEGRITY`
- `..._BLOCKED_SOURCE_ACCESS`

Do not hide NCU/object-attribution limitations in prose.

Suggested implementation branch:

`hrl/c16-qwen3-attention-kv-consumer-174new-v19`

Commit/push the result and verify remote HEAD equals local HEAD before reporting completion.
