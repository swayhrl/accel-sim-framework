# C16 Qwen3 S2→S3 KV final consumer closure correction — 174-new V21R1

## Execution mode

Execute this task in **GOAL MODE**.

This is a CPU-only correction/closure Goal for the already-running V21 line. Do not run GPU work and do not mutate accepted raw/catalog.

The previous V21 attempt is **not sufficient as final Qwen3 closure** because it only reported a single-S3 audit and a stale next-target recommendation (`REUSE_EXACT_REPEAT_K_K_SEMANTIC_TARGET_UNDER_S3`) even though V20 already completed and admitted S3. Preserve any valid V21 local artifacts, but complete the actual intended S2+S3 closure below.

Use the established 174-new workflow:

- local Git: `/root/workspace/accel-sim-framework`
- node164 mount: `/root/share/mnt164`
- existing `gh auth` + HTTPS credential integration
- do not switch to SSH
- known stdout-capture issue: if stdout/stderr is unexpectedly empty, redirect decisive output to `/tmp/...` files and read those files; empty captured stdout alone is not evidence of missing data.

Canonical repo:

`https://github.com/swayhrl/accel-sim-framework.git`

## Exact producer authority

V20 producer HEAD:

`c94825dab9b114e468a83cdad009181f23add608`

Decision:

`C16_QWEN3_S3_KV_SCALING_109_V20_PASS`

Semantic target on both sides:

`layer0.self_attn.repeat_kv(K)`

Evidence class:

`KV_STORAGE_DIRECT_READ`

### Exact S2 formal authority

Run ID:

`C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v20-s2-repeat-k_20260916T162000Z_202020202020`

Raw:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v20-s2-repeat-k_20260916T162000Z_202020202020`

Catalog:

`/root/share/mnt164/huangrulin/c16_ai_workload/catalog/entries/C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v20-s2-repeat-k_20260916T162000Z_202020202020.json`

Expected catalog SHA256:

`aabeb406523d55355432b3367c6089b43a8c7b4821b97a100717a1b37480a2c8`

Expected source manifest SHA256:

`f52fcdf0e281407f106f4f478fa1072a4ec299dde30df7c32abb089e8b7c6116`

Expected producer values to independently audit:

- 8 static direct-GLOBAL MREF
- executed 8 / zero 0
- grid_x 16392
- CTA x 0..16391
- active-lane events 16785408
- overflow 0

### Exact S3 formal authority

Run ID:

`C16R_qwen3-8b_s3-text_decode_nvbit-warp-mref-shard_v20-s3-repeat-k_20260916T163000Z_303030303030`

Raw:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen3-8b_s3-text_decode_nvbit-warp-mref-shard_v20-s3-repeat-k_20260916T163000Z_303030303030`

Catalog:

`/root/share/mnt164/huangrulin/c16_ai_workload/catalog/entries/C16R_qwen3-8b_s3-text_decode_nvbit-warp-mref-shard_v20-s3-repeat-k_20260916T163000Z_303030303030.json`

Expected catalog SHA256:

`b85430200f520506bc2abf3165af018b628c11626d47b7c77e00eb2b03c79082`

Expected source manifest SHA256:

`d986397b7b32dafd7efe3cfcbfaae71dd367d4c8ce0587aa8ea8e35a0acb339b`

Expected producer values to independently audit:

- 8 static direct-GLOBAL MREF
- executed 8 / zero 0
- grid_x 65544
- CTA x 0..65543
- active-lane events 67117056
- overflow 0

## Typed tracer correction that must be independently checked

The accepted V20 capture uses:

Source LDG static indices:

- 237: source address from register pair `R4:R5`
- 475: source address from `R4:R5`
- 713: source address from `R4:R5`
- 950: source address from `R2:R3`

Destination STG indices use normal MREF destination address path:

- 241
- 479
- 717
- 953

Expected object split:

- source LDG dynamic addresses losslessly join that replay's `KV_POST_UPDATE_K`
- destination STG dynamic addresses losslessly join that replay's `KV_DERIVED_REPEAT_K`

Do not trust the producer claim without checking the accepted raw.

## Goal

Complete the actual final Qwen3 independent closure. Reuse any valid previous V21 local work, but do not stop until all required S2+S3 stages below are complete.

### 1. Authority audit

For both exact runs:

- verify exact catalog entry SHA
- verify exact source manifest SHA
- verify WARP_SHARD_MANIFEST readability
- verify verification/admission/ACK are positive
- verify S2 admission/ACK precedes S3 admission/ACK

Do not enumerate or substitute alternative Qwen3 runs.

### 2. Decode all 16 shards independently

Use C16WARP1:

- header `'<8sIIQQQ'`
- WRec `'<6I32Q'`

