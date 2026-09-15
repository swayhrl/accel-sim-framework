# CODEX Goal — old174 C12–C15 Source Archaeology

## Role

Run on the old Docker:

```text
ssh root@10.208.130.174 -p 2233
```

This task reconstructs filesystem/provenance authority for historical C12–C15 TLB/Cache simulation work. It does not own future analysis design.

## Goal

Produce a complete, evidence-backed inventory of historical simulation inputs, code/config anchors, execution outputs, post-processing outputs and conclusion anchors, with special emphasis on distinguishing shared host-backed data from old-container-private data that would be lost when 2233 is retired.

## Hard safety constraints

- CPU-only / filesystem-only.
- Do not run GPU, NVBit, NCU, Nsight or model workloads.
- Do not rerun long simulator experiments in this round.
- Do not delete, move, rename, compress-in-place, truncate or rewrite historical evidence.
- Do not clean workspaces.
- Do not migrate large files yet.
- Do not modify ChatGPT-owned handoff files.
- Do not invent missing provenance.

## Search roots

### Shared / likely host-backed

Audit at least:

```text
/root/share
/root/data
```

Use `findmnt -T`, `stat`, `df -T`, and other read-only evidence to characterize mounts.

### Old-container private / uncertain

Audit at least:

```text
/workspace
/root
/tmp
```

Exclude recursive traversal of known large model/archive roots when they are unrelated to C12–C15. Search intelligently using stage names, filenames, receipts and known experiment identifiers rather than blindly hashing terabytes.

## Search vocabulary

Search for direct and historical aliases around:

```text
C12
C13
C14
C15
c12_c5
c13
c14
c15
vm_tlb
TLB
PTW
Segment
Selective
Cache
L1
L2
replay
finalize
checkpoint
m4b
m4c
traceg
Accel-Sim
GPGPU-Sim
```

Also inspect shell history / scripts / manifests / review packs / receipts for exact absolute paths referenced by old runs, but do not treat shell-history text alone as proof an artifact still exists.

## Required reconstruction per experiment

For each identifiable historical experiment/run, recover as much as evidence permits:

```text
stage
experiment_id / run_id
scientific_status
question / mechanism / variant
trace input absolute path
trace identity / hash / size
config path + SHA
framework commit
core/simulator commit
binary/build identity if preserved
exact or reconstructed launch command
important environment variables
raw run directory
stdout/stderr/logs
raw counters/statistics
post-processing script path + Git SHA if available
derived CSV/JSON/TSV outputs
review-pack/report/result anchor
known conclusion
known limitation
```

Any unresolved field must remain `UNKNOWN`.

## Special attention: historical simulation outputs

Do not stop after finding source code/configs. The main purpose is to find actual run outputs and derived results.

For each output tree, record:

- absolute path;
- total bytes;
- regular-file count;
- oldest/newest relevant mtime as low-trust metadata;
- key file names;
- key SHA256 hashes;
- whether it is shared-visible or old-container-private;
- whether it appears FORMAL / DIAGNOSTIC / PRE_FIX / OBSOLETE / UNKNOWN;
- what upstream trace/config/run it belongs to.

## Visibility classification

Classify each asset using exactly one of:

```text
SHARED_VISIBLE_UNCHANGED
OLD_DOCKER_PRIVATE_MUST_MIGRATE
GIT_AUTHORITY_ONLY
REDUNDANT_ARCHIVAL_COPY
MISSING_OR_UNKNOWN
```

See `SOURCE_CLASSIFICATION_AND_MIGRATION_POLICY.md`.

## Shared-path probes

Generate a compact set of representative probes for Round-2 verification from 174-new.

For each important shared path, choose one or more stable regular files and record:

```text
absolute_path
size
sha256
stat mode/uid/gid
mount target/source/fs type
```

Do not use inode equality as a required cross-container property; size/SHA/mount/path visibility are the relevant checks.

## Git versus filesystem source authority

For any source/config/analyzer copy found outside Git:

1. determine whether an equivalent authoritative Git path exists;
2. if possible identify Git commit or blob equality;
3. classify mirrored worktree/staging source as archival rather than authoritative when appropriate;
4. flag any scientifically important script/config that exists only on filesystem and is not represented in Git.

## Required deliverables

Create:

```text
docs/vm_tlb/review_packs/C12_C15_OLD174_SOURCE_ARCHAEOLOGY_V1/
├── README.md
├── EXPERIMENT_LINEAGE.tsv
├── EXPERIMENT_LINEAGE.json
├── FILESYSTEM_ASSET_INVENTORY.tsv
├── SHARED_PATH_PROBES.tsv
├── OLD_DOCKER_PRIVATE_ASSETS.tsv
├── TRACE_INPUT_INVENTORY.tsv
├── SIMULATOR_RUN_OUTPUT_INVENTORY.tsv
├── DERIVED_RESULT_INVENTORY.tsv
├── SCRIPT_CONFIG_AUTHORITY.tsv
├── SCIENTIFIC_STATUS.tsv
├── MISSING_OR_UNKNOWN.md
├── MIGRATION_RECOMMENDATION.md
└── SHA256SUMS
```

Also update a Codex-owned report under:

```text
docs/vm_tlb/codex_handoff/c16/simulation_inheritance/OLD174_SOURCE_ARCHAEOLOGY_REPORT.md
```

## Minimum acceptance criteria

The review pack must make it possible for ChatGPT to answer, without relying on chat history:

1. What C12–C15 formal/diagnostic simulation experiments existed?
2. What exact traces/configs/code versions fed them?
3. Where are the raw simulator outputs now?
4. Where are the derived statistics/results now?
5. Which assets are already visible to 174-new through shared mounts?
6. Which scientifically valuable assets exist only in old174 private storage?
7. Which referenced artifacts are missing or unresolved?
8. Which code/config copies are authoritative in Git and should not be migrated as duplicate source?
9. What must be copied in Round 2 before old174 can safely retire from this workflow?

## STOP condition

STOP after inventory/provenance reconstruction, review-pack hash closure, clean Git status and push.

Do not perform the actual large-file migration in this round.
