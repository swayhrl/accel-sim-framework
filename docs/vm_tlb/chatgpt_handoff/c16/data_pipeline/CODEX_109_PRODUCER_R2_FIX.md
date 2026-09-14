# CODEX 109 — Pipeline V1 Producer R2 Fix

Ownership: ChatGPT
Execution node: 109 / RTX4080
Status: execute as a fresh branch/worktree from this coordination branch.

## Objective

Repair Producer R1 so that the producer implementation actually satisfies the frozen `PIPELINE_V1_CONTRACT.md` and the original T1–T13 acceptance matrix. This is still CPU/synthetic only: no real remote transfer and no GPU/scientific workload rerun.

## Read first

1. `docs/vm_tlb/chatgpt_handoff/c16/data_pipeline/PRODUCER_109_R1_REVIEW.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/data_pipeline/PIPELINE_V1_CONTRACT.md`
3. `docs/vm_tlb/chatgpt_handoff/c16/data_pipeline/CODEX_109_PRODUCER_PREP.md`

## Branch isolation

Suggested execution branch:

`hrl/c16-data-pipeline-v1-producer-109-r2`

Do not modify ChatGPT-owned handoff files.

## Required implementation

### 1. Real CLIs

Implement functional argparse/exit-code CLIs for:

- `generate_run_id.py`
- `finalize_capture.py`
- `publish_capture.py`
- `verify_remote_ack.py`
- `cleanup_transferred.py`

Each must support `--help` and deterministic machine-readable output where applicable.

### 2. Frozen schemas

Implement strict JSON schemas matching `PIPELINE_V1_CONTRACT.md`:

- run manifest: all required top-level fields and nested semantic identity;
- transfer ACK: run_id, source manifest SHA, destination verification SHA, file_count, total_bytes, destination_raw_path, verified_at_utc, verification_status, catalog_entry_sha256;
- catalog entry: multi-file run authority via manifest SHA, not a single raw payload SHA.

Reject unknown/malformed structure where the frozen contract requires exactness.

### 3. finalize_capture

Must:

- validate the strict manifest schema before mutation;
- require exact run_id match between CLI/manifest/directory contract;
- reject CAPTURING/incomplete state;
- reject symlinks;
- reject missing required artifacts;
- detect declared-vs-observed artifact mismatch if a declaration is present;
- build deterministic sorted artifact inventory;
- hash every regular artifact;
- write `RUN_MANIFEST.json` atomically using temp + fsync + rename;
- generate a local close receipt containing manifest SHA, file_count, total_bytes, closed_at_utc;
- write READY only after all closure steps pass;
- fsync relevant files/directories when supported locally;
- promote staging -> ready with no-overwrite behavior;
- leave source evidence recoverable/fail-closed on error.

### 4. publish_capture dry-run

Implement real command construction and dry-run validation for transport:

- SSH alias configurable, expected use `hrl174new`;
- destination root configurable;
- destination must be `inbox/<RUN_ID>.partial/`;
- resume-capable rsync flags;
- copy-not-move;
- no `--delete`;
- refuse final `raw/<RUN_ID>` as direct target;
- refuse unsafe path traversal and empty/invalid RUN_ID;
- `--dry-run` performs zero remote mutation and prints/records exact argv.

Do not execute a real remote transfer in R2.

### 5. verify_remote_ack and state transition

Validate strict ACK schema and bind at minimum:

- run_id;
- source manifest SHA256;
- verification_status=PASS;
- expected destination raw path/identity;
- destination verification SHA;
- file_count;
- total_bytes;
- catalog_entry_sha256.

On valid synthetic ACK, perform/verify a no-overwrite `ready/<RUN_ID>` -> `transferred/<RUN_ID>` transition while preserving artifacts. Invalid/mismatched ACK must not mutate local state.

### 6. cleanup_transferred

Default mode: report/inventory only; absolutely no deletion.

Optional destructive mode may exist only behind an explicit flag plus confirmation gates, but must not be exercised in this stage.

## Required T1–T13 tests

Implement separate named tests and record each result independently:

- T1 valid finalize PASS
- T2 missing artifact FAIL
- T3 mutated artifact / declared hash mismatch FAIL
- T4 symlink FAIL
- T5 duplicate RUN_ID / ready collision FAIL
- T6 invalid scientific status and malformed schema/identity FAIL
- T7 deterministic manifest/inventory ordering PASS
- T8 publish dry-run targets `.partial`, uses resume-capable copy, and proves no-delete/no-remote-mutation semantics
- T9 malformed/incomplete ACK FAIL
- T10 wrong run_id/source-manifest/destination binding ACK FAIL
- T11 valid synthetic ACK PASS and ready -> transferred transition PASS
- T12 cleanup default proves no deletion
- T13 10k RUN_ID uniqueness + filesystem-safe syntax PASS

Add negative tests for path traversal and direct-to-raw target if not already covered.

## Required review evidence

New review pack:

`docs/vm_tlb/review_packs/C16_DATA_PIPELINE_V1_PRODUCER_109_R2/`

Must include:

- README.md
- MANIFEST.json
- SOURCE_ANCHORS.md
- CHANGED_FILES.md
- VALIDATION_SUMMARY.md
- TEST_MATRIX.tsv with one row per T1–T13
- CLI_HELP.txt (or per-command help evidence)
- SAMPLE_RUN_MANIFEST.json conforming to strict schema
- SAMPLE_LOCAL_CLOSE_RECEIPT.json
- SAMPLE_TRANSFER_ACK.json conforming to strict schema
- PUBLISH_DRY_RUN.txt with exact argv and no-mutation declaration
- OPEN_ISSUES.md
- SHA256SUMS

## Acceptance criteria

PASS only if all are evidenced:

- `PRODUCER_R2_SCHEMA_PASS`
- `PRODUCER_R2_CLI_PASS`
- `FINALIZE_FAIL_CLOSED_PASS`
- `ATOMIC_MANIFEST_CLOSE_PASS`
- `PUBLISH_DRY_RUN_PASS`
- `ACK_STRICT_BINDING_PASS`
- `STATE_TRANSITION_PASS`
- `CLEANUP_NONDESTRUCTIVE_DEFAULT_PASS`
- `T1_T13_INDIVIDUAL_PASS`
- `NO_REMOTE_MUTATION_PASS`
- `NO_SOURCE_DELETE_PASS`
- `NO_GPU_WORKLOAD_RERUN_PASS`

## STOP

Commit/push and STOP after local R2 tests.

Do not contact 174-new for real transfer.
Do not import R5.
Do not start multi-model capture.
