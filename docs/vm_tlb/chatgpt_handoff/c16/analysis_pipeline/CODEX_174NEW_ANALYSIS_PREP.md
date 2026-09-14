# CODEX 174-new — Analysis Prep Before Formal Trace Wave

Ownership: ChatGPT
Execution node: 174-new / port 2239
May run immediately in parallel with node109 pre-capture planning.

## Objective

Prepare the CPU-side analysis stack before new formal traces arrive, using existing archived RTX3090/R5 evidence only as read-only fixtures. Also close two non-blocking metadata gaps left by Pipeline V1 integration.

Do not wait for the node109 capture campaign.

## Read first

```text
docs/vm_tlb/chatgpt_handoff/c16/analysis_pipeline/PIPELINE_V1_INTEGRATION_REVIEW.md
docs/vm_tlb/chatgpt_handoff/c16/analysis_pipeline/ANALYSIS_OUTPUT_CONTRACT_V1.md
docs/vm_tlb/chatgpt_handoff/c16/data_pipeline/CODEX_174NEW_ANALYSIS_AFTER_PIPELINE.md
```

## Branch isolation

Create fresh branch/worktree, suggested:

```text
hrl/c16-analysis-prep-174new-v1
```

Do not modify ChatGPT-owned handoff files.

## Stage 0 — freeze pipeline consumption rules

Bind analysis to:

```text
Pipeline integration implementation:
3c4847d2da818013dca6422194af36966136ab31

canonical root:
/root/share/mnt164/huangrulin/c16_ai_workload
```

Until separately hardened, enforce:

```text
formal admission concurrency = 1
```

Do not change storage administration/permissions.

## Stage 1 — correct legacy/authority metadata state

### 1A actual RTX4080 R5 artifact reconciliation

The current archive contains N1 qualification artifacts; do not call those the complete R5 archive.

From 174-new, use `ssh gpu109` read-only to locate existing R5 artifacts for the accepted R5 authority:

```text
hrl/c16-4080-u5-u9-r5-clean
b75f26674a09705659e770ab2134351414aa3c93
```

Search bounded known R5 roots only, including `/data/c16/ncu`, `/data/c16/results`, and the R5 receipt/review references.

Target roles include, when independently closable:

```text
U5 repeated native result
U6 R5-local function/address map
U7 R5 NCU raw report
U7 export/metrics receipt
U9 target/raw stdout/address-bearing artifact
R5 isolation/identity receipts
```

For each object require:

```text
role
original path
size
SHA256
authority binding
```

Copy-not-move to `legacy/rtx4080_r5/` only if path/size/SHA/authority close.

Missing item => `MISSING_PROVENANCE`; do not rerun/recreate.

Keep N1 qualification archive separately classified as N1, not R5.

### 1B authority metadata seed

Seed small metadata needed for future joins, preferably from node109's already admitted authority packages and/or frozen Git handover tables:

```text
Llama exact model/input authority used by R5
21 exact Qwen historical bindings
Qwen3-8B NO_HISTORICAL_FROZEN_BINDING audit
DeepSeek-V2-Lite NO_HISTORICAL_FROZEN_BINDING audit
model revisions / asset receipt SHAs
```

No model weights in this task.

Produce a machine-readable authority index under node164 provenance/catalog area with per-file/source SHA closure.

## Stage 2 — parser foundation

Implement/reuse CPU parsers under an explicit Git path such as:

```text
util/vm_tlb/c16/analysis/
```

Required capabilities:

1. memory-only/raw JSONL parser for the archived Q2 Route-B format;
2. NCU CSV/text normalization;
3. generic object-range join helper;
4. page/cache-line fingerprint builder;
5. parse/feature receipt writer;
6. index builder for parsed/features.

Do not require CUDA/NVBit/NCU runtime on 174-new.

Write all large derived outputs directly under node164, not local overlay.

## Stage 3 — exact historical regression

Use archived formal RTX3090 Q2 Prefill and Decode raw as parser regression fixtures.

Reproduce the exact expected anchor metrics in `ANALYSIS_OUTPUT_CONTRACT_V1.md`.

At minimum require exact equality for:

```text
lane event count
read/write counts
2B/4B width counts
unique VA
128B lines
4K pages
2M pages
```

If the parser cannot reproduce them exactly, STOP before claiming parser qualification.

Historical callback-order reuse may be reproduced as an optional secondary check, but must retain the label `OBSERVED_CALLBACK_ORDER`.

## Stage 4 — synthetic correctness tests

Add directed fixtures for:

```text
4K page bucketing across boundaries
64K page bucketing
128B cache-line bucketing
multi-byte access crossing a line/page boundary
read/write/atomic classification
active mask / active lane handling
object overlap and alias priority
UNKNOWN object attribution
empty/partial input fail-closed behavior
deterministic output ordering
```

## Stage 5 — NCU parser regression

Use the archived N1 report/CSV only as a parser fixture and retain its N1 classification.

If actual R5 U7 export is successfully reconciled in Stage 1A, normalize it separately as R5.

Do not mix N1 and R5 metrics.

## Stage 6 — prepare incremental analysis entrypoint

Provide a CLI/workflow that, given one newly cataloged formal RUN_ID, performs:

```text
raw verify reference
-> parse
-> fingerprint
-> derived receipt
-> PARSE_INDEX / FEATURE_INDEX update or deterministic snapshot rebuild
```

It must not wait for a campaign-wide batch.

## Required outputs

Review pack suggested:

```text
docs/vm_tlb/review_packs/C16_ANALYSIS_PREP_174NEW_V1/
```

Include at minimum:

```text
README.md
FINAL_DECISION.json
R5_ACTUAL_ARTIFACT_RECONCILIATION.tsv
AUTHORITY_METADATA_SEED.tsv
Q2_PARSER_REGRESSION.tsv
ANALYSIS_TEST_MATRIX.tsv
NCU_PARSER_REGRESSION.tsv
PARSE_INDEX_SAMPLE.tsv
FEATURE_INDEX_SAMPLE.tsv
RAW_LOG_INDEX.tsv
OPEN_ISSUES.md
SHA256SUMS
```

## Acceptance criteria

PASS only if:

```text
ANALYSIS_PREP_PASS
Q2_PREFILL_REGRESSION_EXACT_PASS
Q2_DECODE_REGRESSION_EXACT_PASS
PAGE_LINE_FINGERPRINT_TESTS_PASS
UNKNOWN_ATTRIBUTION_PRESERVED_PASS
NCU_PARSER_BOUNDARY_PASS
RAW_IMMUTABILITY_PASS
DERIVED_RECEIPT_PASS
INCREMENTAL_RUN_ENTRYPOINT_PASS
AUTHORITY_METADATA_SEED_PASS
```

`RTX4080_R5_ARCHIVE_PASS` is desirable but not mandatory if existing R5 evidence is genuinely missing; use explicit `PARTIAL_MISSING_PROVENANCE` instead.

## Non-authorizations

Do not:

```text
rerun GPU workloads
retokenize inputs
invent Qwen3/DeepSeek bindings
change old raw evidence
make universal model claims
perform multi-model capture
```

## STOP boundary

STOP after the analysis foundation and metadata closeout are committed/pushed.

Do not wait for future formal Qwen traces before reporting this stage.
