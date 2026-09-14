# Phase B — 174-new / 164 Data Root Admission

## Purpose

This phase admits the long-term C16 AI-workload storage root visible from new174/2239. It is CPU/storage-only.

It does **not** implement the 109→174-new transfer pipeline and does **not** import historical scientific data.

## Starting authority

Repository branch:

```text
hrl/c16-174new-164-data-root-admission-v1
```

This branch descends from accepted old174 final handover:

```text
674e834d25ab4f5be914bcebe021ce685eb51e54
```

Read first:

```text
docs/vm_tlb/chatgpt_handoff/c16/data_pipeline/DATA_ROOT_CONTRACT_V1.md
docs/vm_tlb/review_packs/C16_OLD174_FINAL_HANDOVER_TO_2239/README.md
docs/vm_tlb/review_packs/C16_OLD174_FINAL_HANDOVER_TO_2239/OPEN_ISSUES.md
```

## Target root

Candidate:

```text
/root/share/mnt164/huangrulin/c16_ai_workload_2239
```

Do not assume mount identity solely from path. Record actual `findmnt`/`mount`/`df`/filesystem observations available inside new174.

Do not commit credentials, remote host addresses, SSH key paths, or unnecessary network topology into Git.

## Required persistent layout

Create only if absent, without overwriting existing content:

```text
inbox/
raw/
provenance/
parsed/
features/
datasets/
catalog/
reports/
quarantine/
legacy/
tmp/
```

Create a header-only:

```text
catalog/C16_TRACE_CATALOG.tsv
```

with fields defined in `DATA_ROOT_CONTRACT_V1.md`.

Create a small storage receipt under:

```text
provenance/DATA_ROOT_ADMISSION_V1.json
```

The persistent receipt must contain only non-secret storage identity/behavior needed by the pipeline: root path, filesystem type if observable, capacity/free-space snapshot, admission timestamp, supported/unsupported semantics, and Git commit. Do not include secrets or private SSH endpoint details.

## Isolated admission fixture

Use a unique test ID under the candidate root. Never reuse a scientific RUN_ID.

Test at least:

1. small deterministic payload write;
2. close + file `fsync()` and report result;
3. SHA256 and size before rename;
4. no-overwrite rename semantics;
5. same-root `inbox/<fixture>.partial` → `raw/<fixture>` promotion behavior;
6. reopen destination and verify size + SHA256;
7. immediate path visibility after rename;
8. bounded medium-file behavior (target 64 MiB, deterministic content is sufficient);
9. medium-file close/fsync/reopen/SHA verification;
10. cleanup of all fixture payloads and temporary directories.

Also test directory `fsync()` if supported. If it returns an expected FUSE/SSHFS limitation, record the exact errno/message; do not treat unsupported directory fsync alone as failure.

Do not claim strict POSIX atomicity beyond what was actually observed. Report rename behavior as an admission observation.

## No-overwrite requirement

Admission scripts/helpers must refuse to overwrite:

- existing root receipt;
- existing catalog content beyond an expected header-only initial file;
- any existing raw/inbox run directory;
- any pre-existing user payload.

If the candidate root already contains unexpected data, inventory it read-only and stop before writing outside a fresh isolated admission namespace.

## Result pack

Generate:

```text
docs/vm_tlb/review_packs/C16_DATA_ROOT_ADMISSION_V1/
```

At minimum:

```text
README.md
DATA_ROOT_RECEIPT.json
MOUNT_AND_CAPACITY.md
FILESYSTEM_SEMANTICS.json
CATALOG_SCHEMA.tsv
FIXTURE_VALIDATION.json
OPEN_ISSUES.md
PHASE_B_DECISION.json
SHA256SUMS
```

The Git review receipt may mirror non-secret fields from the persistent storage receipt.

## Decision values

Exactly one:

```text
DATA_ROOT_ADMISSION_PASS
DATA_ROOT_ADMISSION_PASS_WITH_FILESYSTEM_LIMITATIONS
DATA_ROOT_ADMISSION_BLOCKED
```

`PASS_WITH_FILESYSTEM_LIMITATIONS` is acceptable when file write/close/hash/reopen and same-root rename work, but a non-essential operation such as directory fsync is unsupported and a fail-closed pipeline workaround is clearly specified.

Block if any of these fail materially:

- persistent root cannot be created/read/written;
- hash/size is not stable after reopen;
- rename/promotion behavior is unsuitable for no-overwrite admission;
- medium-file test is not stable;
- mount is not reliably visible from new174;
- test cleanup cannot be completed safely.

## Hard prohibitions

```text
NO GPU/CUDA/Llama/NVBit/NCU/NSYS execution.
NO SSH to node109 for capture work.
NO old174 bulk copy.
NO RTX3090 minimal-set import yet.
NO RTX4080 R5 import yet.
NO model migration.
NO Qwen input migration.
NO parser/feature pipeline implementation yet.
NO scientific catalog registration yet.
NO deletion or modification of historical evidence.
NO large raw data in Git.
```

## Stop condition

After storage root and review pack are admitted, commit and push this branch and STOP.

Do not start Pipeline V1 / Phase C in the same run.
