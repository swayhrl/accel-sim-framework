# CODEX 174-new — V2 Sharded Trace Analysis Goal

Execution node: 174-new / 164
Base analysis authority: `d07b7eb5d43b9a31474a6d298ec4e4f75292cc48`
Runs in parallel with node109 V2 recovery/capture.

## Goal

Extend the qualified C16 analysis pipeline so it can ingest and analyze the V2 formal evidence classes without inventing unsupported order semantics.

## Source branch

Start from the accepted analysis-prep branch/commit, not from the node109 campaign code branch.

Suggested execution branch:

```text
hrl/c16-analysis-sharded-v2-174new
```

Read the V2 recovery coordination documents from `hrl/c16-formal-campaign-recovery-v2`.

## Required support

### 1. CTA-sharded all-MREF

For a logical target composed of multiple shard RUN_IDs:

- verify every child raw manifest/hash;
- verify same model/input/scenario/target function/code-object/static-MREF-set identity;
- verify disjoint/declared CTA selectors;
- parse each shard independently;
- produce per-shard fingerprints;
- produce aggregate set unions and distributions.

Allowed aggregate outputs:

```text
union unique 4K/64K pages
union unique 128B lines
per-CTA footprint distribution
object attribution by shard and aggregate
load/store/atomic composition
static-MREF coverage
spatial CTA diversity
```

Do not concatenate shards and call the result a global execution order.

### 2. MREF-sharded complete-set

Verify:

- MREF groups are disjoint;
- union equals the frozen selected static MREF set;
- exact target identity matches across replays.

Allowed aggregate outputs:

```text
union page/line footprint
per-MREF footprint
object mix
access-type/width composition
static-MREF coverage
```

Prohibit cross-group reuse distance/order claims.

### 3. Binary compact record decoder

If node109 emits a new compact binary format:

- implement parser from the format spec/version recorded in the run;
- round-trip directed tests using generated records;
- validate active mask/address reconstruction;
- validate absolute/delta address modes losslessly;
- fail closed on truncation/version mismatch/drop counters.

Do not infer fields not present in the record.

## Logical target manifests

Create a derived logical-target index binding:

```text
logical_target_id
formal_evidence_class
child RUN_ID list
source manifest SHAs
merge semantics
supported analyses
unsupported claims
analysis parser commit
output hashes
```

## Incremental policy

As soon as an ACKed V2 shard arrives, parse it. Do not wait for the entire campaign to finish.

A logical target may be marked `PARTIAL_SHARDS_PRESENT` until its parent manifest says the expected shard set is complete.

## Regression

The existing RTX3090 Q2 Prefill/Decode exact regression must remain PASS after parser changes.

Add synthetic tests for:

```text
CTA shard union
CTA overlap rejection when forbidden
MREF disjoint-union completeness
missing shard
wrong code object
wrong static MREF set SHA
cross-shard order prohibition
binary record truncation
binary delta reconstruction
```

## Outputs

Suggested review pack:

```text
docs/vm_tlb/review_packs/C16_ANALYSIS_SHARDED_V2_174NEW/
```

Include:

```text
README.md
FINAL_DECISION.json
PARSER_TEST_MATRIX.tsv
LOGICAL_TARGET_INDEX.tsv
SHARD_PARSE_INDEX.tsv
MERGE_SEMANTICS.md
REGRESSION_RESULTS.tsv
OPEN_ISSUES.md
SHA256SUMS
```

## Acceptance

PASS when:

- legacy Q2 regression remains exact;
- CTA-sharded merge semantics are implemented/tested;
- MREF-sharded merge semantics are implemented/tested;
- compact binary parser is implemented if a format spec exists, otherwise leave an explicit ready hook;
- unsupported order/reuse claims are mechanically prevented or explicitly flagged;
- no source raw mutation occurs.

STOP after parser/merge support is pushed. Do not wait for node109 campaign completion if local tests are complete.
