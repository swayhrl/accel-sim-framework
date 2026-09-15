# CODEX Goal — old174 private-path closeout and selective export

## Status

Executable Goal. Run inside the old174 Docker reached by:

`ssh root@10.208.130.174 -p 2233`

This Goal is CPU/filesystem-only. Do not SSH back into the same endpoint as a prerequisite for local inspection.

## Inputs

Read these authorities before work:

- Coordination Round 2 `JOINT_REVIEW_AND_DECISIONS.md`
- old174 archaeology V1 commit `872423194e393fac9ca85171c77bafa87bde389e`
- old174 review pack `docs/vm_tlb/review_packs/C12_C15_OLD174_SOURCE_ARCHAEOLOGY_V1/`
- especially `OLD_DOCKER_PRIVATE_ASSETS.tsv`, `EXPERIMENT_LINEAGE.tsv`, `SCIENTIFIC_STATUS.tsv`, and `MIGRATION_RECOMMENDATION.md`

## Objective

Close the only major gap in old174 archaeology: directly inspect the old Docker's private filesystem and export only scientifically valuable C12-C15 assets that are truly private-only.

The Goal is not to rerun experiments and not to preserve an entire Docker filesystem.

## Mandatory first step: prove execution context

Record:

- hostname
- current PID namespace/container identifiers when observable
- `pwd`
- `findmnt /root/share`
- `findmnt /root/data`
- `findmnt /workspace`
- root filesystem mount source
- `ls -ld /workspace /root /tmp`

State explicitly that inspection is local to old174 and does not require SSH authentication.

## Search scope

### Exact known historical scopes

Inspect directly:

- `/workspace/vm-m4b-speculative/c5-results/C11_AUTHORIZED_NOT_RUN/`
  - `decode1/*/run.log`
  - `prefill/*/run.log`
  - sibling manifests/config copies/run receipts that bind those logs
- `/workspace/c14-dual-path-micro-runs/`
- any exact old-private path referenced by the C12-C15 Git review packs or provenance tables

### Narrow discovery scope

Search `/workspace`, non-shared `/root`, and `/tmp` for C12-C15-relevant names/markers only, including:

- `C11`, `C12`, `C13`, `C14`, `C15`
- `m4b`, `m4c`, `vm_tlb`, `c5-results`, `dual-path`, `segment`, `selective`
- `accel-sim.out`, `gpgpu-sim`, `traceg`, `kernelslist.g`
- `RUN_MANIFEST`, `RAW_LOG_INDEX`, `PROVENANCE`, `FINAL_REPORT`, `telemetry`

Do not recursively hash the entire Docker root or unrelated data.

## Classification

Every discovered candidate must be classified as exactly one of:

- `PRIVATE_ONLY_SCIENTIFIC_MUST_EXPORT`
- `PRIVATE_DUPLICATE_SHARED`
- `PRIVATE_DUPLICATE_GIT_DERIVED`
- `PRIVATE_OBSOLETE_OR_TEMPORARY`
- `PRIVATE_RELEVANCE_UNKNOWN`

Scientific status independently:

- `FORMAL`
- `DIAGNOSTIC`
- `PRE_FIX`
- `OBSOLETE`
- `UNKNOWN`

Do not infer scientific status from filename alone.

## Redundancy proof

Before exporting a large candidate, compare against:

- `/root/share/workspace_migrated_20260905/...`
- other existing `/root/share` retained copies
- Git authority hashes/receipts

Use size/file count first, then SHA-256 for exact candidate files or deterministic tree manifests.

If a byte-identical or hash-equivalent authoritative copy already exists in shared storage, classify it as `PRIVATE_DUPLICATE_SHARED` and do not export another copy.

Git source/config/report files should normally be referenced by commit/path, not exported as raw payload.

## Export protocol

Shared staging root:

`/root/share/c12_c15_inheritance_exchange_v1/old174_private_export/`

Create it only as needed.

For every `PRIVATE_ONLY_SCIENTIFIC_MUST_EXPORT` asset:

1. preserve source-root identity and relative path, for example:
   - `workspace/...`
   - `root_private/...`
   - `tmp/...`
2. copy; never move;
3. preserve file contents; metadata preservation is secondary to content identity;
4. compute source SHA-256 before/independently from destination verification;
5. compute destination SHA-256 after copy;
6. require source SHA == destination SHA for every exported file;
7. write a per-asset receipt.

Do not export:

- build caches;
- package caches;
- source trees already authoritative in Git;
- temporary editor files;
- large unrelated datasets;
- byte-identical shared duplicates.

## Required outputs in shared exchange

Under:

`/root/share/c12_c15_inheritance_exchange_v1/`

produce:

- `PRIVATE_EXPORT_MANIFEST.tsv`
- `PRIVATE_EXPORT_TREE_MANIFEST.tsv`
- `PRIVATE_EXPORT_SHA256SUMS`
- `PRIVATE_EXPORT_READY.json`
- `PRIVATE_PATH_CLOSEOUT.md`

`PRIVATE_EXPORT_MANIFEST.tsv` must include at least:

- asset_id
- source_absolute_path
- source_root
- destination_relative_path
- bytes
- file_count
- source_sha_or_tree_sha
- destination_sha_or_tree_sha
- lineage_id
- scientific_status
- classification
- shared_duplicate_checked
- git_authority_checked
- notes

`PRIVATE_EXPORT_READY.json` must state whether any private-only payload exists and bind the manifest/tree-manifest hashes.

## Required Git review pack

Create:

`docs/vm_tlb/review_packs/C12_C15_OLD174_PRIVATE_CLOSEOUT_V2/`

with at least:

- `README.md`
- `EXECUTION_CONTEXT.md`
- `PRIVATE_PATH_INVENTORY.tsv`
- `PRIVATE_VS_SHARED_COMPARISON.tsv`
- `PRIVATE_VS_GIT_AUTHORITY.tsv`
- `PRIVATE_EXPORT_MANIFEST.tsv` or a hash-bound copy/reference to the shared exchange manifest
- `EXPERIMENT_LINEAGE_PATCH.tsv`
- `MISSING_AFTER_DIRECT_INSPECTION.md`
- `SOURCE_DELETION_POLICY.md`
- `SHA256SUMS`

Also write/update a Codex report under:

`docs/vm_tlb/codex_handoff/c16/simulation_inheritance/OLD174_PRIVATE_CLOSEOUT_REPORT.md`

## Acceptance

PASS if:

- direct local inspection covers all five previous ODP rows;
- no old-private path remains uninspected merely because self-SSH failed;
- all scientifically valuable private-only artifacts are exported and hash-closed, or there are zero such artifacts and that is evidenced;
- private/shared/Git redundancy is explicitly resolved;
- no source deletion occurred.

Allowed final statuses:

- `OLD174_PRIVATE_CLOSEOUT_PASS_NO_PRIVATE_ONLY_ASSETS`
- `OLD174_PRIVATE_CLOSEOUT_PASS_EXPORTED_PRIVATE_ASSETS`
- `OLD174_PRIVATE_CLOSEOUT_PARTIAL_TRUE_FILESYSTEM_BLOCKER`

The third status requires a genuine local filesystem/permission/corruption blocker, not an SSH-to-self problem.

## Forbidden

Do not:

- run GPU workloads;
- rerun Accel-Sim/GPGPU-Sim experiments;
- delete or clean historical sources;
- bulk-copy the whole `/workspace` or `/root` tree;
- alter current C16 node164 formal captures;
- modify ChatGPT-owned handoff files.

## STOP

Commit/push the review pack and report, verify worktree cleanliness, then STOP.
