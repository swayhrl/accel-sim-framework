# C16 V2 First Formal Ingest Guidance

Ownership: ChatGPT
Status: coordination for the first successful MREF-sharded formal trace

## Current producer evidence

Node109 has demonstrated a `MREF_SHARDED_COMPLETE_SET` capture for the first Qwen2.5-0.5B S2_TEXT attention target:

- frozen static GLOBAL-MREF set size: 29;
- each static-MREF shard terminal-closes under deterministic replay;
- 13 static MREFs execute and produce address records;
- the remaining static MREFs are explicitly observed as zero-execution under the same exact launch replay;
- reported overflow is zero;
- current producer quickcheck reports 258,048 exact lane addresses, 1,008 unique 4 KiB pages, and 30,464 unique 128 B lines;
- the local Pipeline V1 bundle has been finalized and promoted to `ready/`; transport/admission/ACK is in progress.

These producer quickcheck counts are provisional until the destination independently verifies the raw bundle and node174-new reproduces them from the admitted evidence.

## Immediate rule for node109

Do not reopen or mutate the already local-closed bundle merely to fit a downstream parser shape.

Complete the existing Pipeline V1 transfer/verify/admit/ACK flow first. If transport/SSH stalls, recover transport only; do not rerun GPU capture and do not rewrite the local manifest.

A scientifically valid raw capture must not be downgraded because the first analysis implementation assumed a different packaging layout.

## Important compatibility gap discovered

The accepted node174-new V2 parser currently assumes one cataloged Pipeline `RUN_ID` per shard. It loads every `child_shards[].run_id` from `catalog/entries/<RUN_ID>.json`.

The first node109 implementation is instead naturally packaged as one immutable Pipeline run containing many hash-inventoried binary shard artifacts plus a parent logical-target manifest.

The parser also historically rejects empty address streams, while a complete MREF-sharded target can legitimately include static MREFs that were selected, replayed, terminal-closed, and proven to execute zero times.

Neither difference invalidates the producer evidence. Analysis must support the evidence actually captured without inventing events or changing raw data.

## Accepted packaging forms for `MREF_SHARDED_COMPLETE_SET`

V2 analysis shall support both:

1. `MULTI_RUN_SHARDS`: one Pipeline RUN_ID per shard; and
2. `SINGLE_CONTAINER_RUN`: one Pipeline RUN_ID whose manifest hashes every shard artifact and whose logical-target control metadata binds each shard artifact to its exact selector and replay identity.

Both forms require the same scientific identity:

- model revision / asset authority;
- frozen input binding;
- scenario and phase;
- exact target function and code object;
- exact launch selector / replay rule;
- static-MREF-set SHA;
- per-shard selected static MREF indices;
- terminal status;
- overflow/drop counters;
- artifact size/SHA closure.

The analysis packaging form is not a scientific variable.

## Zero-execution shards

A selected static MREF may contribute zero address events and still satisfy complete-set coverage only when there is positive zero-execution proof.

Required zero-execution proof:

- exact target/replay identity matches the logical target;
- selected static MREF index is explicitly recorded;
- capture reaches terminal `COMPLETE`;
- callback/event count is exactly zero;
- overflow/drop count is zero;
- the corresponding log/control artifact is hash-closed by the admitted raw manifest.

Classify such a shard as `ZERO_EXECUTION_PROVEN`, not `MISSING` and not `EMPTY_PARSE_FAILURE`.

A shard with absent output, timeout, missing terminal marker, corruption, overflow, or identity mismatch is not zero-execution proof and must fail closed.

## Aggregate semantics

For `MREF_SHARDED_COMPLETE_SET` the logical aggregate may support:

- static MREF coverage and executed-vs-zero-executed membership;
- exact-address set union;
- unique 4 KiB / 64 KiB page sets and counts;
- unique 128 B line sets and counts;
- per-MREF footprint distributions;
- object attribution and access/width composition where represented;
- launch-local set/cardinality comparisons.

It must not claim:

- cross-shard callback order;
- cross-shard/global reuse distance;
- global hardware memory order;
- a trace-order-derived shared-cache MRC across independently replayed MREF shards.

## First formal evidence acceptance

The first Qwen0 attention logical target becomes accepted formal evidence only after all of the following pass:

1. Pipeline V1 destination rehash and ACK for the immutable raw container/run(s);
2. exact static-MREF-set coverage: declared shard selectors plus `ZERO_EXECUTION_PROVEN` members equal the frozen 29-MREF set;
3. no overlapping duplicate MREF selectors unless explicitly identical audit copies are excluded from the formal union;
4. all executing shards terminal-close with zero overflow/drop;
5. the binary record layout/version is hash-bound and the 174-new decoder reproduces producer quickcheck counts from admitted raw;
6. object-map authority is bound to the same model process/replay contract or unknowns remain `UNKNOWN_RUNTIME`;
7. derived outputs and logical-target receipt are hash-closed;
8. unsupported temporal claims remain mechanically prohibited.

Do not require a rerun merely because the first producer package is a single container rather than 29 separate Pipeline runs.
