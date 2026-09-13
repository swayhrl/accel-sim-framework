# C16 Recovery V3 — Final Dataset and Closeout Handoff

## Purpose

Normalize every accepted native/census/capture result into one locally durable, cross-model dataset and publish a compact Git review pack without embedding raw traces.

## Local dataset root

Use the existing project artifact convention and create a dedicated recovery-v3 local root, for example:

```text
artifacts/c16_g_retry570/recovery_v3/
```

Do not move older accepted Llama artifacts; reference them by path/SHA/commit and, where helpful, create immutable indexes pointing to the inherited local payloads.

## Required top-level indexes

At minimum create:

```text
C16_RECOVERY_V3_DEPLOYMENT_MATRIX.tsv
C16_RECOVERY_V3_SCENARIO_MATRIX.tsv
C16_RECOVERY_V3_NATIVE_CATALOG_INDEX.tsv
C16_RECOVERY_V3_TARGET_PLAN_INDEX.tsv
C16_RECOVERY_V3_TRACE_DATASET_INDEX.tsv
C16_RECOVERY_V3_RAW_ARTIFACT_INDEX.json
C16_RECOVERY_V3_RESOURCE_SKIPS.tsv
C16_RECOVERY_V3_USER_ACTION_EXCEPTIONS.tsv
C16_RECOVERY_V3_COST_LEDGER.tsv
```

## Trace dataset row schema

Each accepted trace row must include:

```text
model/deployment key
authority role (C16_AUTHORITATIVE / USER_EXTENSION)
model ID + revision/content manifest
wave
scenario
requested batch/context/decode
actual token count
phase
decode step when applicable
target-plan ID/SHA
target semantic class
full function/kernel identity
module/library identity
static range
opcode
memory space
launch count
record count
address-record count
trace bytes
local raw path
raw SHA256
capture terminal status
source run_id
producer code commit
evidence publication commit
limitation/evidence tier
```

## Native/census normalization

Do not reduce missing/blocked/skipped rows to zero measurements.

Use explicit states:

```text
COMPLETE
BOUNDED_PARTIAL
SKIPPED_RESOURCE
USER_ACTION_GATED_ACCESS
IDENTITY_UNRESOLVED_AFTER_AUTHORITY_SEARCH
NOT_APPLICABLE
```

A zero record count is scientific data only when the target launch/phase contract establishes that zero is meaningful. Otherwise use an explicit missing/status field.

## Cross-model integrity checks

Before publication verify:

1. no static range is inherited across models without a per-model requalification receipt;
2. raw and AWQ Qwen7 are distinct deployment identities;
3. prefill/decode targets remain phase-specific;
4. Llama S0 inherited evidence is not duplicated as a new recovery-v3 run;
5. all required successful raw payloads have local SHA closure;
6. `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0`;
7. no raw trace is committed to Git;
8. every scenario row has an explicit execution/scientific status;
9. every resource skip has a resource evidence receipt;
10. every user-action exception lists exact missing action/credential/identity and does not block unrelated completed rows.

## Wave checkpoints

Publish at least:

- Wave-1 checkpoint after Llama/Qwen2.5 family rows are closed;
- final Wave-2 + extension checkpoint.

This lets downstream C/H/A consume fixed evidence before the full campaign ends.

## Final Git review pack

Publish compact metadata under a dedicated path such as:

```text
docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/
  lane_g_retry570_full_authority_recovery_v3/
```

Include:

- final report;
- model/scenario execution matrix;
- target-plan index;
- trace dataset index;
- local raw-artifact SHA summary;
- resource/user-action exception tables;
- cleanup audit;
- cost summary;
- publish manifest + validator receipt.

## Final status policy

Preferred:

```text
C16_FULL_AUTHORITY_RECOVERY_V3_DATASET_COMPLETE
```

If true external exceptions remain after all recovery attempts:

```text
C16_FULL_AUTHORITY_RECOVERY_V3_DATASET_COMPLETE_WITH_EXTERNAL_EXCEPTIONS
```

Do not use `COMPLETE_WITH_BLOCKED_MODELS` for fixable network/package/transfer problems.

## Required final report lead fields

```text
RECOVERY_V3_STATUS=
RECOVERY_V3_COMMIT=
PUBLISH_MANIFEST_SHA256=
WAVE1_STATUS=
WAVE2_STATUS=
GLM_EXTENSION_STATUS=
TOTAL_DEPLOYMENTS_COMPLETE=
TOTAL_SCENARIO_ROWS_COMPLETE=
TOTAL_BOUNDED_PARTIAL_ROWS=
TOTAL_RESOURCE_SKIPS=
TOTAL_USER_ACTION_EXCEPTIONS=
ALL_SUCCESSFUL_RAW_LOCAL_SHA_CLOSED=
REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=
TOTAL_LOCAL_RAW_BYTES=
ACTIVE_GPU_PROCESS_COUNT=
ACTIVE_DIAGNOSTIC_PROCESS_COUNT=
MEASUREMENT_ACTIVE_AFTER_CAMPAIGN=
```

Then report each deployment's exact identity, scenario coverage, native/census status, target-plan SHA, trace coverage, local raw bytes/SHA closure, and any remaining limitation.

## Acceptance

R8 and R9 gates in `C16_FULL_AUTHORITY_RECOVERY_V3_STAGE_ACCEPTANCE.md` must pass before declaring the campaign complete.
