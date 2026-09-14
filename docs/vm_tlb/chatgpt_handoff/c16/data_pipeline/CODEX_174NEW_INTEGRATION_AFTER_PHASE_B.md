# CODEX 174-new — Pipeline V1 Integration After Phase B

Ownership: ChatGPT
Execution node: 174-new / port 2239
Status: execute only after the current Phase-B data-root admission has PASS or PASS_WITH_FILESYSTEM_LIMITATIONS

## Objective

In one combined round, implement the destination half of Pipeline V1, qualify the real 109 -> 174-new -> 164 path, then—only if the data plane passes—import the existing RTX4080 R5 artifacts and the curated RTX3090 historical minimum set without rerunning scientific workloads.

## Preconditions

All must be known before formal integration:

```text
Phase B final decision
accepted 164 root
filesystem capability/fallback decision
109 producer-prep branch/commit
old174 handover commit 674e834d25ab4f5be914bcebe021ce685eb51e54
RTX4080 clean R5 authority b75f26674a09705659e770ab2134351414aa3c93
```

If the 109 producer prep is not complete, implement only receiver-side code/tests and STOP before cross-node transfer.

## Read first

```text
PARALLEL_EXECUTION_PLAN_V1.md
PIPELINE_V1_CONTRACT.md
Phase-B review pack / decision
109 producer review pack
C16_OLD174_FINAL_HANDOVER_TO_2239 review pack
```

## Branch isolation

Use a fresh execution branch/worktree. Suggested branch:

```text
hrl/c16-data-pipeline-v1-integration-174new-r1
```

Do not modify ChatGPT-owned handoff files.

## Part A — destination implementation

Implement/reuse shared code under:

```text
util/vm_tlb/c16/data_plane/
```

Required destination components:

```text
verify_capture.py
admit_capture.py
write_transfer_ack.py
catalog.py
rebuild_catalog_snapshot.py
legacy_import.py
```

Use the Phase-B accepted root exactly.

Required semantics:

```text
inbox/<RUN_ID>.partial
independent destination rehash
exact artifact-set comparison
quarantine on failure
no-overwrite admit
immutable catalog entry
ACK only after successful admit + catalog registration
deterministic TSV/Parquet snapshot rebuild
```

## Part B — cross-node qualification

Use `ssh gpu109` from 174-new and `ssh hrl174new` from 109.

Execute in this order and continue automatically only after each gate PASS:

### B1 small fixture

A tiny deterministic synthetic bundle.

Require full finalize -> publish -> verify -> admit -> catalog -> ACK -> producer transferred closure.

### B2 64 MiB fixture

Measure:

```text
source bytes
transfer duration
throughput
destination bytes
source/destination SHA
```

### B3 bounded large fixture

Target 1 GiB deterministic fixture.

If the mount/SSHFS path makes 1 GiB impractical, allow a bounded >=256 MiB fixture only when:

```text
small + 64MiB semantics already PASS
reason is recorded
throughput is measured
filesystem limitation is explicitly classified
```

### B4 resume case

Exercise a real partial/resume path. The method may pre-seed a deterministic prefix or intentionally interrupt a synthetic transfer, but must not corrupt an admitted destination.

### B5 collision/no-overwrite

Attempt duplicate RUN_ID or destination collision. Must fail closed without changing the existing admitted object.

### B6 corruption/quarantine

Mutate a synthetic destination payload after transfer-before-admit. Verification must fail and no ACK may be produced.

## Part C — legacy RTX4080 R5 import

Proceed in the same run only if Part B yields `PIPELINE_V1_END_TO_END_PASS`.

Do not rerun U5/U6/U7/U9.

Inventory and import the existing node109 R5 artifacts under their original producer/scientific identity.

Required metadata:

```text
legacy=true
producer=node109 RTX4080
R5 authority commit=b75f26674a09705659e770ab2134351414aa3c93
R4 quantitative data=non-authoritative
original absolute path
source size/SHA
destination size/SHA
artifact role
scientific status
```

Import only artifacts that can be path+size+SHA closed from current R5 evidence. Missing provenance => fail closed for that artifact, do not recreate it.

Recommended destination namespace:

```text
legacy/rtx4080_r5/<bundle-or-run-id>/
```

Register catalog entries.

## Part D — curated RTX3090 historical minimum archive

Proceed only if Parts B/C do not reveal data-plane corruption.

Use the old174 handover catalog as authority. Copy-not-move only the explicitly curated minimum formal comparison set, approximately 763.9 MB total, including the formal Route-B Q1/Q2 and Route-A bridge corpus identified in `HISTORICAL_TRACE_CATALOG.tsv`.

Do not bulk-copy `/root/share/c16_recovery_v3` or `/workspace/c16_exchange/autodl_wave1`.

Preserve:

```text
producer/campaign=RTX3090 historical
scientific_status=FORMAL where handover says FORMAL
34/36 exact map boundary
two CUTLASS failed-closed rows unchanged
```

Destination recommendation:

```text
legacy/rtx3090_minimal_compare/
```

Every copied object requires source and destination size/SHA equality and catalog registration.

## Part E — small authority metadata seed

Copy/register only small metadata needed for future joins:

```text
Llama R5 model/input authority receipts
21 Qwen historical binding receipts/index
Qwen3-8B / DeepSeek NO_HISTORICAL_FROZEN_BINDING audit metadata
old174 handover authority tables
```

Do not copy model weights in this round.

## Deliverables

Suggested review pack:

```text
docs/vm_tlb/review_packs/C16_DATA_PIPELINE_V1_END_TO_END_R1/
```

Must include:

```text
README.md
FINAL_DECISION.json
FILESYSTEM_BINDING.md
PIPELINE_TEST_MATRIX.tsv
TRANSFER_BENCHMARK.tsv
FAILURE_INJECTION.tsv
R5_LEGACY_IMPORT.tsv
RTX3090_MINIMAL_ARCHIVE.tsv
AUTHORITY_METADATA_SEED.tsv
CATALOG_SNAPSHOT.tsv
RAW_LOG_INDEX.tsv
OPEN_ISSUES.md
SHA256SUMS
```

## Acceptance criteria

Infrastructure PASS requires:

```text
PIPELINE_V1_END_TO_END_PASS
SMALL_FIXTURE_PASS
MEDIUM_FIXTURE_PASS
BOUNDED_LARGE_FIXTURE_PASS_OR_DOCUMENTED_LIMITATION
RESUME_PASS
NO_OVERWRITE_PASS
CORRUPTION_FAIL_CLOSED_PASS
ACK_ROUND_TRIP_PASS
CATALOG_IMMUTABLE_ENTRY_PASS
CATALOG_REBUILD_PASS
```

Real-data closeout additionally targets:

```text
R5_LEGACY_IMPORT_PASS_OR_PARTIAL_WITH_EXPLICIT_MISSING_PROVENANCE
RTX3090_MINIMAL_ARCHIVE_PASS
AUTHORITY_METADATA_SEED_PASS
```

A partial R5 import due only to already-missing provenance does not invalidate Pipeline V1; classify it explicitly and never regenerate evidence.

## STOP boundary

STOP after pipeline qualification + allowed legacy imports + catalog seed.

Do not start multi-model GPU capture.
Do not define new Qwen3/DeepSeek inputs.
Do not rerun old scientific workloads.
