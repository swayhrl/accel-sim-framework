# C16 Qwen3 S2→S3 KV context-scaling independent consumer — 174-new V21

## Execution mode

Execute this task in **GOAL MODE**.

This is one autonomous **CPU-only independent consumer/closure Goal**. Do not run GPU work and do not mutate accepted raw/catalog. Do not merely summarize the node109 producer review pack; independently consume the accepted node164 raw and recompute the core evidence.

Use the established 174-new workflow:

- local Git repository: `/root/workspace/accel-sim-framework`
- node164 durable mount: `/root/share/mnt164`
- existing `gh auth` + HTTPS Git credential integration
- do **not** switch to SSH or generate SSH keys
- known Codex stdout-capture issue: if stdout/stderr is unexpectedly empty, redirect decisive output to local `/tmp/...` files and read them; empty captured stdout alone is not evidence of missing data.

Canonical repository identity:

`https://github.com/swayhrl/accel-sim-framework.git`

## Producer authority

Node109 V20 producer branch:

`hrl/c16-qwen3-s3-kv-scaling-109-v20`

Producer HEAD:

`c94825dab9b114e468a83cdad009181f23add608`

Producer decision:

`C16_QWEN3_S3_KV_SCALING_109_V20_PASS`

Producer review pack:

`docs/vm_tlb/review_packs/C16_QWEN3_S3_KV_SCALING_109_V20/`

Exact semantic target on both sides:

`layer0.self_attn.repeat_kv(K)`

Evidence class:

`KV_STORAGE_DIRECT_READ`

Do not promote this to a claim that QK/AV directly read original KV-cache storage. QK/AV remain derived-buffer reads only.

## Exact accepted formal authorities

### S2 fresh full-scope baseline

Run ID:

`C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v20-s2-repeat-k_20260916T162000Z_202020202020`

Catalog entry:

`/root/share/mnt164/huangrulin/c16_ai_workload/catalog/entries/C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v20-s2-repeat-k_20260916T162000Z_202020202020.json`

Raw directory:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v20-s2-repeat-k_20260916T162000Z_202020202020`

Expected catalog SHA256:

`aabeb406523d55355432b3367c6089b43a8c7b4821b97a100717a1b37480a2c8`

Expected source manifest SHA256:

`f52fcdf0e281407f106f4f478fa1072a4ec299dde30df7c32abb089e8b7c6116`

Producer-reported key values to audit, not blindly trust:

- K-post shape `[1,8,2049,128]`
- repeat-K shape `[1,32,2049,128]`
- grid_x `16392`
- static direct-GLOBAL MREF count `8`
- executed `8`, zero `0`
- active-lane events `16785408`
- full-scope CTA union `0..16391`, 16392 unique CTAs
- overflow `0`

### S3 fresh full-scope baseline

Run ID:

`C16R_qwen3-8b_s3-text_decode_nvbit-warp-mref-shard_v20-s3-repeat-k_20260916T163000Z_303030303030`

Catalog entry:

`/root/share/mnt164/huangrulin/c16_ai_workload/catalog/entries/C16R_qwen3-8b_s3-text_decode_nvbit-warp-mref-shard_v20-s3-repeat-k_20260916T163000Z_303030303030.json`

Raw directory:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen3-8b_s3-text_decode_nvbit-warp-mref-shard_v20-s3-repeat-k_20260916T163000Z_303030303030`

Expected catalog SHA256:

`b85430200f520506bc2abf3165af018b628c11626d47b7c77e00eb2b03c79082`

Expected source manifest SHA256:

`d986397b7b32dafd7efe3cfcbfaae71dd367d4c8ce0587aa8ea8e35a0acb339b`

Producer-reported key values to audit, not blindly trust:

- K-post shape `[1,8,8193,128]`
- repeat-K shape `[1,32,8193,128]`
- grid_x `65544`
- static direct-GLOBAL MREF count `8`
- executed `8`, zero `0`
- active-lane events `67117056`
- full-scope CTA union `0..65543`, 65544 unique CTAs
- overflow `0`

## Methodological authority / tracer correction

V20 deliberately replaced the ambiguous V18R2 baseline with fresh isolated full-scope captures.

