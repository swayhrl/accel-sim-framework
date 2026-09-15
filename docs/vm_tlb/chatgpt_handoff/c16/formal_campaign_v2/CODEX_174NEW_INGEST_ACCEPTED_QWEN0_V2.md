# CODEX 174-new — Ingest Accepted Qwen0 V2 Formal Runs

Execution node: 174-new / port 2239
Mode: GOAL

## Inputs

Read first:

- `FIRST_FORMAL_INGEST_GUIDANCE_V1.md`
- `PRODUCER_V2_FINAL_REVIEW.md`

Use accepted analysis implementation base:

`9efecc6c17c542a41b7b1913a62e5a10c0b4f745`

Consume producer authority:

`fd2cb24a73d5bb0d5bfadde19438db9ebc2552df`

Canonical root:

`/root/share/mnt164/huangrulin/c16_ai_workload`

## Goal

Independently verify, decode, analyze and close the first two admitted Qwen0 V2 formal logical targets without any GPU rerun or raw mutation.

Accepted runs are exactly those listed in `PRODUCER_V2_FINAL_REVIEW.md`.

## Required implementation

### 1. Add frozen C16WARP1 decoder

Implement downstream decoding for the hash-bound producer format rather than shelling out to the producer decoder as the sole source of truth.

Validate at minimum:

- magic/version identifier;
- header size and record size;
- static MREF in header matches the artifact/shard declaration;
- function-local occurrence matches target identity;
- file length equals header plus declared record count times 280 bytes;
- `records_written`, callback/warp record counts and terminal side evidence are consistent;
- active-mask lane handling is exact;
- no address is synthesized for inactive lanes;
- malformed/truncated/trailing binary bytes fail closed.

Record decoder source SHA and parser commit.

### 2. Support SINGLE_CONTAINER_RUN MREF complete sets

Both accepted logical targets are one Pipeline RUN containing many MREF shard artifacts.

Do not split or rewrite raw into fake child Pipeline RUNs.

Treat each `mref_<static>.bin` plus its bound terminal/status evidence as a logical child shard inside the single cataloged run.

The Pipeline raw manifest SHA remains the container authority.

### 3. Distinguish executed and zero-execution shards

For every static MREF in the frozen set, independently classify:

- `EXECUTED_SHARD`, or
- `ZERO_EXECUTION_PROVEN`, or
- `MISSING_OR_INVALID_SHARD`.

`ZERO_EXECUTION_PROVEN` requires all of:

- static MREF belongs to frozen selected set;
- exact model/input/scenario/function/code-object/occurrence identity;
- terminal complete;
- zero callback/records;
- zero overflow/drop;
- shard/status evidence hash-bound inside the admitted bundle.

A zero-length/no-record artifact without this evidence must fail closed.

### 4. Exact completeness checks

Q05_ATTN:

- expected static MREF count = 29;
- static set SHA = `9f82df6f77893a4f9c5e3c8d1d1ee44a63c1421d5676cef7dab21f562eff7857`.

Q05_GEMM:

- expected static MREF count = 141;
- static set SHA = `5a3958e94b8161b4ec67a406baf60641e8284664cdb9a6cb930ed4ed4fe93264`.

The analyzed union must exactly cover the frozen static set, including zero-execution-proven members. Missing/extra/duplicate MREFs fail closed.

### 5. Independent producer-vs-consumer cross-check

Recompute from node164 admitted raw and compare against producer committed summary.

Expected producer-final classification summary:

- Q05_ATTN: 12 executed, 17 zero-execution-proven, 10,752 warp records, overflow total 0.
- Q05_GEMM: 16 executed, 125 zero-execution-proven, 38,912 warp records, overflow total 0.

Do not silently force these values. If raw recomputation differs, report the discrepancy and diagnose it. The raw/manifests decide acceptance.

Also independently derive and report:

- active lane/address event count;
- unique exact VA;
- unique 4KiB pages;
- unique 64KiB pages;
- unique 2MiB pages;
- unique 128B lines;
- per-MREF footprint distribution;
- load/store and access-width distribution from exact static map where available;
- object attribution to `WEIGHT`, `QUANT_METADATA`, `KV_CACHE`, `ACTIVATION` only when evidenced, otherwise `UNKNOWN_RUNTIME`.

### 6. Preserve scope boundary

The aggregate output must mechanically state:

- `aggregate_order_label=CROSS_SHARD_ORDER_PROHIBITED`;
- `cross_shard_reuse_distance=UNSUPPORTED`;
- `global_hardware_order=UNSUPPORTED`.

Do not concatenate MREF shards into a pseudo temporal stream.

Per-shard callback order may be reported only as per-shard observed order.

## Required outputs

Review pack:

`docs/vm_tlb/review_packs/C16_FIRST_V2_FORMAL_INGEST_174NEW_V1/`

At minimum:

- `FINAL_DECISION.json`
- `RUN_VERIFICATION.tsv`
- `BINARY_DECODER_QUALIFICATION.tsv`
- `MREF_COMPLETENESS.tsv`
- `PRODUCER_CONSUMER_CROSSCHECK.tsv`
- `LOGICAL_TARGET_FINGERPRINT.tsv`
- `OBJECT_ATTRIBUTION.tsv`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Persist derived outputs under node164 `parsed/`, `features/`, or the existing accepted derived namespace, with receipts binding:

- source RUN_ID;
- source raw manifest SHA;
- producer commit;
- parser commit;
- decoder format/spec SHA;
- parser argv/config;
- output hashes.

## Acceptance

PASS requires both logical targets to independently satisfy:

- exact catalog/raw manifest binding;
- C16WARP1 decoder validation;
- frozen static MREF set exact completeness;
- every MREF classified as executed or zero-execution-proven;
- zero overflow/drop for accepted shards;
- producer/consumer summary consistent or any discrepancy fully root-caused;
- aggregate/page/cache-line/object outputs hash-closed;
- unsupported ordering claims mechanically absent;
- legacy RTX3090 Q2 regression remains PASS;
- raw evidence unchanged.

Decision labels:

- `FIRST_V2_FORMAL_INGEST_PASS`
- `FIRST_V2_FORMAL_INGEST_PARTIAL_WITH_ROOT_CAUSE`
- `FIRST_V2_FORMAL_INGEST_FAIL`

Do not ask for or trigger a GPU rerun to repair an analysis-side incompatibility.

## STOP

Commit/push the review pack and implementation, leave a clean worktree, then STOP.
