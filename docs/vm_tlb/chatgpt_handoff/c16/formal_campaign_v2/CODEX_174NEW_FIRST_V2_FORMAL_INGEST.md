# CODEX 174-new — First V2 Formal Ingest

Ownership: ChatGPT
Execution node: 174-new / node164
Status: execute after node109 publishes the final first V2 formal run/format evidence

## Goal

Consume the first admitted node109 `MREF_SHARDED_COMPLETE_SET` formal Qwen2.5-0.5B S2_TEXT attention evidence, adapt the analysis layer to the exact producer packaging/format without mutating raw data, reproduce the producer quickcheck independently, and publish a hash-closed logical-target analysis receipt.

This is a goal-mode task. Resolve parser/packaging incompatibilities rather than declaring the already captured raw evidence invalid when its scientific identity is sound.

## Required bases

Read and preserve:

- accepted analysis prep: `d07b7eb5d43b9a31474a6d298ec4e4f75292cc48`;
- accepted sharded analysis: `9efecc6c17c542a41b7b1913a62e5a10c0b4f745`;
- Pipeline V1 integration: `3c4847d2da818013dca6422194af36966136ab31`;
- `FIRST_FORMAL_INGEST_GUIDANCE_V1.md`;
- node109 final V2 producer/review pack and binary format specification commit.

Use a fresh branch/worktree. Suggested branch:

`hrl/c16-first-v2-formal-ingest-174new-v1`

## Step A — raw admission check

Do not analyze an unadmitted partial transfer.

Require:

- catalog entry exists;
- raw manifest SHA matches catalog;
- Pipeline verification/ACK is PASS;
- admitted raw directory is immutable for this task;
- all producer artifacts are present and independently hash-verified.

If the transfer is incomplete, wait/retry receiver-side transport/admission only. Do not request a GPU rerun.

## Step B — packaging reconciliation

Inspect the admitted producer manifest and logical-target metadata.

Support both packaging forms:

- existing `MULTI_RUN_SHARDS` implementation; and
- `SINGLE_CONTAINER_RUN`, where many shard artifacts are members of one Pipeline run.

For the single-container form, each logical child descriptor must bind at least:

- container RUN_ID;
- artifact relative path;
- artifact SHA256;
- static MREF selector/index;
- exact target/replay identity;
- terminal/overflow evidence relative path and SHA;
- record format/version;
- zero-execution status when applicable.

Do not split/copy raw files into pretend child runs merely to satisfy the old parser. Add a container-aware analysis adapter instead.

## Step C — binary decoder

Node109 is expected to freeze a versioned binary record layout and/or a reference decoder/quickcheck.

Implement the decoder in the 174-new analysis code only from the producer's committed format specification.

Requirements:

- explicit format/version dispatch;
- record-size/endianness validation;
- fail closed on truncation, unknown version, malformed selector, invalid address record, or trailing garbage unless the format explicitly allows it;
- bind decoder version/spec SHA into derived receipts;
- no OCR/guessing/reverse engineering from byte patterns when the format spec is incomplete.

If the producer bundle contains a reference decoder, independently implement or at minimum independently validate its output against the frozen spec; do not simply trust producer summary counts.

## Step D — zero-execution shard support

Extend MREF complete-set analysis to distinguish:

- `EXECUTED_SHARD`;
- `ZERO_EXECUTION_PROVEN`;
- `MISSING_OR_INVALID_SHARD`.

`ZERO_EXECUTION_PROVEN` requires exact replay identity, explicit selected static index, terminal complete, exactly zero callback/address records, zero overflow/drop, and hash-closed evidence.

Zero-execution shards count toward frozen static-MREF-set coverage but contribute no address/page/line events.

An empty file without positive terminal evidence must fail closed.

## Step E — complete-set verification

For the first attention logical target, verify that the union of:

- executed shard selectors; and
- zero-execution-proven selectors

exactly equals the frozen selected GLOBAL-MREF set from the RTX4080 static map.

