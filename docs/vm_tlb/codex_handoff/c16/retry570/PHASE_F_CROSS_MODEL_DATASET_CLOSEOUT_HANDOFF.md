# Phase F — cross-model normalization and dataset closeout

Run after Llama and all four remaining model phases are COMPLETE or precisely BLOCKED.

## Purpose

Turn per-model capture packs into one analysis-ready C16 AI-trace dataset without erasing model/runtime/phase differences.

## F0 — dataset manifest

Build one row per model and per phase-target class:

```text
MODEL_KEY
EXACT_MODEL_ID
REVISION_OR_CONTENT_HASH
QUANTIZATION
DTYPE
BATCH
INPUT_LENGTH
DECODE_LENGTH
PHASE
TARGET_CLASS
FULL_TARGET_IDENTITY
STATIC_RANGE
OPCODE
FINAL_CAPTURE_SCOPE
LAUNCH_COUNT
TOTAL_RECORDS
ADDRESS_RECORDS
TRACE_BYTES
RAW_SHA256
MODEL_PACK_COMMIT
STATUS
```

Do not normalize away differences such as AWQ versus BF16 or MoE versus dense.

## F1 — structural-zero audit

For every zero record count classify exactly one:

```text
STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED
LAUNCHED_BUT_ZERO_RECORDS_REQUIRES_INVESTIGATION
PHASE_NOT_EXECUTED
MODEL_BLOCKED_NO_CAPTURE
```

No bare `0` without cause.

## F2 — schema and consumer compatibility

Verify every successful trace can be consumed by the actual downstream parser/converter. If different target classes produce different record layouts, either normalize through an explicit versioned converter or keep separate schema classes.

Do not fabricate common fields that do not exist in the raw trace.

## F3 — cross-model comparability notes

Publish a compact note separating:

- architecture differences;
- precision/quantization differences;
- backend/fusion differences;
- workload-shape differences;
- phase-specific kernel dispatch differences;
- capture-scope differences.

This prevents later cache/TLB conclusions from attributing backend/shape artifacts solely to model architecture.

## F4 — integrity closure

Require:

```text
all successful raw payloads remote SHA -> local SHA closed
all per-model manifests validate
no duplicate artifact identities
no raw trace committed to Git
ACTIVE_GPU_PROCESS_COUNT=0
ACTIVE_DIAGNOSTIC_PROCESS_COUNT=0
MEASUREMENT_ACTIVE absent
```

## F5 — top-level publication

Publish a dataset pack, e.g.:

```text
docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/
  lane_g_retry570_nvbit175_post_llama_multimodel_dataset/
```

Include:

```text
MODEL_DATASET_MATRIX.tsv
PHASE_TARGET_MATRIX.tsv
STRUCTURAL_ZERO_AUDIT.tsv
DOWNSTREAM_CONSUMER_VALIDATION.json
CROSS_MODEL_COMPARABILITY_NOTES.md
RAW_ARTIFACT_INDEX.json
CAMPAIGN_SUMMARY.json
PUBLISH_MANIFEST.json
PUBLISH_VALIDATION_RECEIPT.json
```

## Final statuses

Preferred:

```text
C16_NVBIT175_POST_LLAMA_MULTIMODEL_DATASET_COMPLETE
```

or, if some models are genuinely blocked after exhaustive authorized recovery:

```text
C16_NVBIT175_POST_LLAMA_MULTIMODEL_DATASET_COMPLETE_WITH_BLOCKED_MODELS
```

A blocked status is not allowed merely because an asset was absent from one historical directory.
