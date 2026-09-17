# C16 DeepSeek-V2-Lite S2→S3 mixed-QK independent consumer — 174-new V30

## Execution mode
Execute in GOAL MODE. CPU-only. Do not run GPU. Do not modify accepted raw/catalog.

Use:
- repo `/root/workspace/accel-sim-framework`
- durable storage `/root/share/mnt164`
- existing 174-new HTTPS + gh credential integration

Suggested implementation branch:
`hrl/c16-deepseek-s2-s3-consumer-174new-v30`

## Exact accepted producer authority
S2 accepted V26 branch/HEAD:
- `hrl/c16-deepseek-v2-lite-persistent-mla-109-v26`
- `afa5b3898ba33ad03f507e20b5312ef28f601c11`

Exact S2 run:
`C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v26-qk-mixed_20260917T130000Z_c26c26c26c26`

S3 accepted V27 branch/HEAD:
- `hrl/c16-deepseek-v2-lite-s3-mixed-qk-109-v27`
- `05f431a37b673e70061ad8921165a7630d981224`

Exact S3 run:
`C16R_deepseek-v2-lite_s3-text_decode_nvbit-warp-mref-shard_v27-qk-mixed_20260917T140000Z_d27d27d27d27`

Both evidence classes must remain:
`MIXED_PERSISTENT_CACHE_CONSUMER`

Do not search for substitute runs if either exact run is unavailable. Fail closed on identity mismatch.

---

# Objective
Independently consume both accepted raw objects and determine whether the S2→S3 typed scaling reported by V27 is reproducible from durable node164 evidence.

This is the final independent-consumer gate before declaring the DeepSeek MLA context-scaling lineage closed for C16 stratification.

---

# Stage 0 — authority/catalog/ACK audit
For both exact runs independently verify:
- durable raw path exists
- accepted catalog entry identity
- source/destination manifest identities
- producer ACK identities
- file count / raw object consistency
- review-pack SHA closures

Do not infer success from producer prose alone.

---

# Stage 1 — independent decode
Independently decode every shard from durable raw for both runs.

S2 expected static-shard authority: 20 direct-GLOBAL static MREFs, but recompute rather than trust the number.

S3 expected static-shard authority: 131 direct-GLOBAL static MREFs, but recompute rather than trust the number.

For every shard recompute:
- executed vs `ZERO_EXECUTION_PROVEN`
- records
- active-lane events
- overflow/drop/terminal status
- CTA/full-scope properties where encoded
- per-shard unique 128B lines
- per-shard unique 4K/64K/2M pages
- trace/context hashes

Verify that the four V27 high-volume shards accepted into formal evidence are the fresh zero-overflow recovery captures rather than superseded overflow attempts.

---

# Stage 2 — typed same-process object joins
Using each shard's same-process `ADDRESS_CONTEXT`, independently classify dynamic addresses into at least:
- `QUERY_CURRENT_TOKEN`
- `PERSISTENT_KEY_PREFIX`
- `CURRENT_KEY_APPEND`
- `OTHER_OR_UNCLASSIFIED`

Do not build cross-shard address unions.

For each endpoint compute exact typed event totals from per-shard evidence.

Confirm or refute:
- S2 logical composition = 2048 persistent prefix + 1 current append
- S3 logical composition = 8192 persistent prefix + 1 current append

Do not relabel either endpoint as a clean direct-read target.

---

# Stage 3 — static implementation relation
Independently audit producer static identity metadata and establish whether S2 and S3 use:
- exact same function/static set
- same function different static set
- different function not directly statically comparable

Expected producer result is `DIFFERENT_FUNCTION_NOT_DIRECTLY_COMPARABLE`; verify, do not assume.

If different function, restrict comparison to typed semantic endpoints and do not compare static indices as if they matched.

---

# Stage 4 — independent S2→S3 scaling
Recompute and report:
- context-length ratio
- cache-after logical-length ratio
- total active-lane-event ratio
- persistent-prefix-event ratio
- current-append-event ratio
- query-current-event ratio
- executed/zero partition at each endpoint
- per-shard page/line distribution deltas

For unique footprint summaries use per-shard distributions or explicitly `SUM_OF_PER_SHARD_UNIQUES`; never create cross-shard VA union.

Do not claim exact 4x unless the recomputed value is exactly 4x.

---

# Stage 5 — NCU and scientific scope
Audit bounded NCU only as typed supporting evidence. Preserve `NOT_COMPARABLE` or other typed gaps if units/counters/kernel identities do not permit direct comparison.

Forbidden claims:
- cache/TLB causality
- cross-process absolute VA relation
- cross-replay VA union
- cross-shard chronology
- reuse distance
- whole-model DeepSeek scaling

Allowed claim scope:
- this exact Layer0 mixed-QK semantic consumer under S2 vs S3 canonical endpoints

---

# Stage 6 — lineage closure decision
If durable raw independently reproduces producer semantics and scaling, emit:
`C16_DEEPSEEK_MLA_S2_S3_CONSUMER_174NEW_V30_PASS`

and authorize:
`DEEPSEEK_MLA_LINEAGE_CLOSED_FOR_C16_STRATIFICATION_NO_FURTHER_OPERATOR_CAPTURE`

If not, emit a typed discrepancy and identify the exact evidence boundary; do not request broad new captures by default.

---

# Review pack
Create:
`docs/vm_tlb/review_packs/C16_DEEPSEEK_MLA_S2_S3_CONSUMER_174NEW_V30/`

Include at least:
- `AUTHORITY_AUDIT.json`
- `S2_SHARD_FINGERPRINTS.tsv`
- `S3_SHARD_FINGERPRINTS.tsv`
- `S2_TYPED_OBJECT_JOIN.tsv`
- `S3_TYPED_OBJECT_JOIN.tsv`
- `STATIC_RELATION.json`
- `S2_VS_S3_SCALING_RECOMPUTED.json`
- `NCU_TYPED_AUDIT.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_AUTHORIZATION.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

---

# Git closure
Complete:
`review pack -> SHA256SUMS -> commit -> push -> LOCAL == git ls-remote == authenticated gh api -> clean worktree -> STOP`

If Codex shell stdout is unexpectedly empty, redirect decisive outputs to `/tmp` and read them rather than declaring missing evidence.