The actual direct-copy SASS has 8 address-bearing direct-GLOBAL MREF instructions and no LDGSTS path. V20 discovered that the old generic MREF-address callback produced address zero for four source LDG instructions. The accepted V20 capture therefore uses:

- **LDG source-address capture from the known address register pair** for source-read indices:
  - static 237: `R4:R5`
  - static 475: `R4:R5`
  - static 713: `R4:R5`
  - static 950: `R2:R3`
- normal MREF destination-address capture for the four STG destination instructions.

The rejected pre-fix diagnostic root was not admitted/cataloged.

V21 must independently audit that the accepted raw is consistent with this typed split. Do not treat the producer's recovery statement as sufficient by itself.

## Goal

Independently establish whether V20 really proves full-scope S2→S3 context scaling for the same Qwen3 `repeat_kv(K)` KV-storage materialization path, and decide whether Qwen3 can be closed for the current C16 lineage sampling plan.

### 1. Immutable authority audit

For both exact run IDs:

- read the exact catalog entry;
- recompute/verify catalog entry SHA where possible;
- read raw `RUN_MANIFEST.json` / `WARP_SHARD_MANIFEST.json`;
- verify expected source manifest SHA;
- verify verification/admission/ACK receipts are positive;
- confirm S2 was admitted/ACKed before S3 admission began;
- verify accepted raw/catalog are read-only from this consumer.

Do not enumerate/search alternative Qwen3 runs.

### 2. Static/path audit

From producer Git evidence and accepted raw metadata, independently verify the frozen semantic/static set:

- exact function identity;
- 8 direct-GLOBAL MREF indices;
- 0 LDGSTS/GLOBAL_TO_SHARED;
- no other address-bearing special path claimed;
- source-read indices vs destination-store indices are explicitly typed.

Record the source-read static indices and destination-store static indices.

### 3. Independently decode all S2 and S3 C16WARP1 shards

Use the validated layout:

- header `'<8sIIQQQ'`
- WRec `'<6I32Q'`

For every shard on both sides independently recompute:

- static index
- classification
- record count
- active-lane events
- overflow
- terminal consistency
- unique CTA coordinates
- `cta_x` min/max
- warp IDs
- per-shard 4K pages
- per-shard 64K pages
- per-shard 2M pages
- per-shard 128B lines
- address min/max

Require all eight shards to be executed for the fresh V20 baseline unless raw proves otherwise.

### 4. Same-process object/range join

For each shard, use **only that replay's own `ADDRESS_CONTEXT`**.

For every active lane address count membership in:

- `KV_POST_UPDATE_K`
- `KV_DERIVED_REPEAT_K`
- neither

Required semantic expectation:

- the four LDG source-read shards must losslessly read `KV_POST_UPDATE_K`;
- the four STG destination shards must losslessly write/address `KV_DERIVED_REPEAT_K`;
- neither count should be zero for the semantically corresponding class;
- no active address should require cross-process joining.

If this typed split does not hold, fail closed rather than repeating the producer claim.

### 5. Full-scope gate

For each scenario independently verify:

- every executed shard CTA range begins at 0;
- every executed shard reaches the expected upper CTA extent;
- union unique CTA count matches expected `grid_x`;
- no evidence of inherited `C16_CTA_BEGIN/END` slicing;
- no evidence of wrong function occurrence;
- drop/overflow/terminal conditions pass.

Expected full-scope extents:

- S2: CTA x `0..16391`, unique CTAs `16392`
- S3: CTA x `0..65543`, unique CTAs `65544`

### 6. Recompute context-scaling comparison

Only after both full-scope gates pass, compare S2 vs S3 using the same methodology.

Recompute at least:

- static MREF set identity/count;
- executed/zero partition;
- total active-lane events;
- event-count ratio;
- kernel grid ratio;
- per-executed-shard event distribution;
- per-shard 4K/64K/2M page-count distributions;
- per-shard 128B-line-count distributions;
- source K-post object-membership fractions;
- destination repeat-K object-membership fractions;
- K-post/repeat-K shape and storage-byte scaling from producer state receipts.

**Important aggregation rule:**

Do not form a cross-shard address union. If reporting an aggregate page/line quantity, label it explicitly as `SUM_OF_PER_SHARD_UNIQUES` unless same-replay union semantics are separately proven. The safest primary comparison is per-shard distributions plus event totals.

