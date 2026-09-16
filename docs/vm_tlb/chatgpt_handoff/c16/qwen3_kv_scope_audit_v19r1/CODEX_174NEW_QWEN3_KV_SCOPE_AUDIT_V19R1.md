# C16 Qwen3 KV formal scope audit — 174-new V19R1

## Execution mode

Execute this task in **GOAL MODE**. This is a bounded CPU-only audit of existing accepted evidence. Do not run GPU work and do not mutate accepted raw/catalog.

Use local Git and the local node164 mount only. Do **not** use SSH for Git or node164 data access. If Codex command stdout is unexpectedly empty, redirect stdout/stderr to local files and read those files; empty captured stdout alone is not evidence of absence.

## Exact authority

V18R2 accepted formal run ID:

`C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v18r2-k-repeat_20260916T040000Z_ee18ee18ee18`

Catalog entry:

`/root/share/mnt164/huangrulin/c16_ai_workload/catalog/entries/C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v18r2-k-repeat_20260916T040000Z_ee18ee18ee18.json`

Raw directory:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v18r2-k-repeat_20260916T040000Z_ee18ee18ee18`

Expected source manifest SHA256:

`3a189ae86864e723a7fc0b8fd739db8c3fe3befa33800ee2c444e799f0ad75b8`

Expected catalog SHA256:

`a043d78b0069f1acd24d5fdc2fc75ccac32b1e1aa3fa1da55a137e26f24b19ad`

Producer signature for the intended repeat-K direct-copy launch:

- grid `(16392,1,1)`
- block `(128,1,1)`
- target `layer0.self_attn.repeat_kv(K)`
- evidence class `KV_STORAGE_DIRECT_READ`

V19 consumer HEAD to preserve as prior evidence:

`925ab0507abb50ebbe4b177d98d9bf3809d1bcd7`

## Why this audit is required

V19 independently recomputed 160 static MREF shards, 8 executed, 152 zero, and 2048 total active-lane events. Before using this as an S2 baseline for S3 context scaling, determine whether the accepted traces cover the intended full repeat-K launch or only a CTA slice / different occurrence.

The V18R2 producer capture script selected `C16_WARP_FUNCTION_OCCURRENCE=0` and inherited the parent environment via `os.environ.copy()`. It did not explicitly bind formal capture to the NVTX range and did not explicitly clear `C16_CTA_BEGIN` / `C16_CTA_END`. Therefore do not assume whole-launch scope from the manifest label alone.

## Goal

Independently determine the actual dynamic scope and object binding of the accepted V18R2 formal traces using the raw traces already on node164.

### 1. Verify immutable authority

Verify catalog SHA, RUN_MANIFEST SHA, run ID, WARP_SHARD_MANIFEST readability and raw path. Record actual hashes, not only expected strings.

### 2. Decode all nonzero C16WARP1 shards

For every shard classified `EXECUTED_SHARD`, independently decode the C16WARP1 header and every WRec. Record at least:

- static index
- function occurrence from header/context
- record count
- active-lane event count
- unique `(cta_x,cta_y,cta_z)` count
- `cta_x` min/max and sorted unique values when reasonably small
- warp IDs observed
- unique active addresses
- address min/max
- 4K/64K/2M pages and 128B lines
- overflow
- terminal consistency

Also summarize the **union of CTA coordinates across all 8 executed shards**.

### 3. Perform a real same-process range join

Read each shard's `ADDRESS_CONTEXT.json` and use its exact runtime ranges. For every active lane address, classify membership against:

- `KV_POST_UPDATE_K`
- `KV_DERIVED_REPEAT_K`
- neither

Produce per-shard and aggregate counts/fractions. Do not label a shard Class-A merely because the context file contains a K range; the dynamic addresses must actually fall inside the source K range.

### 4. Diagnose capture scope

Use evidence, not launch-order assumptions.

Distinguish at least these outcomes:

- `FULL_SCOPE_VALIDATED`: dynamic records and range join are consistent with the intended repeat-K launch, with no evidence of CTA slicing or wrong occurrence.
- `SCOPED_CAPTURE_ONLY`: traces are demonstrably limited to a CTA subset (for example a very small contiguous CTA set) and therefore event totals / ZERO_EXECUTION_PROVEN cannot be promoted to whole-kernel claims.
- `WRONG_OCCURRENCE`: dynamic addresses do not bind to post-update K storage or other evidence shows occurrence 0 was not the intended repeat-K launch.
- `BLOCKED_INSUFFICIENT_EVIDENCE`: existing raw cannot distinguish the above without GPU recapture.

Do **not** decide solely from the fact that 8 records is smaller than the theoretical launch warp count; a static instruction may be predicated. Use CTA-coordinate coverage and actual K-range membership.

### 5. Reassess V19 claims

State exactly which V19 quantities remain valid under the diagnosed scope:

- 160 static MREF set
- 8 executed / 152 zero
- 2048 active-lane events
- page/line distributions
- `KV_STORAGE_DIRECT_READ`

If scope is partial, rename the dynamic quantities explicitly as slice-local rather than whole-kernel.

### 6. Produce next-step authorization

If and only if `FULL_SCOPE_VALIDATED`, authorize the exact same semantic target for S3 long-context producer work.

If `SCOPED_CAPTURE_ONLY` or `WRONG_OCCURRENCE`, do not authorize S3 yet. Provide one bounded S2 recapture correction that makes the target unambiguous, preferably a dedicated repeat-K replay where the target direct-copy launch is uniquely identified and `C16_CTA_BEGIN/END` are explicitly unset, followed by full-CTA formal capture.

## Required review pack

Create:

`docs/vm_tlb/review_packs/C16_QWEN3_KV_SCOPE_AUDIT_174NEW_V19R1/`

At minimum include:

- `AUTHORITY_AUDIT.json`
- `NONZERO_SHARD_CTA_SCOPE.tsv`
- `KV_RANGE_JOIN.tsv`
- `AGGREGATE_SCOPE_SUMMARY.json`
- `V19_CLAIM_REASSESSMENT.tsv`
- `NEXT_STEP_AUTHORIZATION.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preserve exact evidence boundaries: no cross-process absolute VA comparison, no cross-shard chronology, no reuse-distance invention.

## Completion

Commit and push to an implementation branch such as:

`hrl/c16-qwen3-kv-scope-audit-174new-v19r1`

Verify remote HEAD equals local HEAD before reporting completion. Then STOP.
