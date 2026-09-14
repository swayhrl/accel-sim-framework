# C16 Data Pipeline — CODEX_NEXT_STAGE

## Status

Authorized now: **Phase B only**.

Execution location: **new174 / port 2239 only**.

Do not touch node109, old174, or scientific raw payloads in this phase.

## Objective

Qualify and freeze the node164 long-term data root for the future C16 109 → new174 → 164 pipeline.

Target decision:

- `DATA_ROOT_ADMISSION_PASS`, or
- `DATA_ROOT_ADMISSION_PASS_WITH_FILESYSTEM_LIMITATIONS`, or
- `DATA_ROOT_ADMISSION_BLOCKED`.

## Source anchors

Coordination branch:

`hrl/c16-data-pipeline-phase-b-coordination-v0`

Old174 handover:

`674e834d25ab4f5be914bcebe021ce685eb51e54`

New174 destination acceptance baseline:

`43212af0de0eef1cd72d905e11bfdeb2fe0e6d37`

RTX4080 R5 scientific anchor:

`b75f26674a09705659e770ab2134351414aa3c93`

## Worktree / branch isolation

On new174, create a fresh execution branch/worktree from the coordination branch.

Suggested execution branch:

`hrl/c16-data-pipeline-phase-b-174new-v1`

Do not modify ChatGPT-owned files under:

`docs/vm_tlb/chatgpt_handoff/c16/data_pipeline/`

## Canonical data root

Phase B freezes the canonical root as:

`/root/share/mnt164/huangrulin/c16_ai_workload`

The earlier candidate:

`/root/share/mnt164/huangrulin/c16_ai_workload_2239`

is superseded because the Docker port is not scientific identity.

Before creating anything:

1. inspect both paths;
2. if either already contains non-fixture data, STOP and report;
3. do not rename, merge, delete or overwrite any existing content.

## Required namespace

If preflight is clean, create only the namespace required for the data plane:

```text
inbox/
raw/
provenance/
parsed/
features/
datasets/
catalog/
  entries/
  snapshots/
reports/
quarantine/
legacy/
tmp/
```

Do not copy model weights, traces, R5 artifacts or historical 3090 data in Phase B.

## Required filesystem/storage preflight

Record at minimum:

- hostname / user;
- resolved mount path;
- `df -hT` for the data root;
- available bytes/inodes if obtainable;
- filesystem type (`fuse.sshfs` expected);
- mount options visible to the container;
- canonical root ownership and mode;
- current free space;
- observed legacy candidate-root state.

Do not treat the mount as local ext4.

## Required data-root admission canary

Use synthetic fixtures only.

### A. Small-file semantics

Test a small deterministic fixture and record:

- create/write;
- file `fsync` where supported;
- close/reopen;
- exact size;
- SHA256;
- read-back hash;
- same-root rename from `inbox/<fixture>.partial` to a test-admit location;
- destination visibility after reopen;
- collision/no-overwrite behavior;
- cleanup.

### B. Medium-file semantics

Create a deterministic **64 MiB** fixture without consuming local new174 disk as an intermediate bulk staging area.

Verify:

- write completion;
- file close/fsync behavior;
- size;
- SHA256 before/after reopen;
- rename visibility;
- cleanup.

Do not use a real model or trace.

### C. Directory fsync / no-replace semantics

Probe and record support for:

- directory `fsync`;
- `renameat2(..., RENAME_NOREPLACE)` or equivalent no-overwrite primitive if readily available.

Unsupported directory fsync or no-replace primitives do **not automatically block** Phase B if:

- file write/reopen/hash is reliable;
- same-mount rename works;
- collision is detectable;
- Phase C can implement an explicit fail-closed fallback.

Record the exact limitation and resulting protocol requirement.

## Catalog seed

Create only a header/schema seed, not real scientific entries.

Prefer immutable per-run catalog entries in:

`catalog/entries/`

and deterministic snapshots in:

`catalog/snapshots/`.

Create a machine-readable `CATALOG_SCHEMA_V1.json` defining at least:

- run_id;
- model;
- revision;
- scenario;
- phase;
- instrument;
- target;
- producer_host;
- producer_commit;
- model_binding;
- input_binding;
- raw_path;
- raw_bytes;
- raw_sha256;
- transfer_status;
- parse_status;
- feature_status;
- scientific_status.

Do not register R5 or historical 3090 data yet.

## Required receipts/results

Commit a Phase B result set under a new review pack, suggested:

`docs/vm_tlb/review_packs/C16_DATA_PIPELINE_PHASE_B_174NEW_164_ADMISSION/`

It must contain at least:

- `README.md`
- `DATA_ROOT_ADMISSION_V1.json`
- `FILESYSTEM_SEMANTICS.json`
- `CATALOG_SCHEMA_V1.json`
- `PHASE_B_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

`DATA_ROOT_ADMISSION_V1.json` should record the canonical root, mount identity, capacity, namespace inventory and canary hashes/results.

`FILESYSTEM_SEMANTICS.json` should explicitly record which local-filesystem assumptions are supported, unsupported or unknown.

## Acceptance criteria

### PASS

Use `DATA_ROOT_ADMISSION_PASS` only if all required semantics are supported without protocol caveats.

### PASS WITH LIMITATIONS

Use `DATA_ROOT_ADMISSION_PASS_WITH_FILESYSTEM_LIMITATIONS` if the root is usable for the planned pipeline but SSHFS lacks optional durability/atomic primitives such as directory fsync or no-replace rename.

The report must name the fallback Phase C must implement.

### BLOCKED

Use `DATA_ROOT_ADMISSION_BLOCKED` if any of the following occurs:

- data root is not stably writable/readable;
- read-back SHA mismatch;
- medium fixture cannot be reliably written/reopened/verified;
- same-mount rename is unreliable;
- existing non-fixture content creates an unresolved namespace conflict;
- storage availability is materially insufficient;
- any operation would require destructive handling of existing data.

## Explicitly forbidden scope

Do NOT:

- run GPU/CUDA/Llama/NVBit/NCU/NSYS workloads;
- SSH to node109 for data transfer;
- import R5 artifacts;
- copy the 3090 historical set;
- copy model weights;
- modify `/root/share/c16_recovery_v3` or `/workspace/c16_exchange/autodl_wave1`;
- change old174 data;
- build the full transfer/ACK implementation yet;
- enter multi-model capture;
- delete or clean historical evidence.

## Git requirements

- use explicit `git add <paths>`;
- `git diff --check` must pass;
- worktree must be clean at closeout;
- update a Codex-owned report under `docs/vm_tlb/codex_handoff/c16/data_pipeline/`;
- commit and push the execution branch.

## STOP condition

After Phase B decision + review pack + Codex report are committed and pushed, **STOP**.

Do not begin Phase C until ChatGPT reviews Phase B.
