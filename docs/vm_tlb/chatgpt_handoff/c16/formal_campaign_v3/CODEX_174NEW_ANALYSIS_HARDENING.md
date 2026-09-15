# CODEX 174-new — V2 Analysis Hardening

Execution node: 174-new
Mode: GOAL MODE
GPU workload: prohibited
Raw mutation: prohibited

## Inputs

Accepted analysis branch/commit:

- `hrl/c16-first-v2-formal-ingest-174new-v1`
- `39c23ed4a2b2fde61b762aac6362c4ede7ab9879`

Accepted producer authority:

- `fd2cb24a73d5bb0d5bfadde19438db9ebc2552df`

Read `FIRST_V2_INGEST_REVIEW.md` before execution.

## Goal

Harden the first V2 analysis semantics before campaign scaling. Do not invalidate the accepted transport/closure evidence. Correct or narrow derived semantics where current evidence does not support them.

## Required work

### 1. Audit static access-kind join

For both Q05_ATTN and Q05_GEMM:

- read the admitted `STATIC_MREF_MAP.tsv` from node164 raw;
- bind every executed static index to its exact static row;
- independently determine whether static metadata proves READ / WRITE / ATOMIC;
- compare that result with the current derived `access_counts`.

If the current all-WRITE result is a parser bug, fix it and create a new derived receipt. Do not rewrite the previous review pack or raw evidence.

If static metadata cannot prove access kind for some row, output `UNKNOWN_ACCESS_KIND` for those events.

Add directed tests with at least one known load and one known store static row.

### 2. Audit width metadata

Determine exactly what byte-width evidence exists in the admitted static maps and producer source.

Classify each executed static MREF as one of:

- `WIDTH_EXACT_<N>B`
- `WIDTH_EXACT_FROM_VALIDATED_STATIC_DECODER`
- `WIDTH_UNKNOWN`

Do not infer a width merely because an opcode string superficially contains a number unless the mapping is validated against known fixtures.

Update line/page fingerprint logic so multi-byte boundary crossing is used only when width is exact. Otherwise provide explicit `START_ADDRESS_BUCKET_ONLY` metrics.

### 3. Audit object-map/address-space validity

Prove whether each admitted formal shard was captured in the same CUDA process/address space as the object map used for attribution.

Use committed runtime/capture commands, manifests, receipts and process/run evidence. Do not assume.

Output:

- `SAME_ADDRESS_SPACE_PROVEN`
- `SEPARATE_REPLAY_ADDRESS_SPACE`
- or `UNRESOLVED_ADDRESS_SPACE_IDENTITY`

for the accepted targets/shards.

If separate/unresolved, retain all unmatched addresses as `UNKNOWN_RUNTIME` and prohibit cross-process absolute-VA object attribution.

### 4. Reclassify cross-shard unions

For each logical target distinguish:

- per-shard exact address/page/line footprint;
- replay-union absolute address/page/line counts;
- normalized object-relative union if and only if proven possible.

Do not label replay-union absolute VA/page/line counts as a physical whole-launch footprint without shared-address-space proof.

### 5. Preserve regressions

Must remain PASS:

- RTX3090 Q2 Prefill exact regression;
- RTX3090 Q2 Decode exact regression;
- C16WARP1 decoder integrity;
- 170 static MREF executed/zero classifications;
- accepted RUN_MANIFEST and artifact SHA closure;
- raw immutability.

## Required outputs

Create a new review pack, suggested:

`docs/vm_tlb/review_packs/C16_V2_ANALYSIS_HARDENING_174NEW_V1/`

At minimum:

- `FINAL_DECISION.json`
- `ACCESS_KIND_AUDIT.tsv`
- `WIDTH_AUDIT.tsv`
- `ADDRESS_SPACE_AUDIT.tsv`
- `PER_SHARD_FINGERPRINT.tsv`
- `AGGREGATE_SEMANTICS.tsv`
- `OBJECT_ATTRIBUTION_AUDIT.tsv`
- `REGRESSION_RESULTS.tsv`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

## Acceptance

PASS when:

- no unsupported READ/WRITE/width/object claim remains;
- cross-shard absolute-VA semantics are explicitly safe or explicitly diagnostic;
- exact prior closure results remain reproducible;
- all derived outputs are hash-bound to raw manifests + parser commit/config.

Do not wait for node109 Decode data. Finish this CPU-only hardening independently and STOP after commit/push.
