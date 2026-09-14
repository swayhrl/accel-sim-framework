# CODEX 109 — Pipeline V1 Producer Prep

Ownership: ChatGPT
Execution node: 109 / RTX4080
Status: may start immediately in parallel with 174-new Phase B

## Objective

Implement and validate the producer-side half of C16 Pipeline V1 locally on node109, without contacting 174-new/164 and without rerunning scientific workloads.

## Read first

```text
docs/vm_tlb/chatgpt_handoff/c16/data_pipeline/PARALLEL_EXECUTION_PLAN_V1.md
docs/vm_tlb/chatgpt_handoff/c16/data_pipeline/PIPELINE_V1_CONTRACT.md
```

## Source / branch isolation

Create a fresh execution branch/worktree. Suggested branch:

```text
hrl/c16-data-pipeline-v1-producer-109-r1
```

Do not modify ChatGPT-owned handoff files.

## Allowed work

Implement shared code under an explicit repository path, preferably:

```text
util/vm_tlb/c16/data_plane/
```

Producer-side required components:

```text
generate_run_id.py
finalize_capture.py
publish_capture.py
verify_remote_ack.py
cleanup_transferred.py
schemas/run_manifest.schema.json
schemas/transfer_ack.schema.json
schemas/catalog_entry.schema.json
```

Shared schema/helper code should be reusable by 174-new.

Create producer runtime roots if absent:

```text
/data/c16/capture/staging
/data/c16/capture/ready
/data/c16/capture/transferred
/data/c16/capture/quarantine
/data/c16/capture/transfer_receipts
```

Do not move or rename existing `/data/c16/ncu`, `/data/c16/nvbit_raw`, `/data/c16/results`, models, or inputs.

## Required behavior

### RUN_ID

- generated, filesystem-safe, UTC-bound, collision-resistant;
- no scientific authority inferred from the string;
- uniqueness test over at least 10k generated IDs.

### finalize_capture

Must fail closed on:

```text
missing required file
manifest mismatch
active/incomplete marker
unexpected symlink
existing ready destination
invalid scientific_status
malformed identity
```

Must produce deterministic inventory + SHA256 and READY marker only after closure.

### publish_capture

Implement transport preparation and dry-run command construction only in this round.

It must:

- target SSH alias `hrl174new` only via configuration/CLI, not hard-coded host IP;
- target a configurable destination root;
- use `<RUN_ID>.partial` staging semantics;
- support resume-capable rsync flags;
- refuse direct write to final `raw/<RUN_ID>`;
- refuse overwrite/collision;
- never delete source;
- have `--dry-run` or equivalent that performs no remote mutation.

Do NOT perform a real remote transfer in this round.

### verify_remote_ack

Validate ACK schema and exact binding to:

```text
run_id
source_manifest_sha256
PASS status
expected destination identity
```

Only after valid ACK may a local test fixture transition ready -> transferred.

### cleanup_transferred

Default mode must be non-destructive inventory/report only.

Any actual deletion mode must require an explicit flag and is not exercised or authorized in this stage.

## Required tests

Use synthetic local fixtures only.

At minimum:

```text
T1 valid finalize PASS
T2 missing artifact FAIL
T3 mutated artifact/hash FAIL
T4 symlink FAIL unless explicitly allowed
T5 duplicate RUN_ID / ready collision FAIL
T6 invalid status/schema FAIL
T7 deterministic manifest ordering PASS
T8 dry-run publish shows partial destination and no-delete semantics
T9 malformed ACK FAIL
T10 wrong manifest SHA ACK FAIL
T11 valid synthetic ACK PASS and ready -> transferred state transition
T12 cleanup default proves no deletion
T13 10k RUN_ID uniqueness PASS
```

Do not use GPU to satisfy these tests.

## Required deliverables

```text
producer implementation
schemas
unit/directed tests
sample synthetic RUN_MANIFEST
sample synthetic ACK
CLI help examples
review pack
codex handoff report
```

Suggested review pack:

```text
docs/vm_tlb/review_packs/C16_DATA_PIPELINE_V1_PRODUCER_109_R1/
```

It must include:

```text
README.md
MANIFEST.json
SOURCE_ANCHORS.md
CHANGED_FILES.md
VALIDATION_SUMMARY.md
TEST_MATRIX.tsv
SAMPLE_RUN_MANIFEST.json
SAMPLE_TRANSFER_ACK.json
OPEN_ISSUES.md
SHA256SUMS
```

## Acceptance criteria

PASS only if:

```text
PRODUCER_SCHEMA_PASS
RUN_ID_PASS
FINALIZE_FAIL_CLOSED_PASS
PUBLISH_DRY_RUN_PASS
ACK_VALIDATION_PASS
STATE_TRANSITION_PASS
NO_SOURCE_DELETE_PASS
NO_REMOTE_MUTATION_PASS
NO_GPU_WORKLOAD_RERUN_PASS
```

## STOP boundary

STOP after local producer prep is committed and pushed.

Do not contact 174-new for real data transfer.
Do not import R5.
Do not start multi-model capture.
Do not rerun Llama/NCU/NVBit.