Reject:

- missing selected MREFs;
- overlapping selectors;
- unbound extra MREFs;
- code-object mismatch;
- target-function mismatch;
- launch-selector/replay mismatch;
- static-MREF-set SHA mismatch;
- overflow/drop in a shard admitted as complete.

## Step F — independent reproduction

Recompute from admitted raw, not producer TSV summaries:

- exact lane/address event count;
- unique exact VA count;
- unique 4 KiB pages;
- unique 64 KiB pages;
- unique 128 B lines;
- read/write/atomic and width composition where encoded;
- executed static MREF list;
- zero-execution-proven static MREF list;
- per-MREF footprint table;
- object attribution including `UNKNOWN_RUNTIME`.

Compare with producer quickcheck. Any mismatch must be investigated to root cause. Do not silently prefer either side.

## Step G — logical-target outputs

Write under the canonical derived namespace:

- per-shard parsed/fingerprint outputs;
- `MREF_COVERAGE.tsv`;
- `PER_MREF_FINGERPRINT.tsv`;
- aggregate set-union fingerprint;
- object attribution summary;
- `LOGICAL_TARGET_RECEIPT.json`;
- deterministic discovery indexes.

The receipt must bind:

- source Pipeline RUN_ID/raw-manifest SHA;
- logical-target manifest SHA;
- binary-format-spec SHA/version;
- parser commit/argv;
- all output hashes;
- evidence class `MREF_SHARDED_COMPLETE_SET`;
- merge semantics `SET_UNION_AND_DISTRIBUTION_ONLY`;
- unsupported claims.

## Claim boundary

Mechanically prohibit aggregate claims about:

- cross-shard order;
- cross-shard reuse distance;
- global hardware order;
- replay-spanning temporal reuse/MRC.

Supported set/cardinality/per-MREF/object analyses are formal when the acceptance gates pass.

## Regression

Existing RTX3090 Q2 Prefill and Decode exact regressions must remain PASS.

Add tests for:

1. single-container MREF packaging PASS;
2. multi-run packaging still PASS;
3. zero-execution-proven shard PASS;
4. empty-without-terminal FAIL;
5. binary truncation FAIL;
6. unknown format/version FAIL;
7. missing MREF FAIL;
8. duplicate/overlap MREF FAIL;
9. wrong code object FAIL;
10. producer-vs-destination quickcheck mismatch FAIL/report;
11. deterministic aggregate output PASS.

## Deliverables

Review pack suggested:

`docs/vm_tlb/review_packs/C16_FIRST_V2_FORMAL_INGEST_174NEW_V1/`

Include at minimum:

- README.md
- FINAL_DECISION.json
- SOURCE_RUN.tsv
- BINARY_FORMAT_BINDING.json
- MREF_COVERAGE.tsv
- PRODUCER_DESTINATION_CROSSCHECK.tsv
- PER_MREF_FINGERPRINT.tsv
- AGGREGATE_FINGERPRINT.json
- OBJECT_ATTRIBUTION_SUMMARY.tsv
- REGRESSION_RESULTS.tsv
- TEST_MATRIX.tsv
- OPEN_ISSUES.md
- SHA256SUMS

## PASS decision

`FIRST_V2_FORMAL_INGEST_PASS` requires:

- Pipeline source closure PASS;
- exact frozen MREF-set coverage PASS;
- zero-execution shards proven rather than inferred;
- destination decoder PASS;
- producer/destination event and footprint crosscheck PASS, or any producer-summary bug is explicitly corrected from admitted raw;
- no overflow/drop for accepted complete shards;
- logical outputs hash-closed;
- old Q2 regression unchanged;
- no raw mutation;
- unsupported temporal claims prohibited.

## STOP

STOP only after the first V2 formal logical target is either accepted with a complete hash-closed derived receipt or rejected for a concrete source-evidence defect that cannot be repaired analysis-side.

Do not ask for a GPU rerun solely because of parser packaging assumptions.