Expected producer ratio to independently test:

`S3 / S2 = 3.998535871156662`

for both `grid_x` and total active-lane events.

Do not round this into an exact 4× claim without noting the `2049 -> 8193` endpoint effect.

### 7. NCU evidence audit

Read the typed NCU evidence and preserved reports/logs, but do not force a numeric cross-scenario cache-effect conclusion.

If native values/units and collection conditions are explicitly comparable, report them as typed measurements. Preserve warnings about uncontrolled GPU caches. Otherwise mark the metric comparison `NOT_COMPARABLE` or `SCOPED`.

Never infer byte counts from ambiguous display units.

### 8. Scientific interpretation

Produce a concise evidence-bounded interpretation answering:

1. Is `repeat_kv(K)` a distinct memory-behavior anchor from the earlier MLP `down_proj` path? Use prior accepted evidence only where directly comparable.
2. Does context expansion from S2 T2048 to S3 T8192 cause approximately proportional launch/event scaling for this exact materialization path?
3. Which properties remain invariant (semantic target, static set, per-CTA execution structure) and which scale (K/repeat storage, grid extent, total memory events, per-shard spatial footprint)?
4. What is **not** proven: cache/TLB causality, reuse distance, global chronology, all-attention behavior, or direct QK/AV KV-storage reads.

### 9. Qwen3 lineage closure decision

The final review pack must contain a typed next-step decision.

Preferred PASS-side decision if all evidence closes:

`QWEN3_LINEAGE_SUFFICIENTLY_CLOSED_FOR_C16_NEXT_LINEAGE`

Rationale should reflect that Qwen3 now has:

- exact static/model authority;
- canonical prospective inputs;
- S2 matched-semantic MLP anchor;
- S2 direct KV-storage materialization anchor;
- typed KV-storage -> repeat-buffer -> attention-core dataflow;
- fresh full-scope S2 and S3 captures for the same `repeat_kv(K)` target;
- independent S2→S3 scaling validation.

If a meaningful evidence gap remains that would materially change this conclusion, emit a specific typed blocker rather than automatically recommending more Qwen3 captures.

Do **not** recommend another Qwen3 operator merely for coverage density.

If Qwen3 is closed, recommend moving the producer mainline to **DeepSeek-V2-Lite**, preserving its actual MLA + MoE structure rather than simplifying it to ordinary MHA/dense MLP.

## Required review pack

Create:

`docs/vm_tlb/review_packs/C16_QWEN3_S3_KV_CONSUMER_174NEW_V21/`

Include at minimum:

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

Preserve strict evidence boundaries:

- no cross-process absolute-VA comparison;
- no cross-replay VA union;
- no cross-shard chronology;
- no reconstructed reuse distance;
- no cache/TLB causality from scaling alone.

## Git transport closure

Suggested implementation branch:

`hrl/c16-qwen3-s3-kv-consumer-174new-v21`

Use 174-new's existing GitHub CLI + HTTPS credential setup. Do not switch authentication mechanisms.

After scientific closure:

1. commit only Goal-owned V21 changes;
2. push actual `HEAD:refs/heads/hrl/c16-qwen3-s3-kv-consumer-174new-v21`;
3. verify repository identity is `swayhrl/accel-sim-framework`;
4. verify nonempty SHA from `git ls-remote`;
5. independently verify the same branch SHA via authenticated `gh api`;
6. success requires `LOCAL == LS_REMOTE_SHA == GH_API_SHA`;
7. if stdout capture is unreliable, persist decisive values in `/tmp` and verify from files.

Do not ask the user to perform routine Git closure manually.

## Stop conditions

Fail closed only on a real evidence blocker, such as:

- exact accepted raw/catalog hash mismatch;
- shard/parser integrity failure;
- source LDG addresses do not losslessly join K-post;
- destination addresses do not join repeat-K;
- full CTA coverage fails;
- drop/overflow/terminal closure fails;
- S2/S3 semantic/static target is not actually matched;
- committed review pack cannot be hash-closed.

On a blocker, preserve all valid CPU-side evidence, create a typed partial review pack, commit/push with strict transport verification, and STOP.

Otherwise complete the entire Goal and STOP only after final remote verification.