For every S2 and S3 shard recompute:

- static index
- record count
- classification
- active-lane events
- overflow
- terminal consistency
- unique CTA coordinates
- cta_x min/max
- warp IDs
- per-shard 4K / 64K / 2M pages
- per-shard 128B lines
- address min/max

Require fresh V20 baseline to show 8 executed / 0 zero on both sides unless raw disproves it.

### 3. Same-process object join

For each shard use only that replay's own `ADDRESS_CONTEXT`.

Count every active address against:

- `KV_POST_UPDATE_K`
- `KV_DERIVED_REPEAT_K`
- neither

Required typed split on both S2 and S3:

- 237,475,713,950: 100% source events in `KV_POST_UPDATE_K`
- 241,479,717,953: 100% destination events in `KV_DERIVED_REPEAT_K`
- no active address may require cross-process VA joining

Fail closed if this split does not hold.

### 4. Full-scope gate

Independently prove:

S2:
- every executed shard cta_x begins at 0
- reaches 16391
- union unique CTAs = 16392

S3:
- every executed shard cta_x begins at 0
- reaches 65543
- union unique CTAs = 65544

Also require:

- overflow/drop/terminal PASS
- no inherited CTA slicing evidence
- no wrong occurrence evidence

### 5. Recompute S2→S3 scaling

After both full-scope gates pass, recompute:

- static MREF identity/count
- executed/zero
- total active-lane events
- event ratio
- grid ratio
- per-shard event distributions
- per-shard 4K/64K/2M page distributions
- per-shard 128B-line distributions
- source object-membership fractions
- destination object-membership fractions
- K-post/repeat-K shape/storage scaling from producer receipts

Expected ratio to independently test:

`3.998535871156662`

for both total active-lane events and grid_x.

Do not call it exactly 4× without noting the `2049 -> 8193` endpoint effect.

Aggregation rule:

- do not form a cross-shard VA union
- primary reporting should be per-shard distributions + event totals
- if an aggregate page/line count is reported, label it `SUM_OF_PER_SHARD_UNIQUES` unless stronger same-replay semantics are explicitly proven

### 6. NCU audit

Read typed NCU evidence and logs.

Preserve uncontrolled-cache warnings and unit limitations. If values/units/conditions are not explicitly comparable, mark comparison `NOT_COMPARABLE` or `SCOPED`. Never infer bytes from ambiguous units.

### 7. Final scientific interpretation

State whether the evidence supports all of the following:

- `repeat_kv(K)` is a distinct memory-behavior anchor from MLP `down_proj`
- S2 T2048 -> S3 T8192 produces approximately proportional launch/event scaling for this exact materialization path
- semantic/static target and per-CTA execution structure remain invariant
- storage/grid/event/spatial footprint scale with context

Explicitly state what is not proven:

- cache/TLB causality
- reuse distance
- global chronology
- all-attention behavior
- direct QK/AV reads from original KV storage

### 8. Required final lineage decision

If all evidence closes, final typed decision must be:

`QWEN3_LINEAGE_SUFFICIENTLY_CLOSED_FOR_C16_NEXT_LINEAGE`

and the recommended next producer lineage must be:

`DeepSeek-V2-Lite`

with its actual MLA + MoE structure preserved.

Do **not** emit `REUSE_EXACT_REPEAT_K_K_SEMANTIC_TARGET_UNDER_S3`; S3 is already completed and admitted in V20.

Do not recommend another Qwen3 operator merely for coverage density.

If a meaningful evidence gap remains, emit a specific blocker instead.

## Required review pack

Create a new correction pack:

`docs/vm_tlb/review_packs/C16_QWEN3_S3_KV_CONSUMER_174NEW_V21R1/`

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
- `NCU_EVIDENCE_AUDIT.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `QWEN3_LINEAGE_CLOSURE.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preserve the prior V21 pack as attempt history; do not overwrite it.

## Git closure

Suggested implementation branch:

`hrl/c16-qwen3-s3-kv-consumer-174new-v21r1`

Use existing `gh auth` + HTTPS credentials. Do not switch to SSH.

Complete:

- commit only V21R1 Goal-owned changes
- push actual HEAD
- verify canonical repo identity
- verify nonempty `git ls-remote` SHA
- verify same branch SHA via authenticated `gh api`
- success requires `LOCAL == LS_REMOTE_SHA == GH_API_SHA`

If stdout capture is empty, persist outputs to `/tmp` and verify from files.

Do not ask the user to do routine Git closure manually.

## Stop

STOP only after:

- full S2+S3 scientific closure, or a genuine typed evidence blocker
- hash-closed review pack
- commit/push
- canonical remote verification

This is a GOAL MODE execution task, not a plan or partial audit.