# Codex start — AI workload source export V0

## Branch

```text
hrl/c16-ai-workload-2233-to-2239-handoff-v0
```

## Required handoff

Read completely before making changes:

```text
docs/vm_tlb/codex_handoff/c16/4080_migration/AI_WORKLOAD_2233_TO_2239_HANDOFF_V0.md
```

## Scope

Execute **M0 / V0 source inventory and Git handoff preparation only**.

The current Docker remains active for decouple-L1/L2 and other architecture work. Do not clean, repurpose, or retire it.

The destination Docker is the future primary AI-workload/NVBit/NCU/Cache-TLB analysis lane, but do not assume that source-local paths, Python environments, runtime libraries, model caches, or raw data are automatically valid there.

## Startup gates

Before modifying anything:

1. verify this branch and HEAD;
2. record `git status` and all worktrees;
3. read the handoff fully;
4. inspect the current 4080 R5 authority at `b75f26674a09705659e770ab2134351414aa3c93`;
5. inspect the RTX3090 closeout inventory at `649af1b9d65a774d4aa8c32a15f9b6f4da0dd4d9` as historical reference only;
6. inventory first; do not bulk-copy or bulk-commit.

## Required work

Audit the source workspace for all files needed to continue the AI-workload line on the destination Docker.

Pay special attention to:

```text
util/vm_tlb/c16/**
docs/vm_tlb/codex_handoff/c16/**
docs/vm_tlb/review_packs/C16_4080*/**
current NVBit C16 tracer/tool source
NCU wrappers/exporters
Llama/other-model runners
model/input identity receipts
static-map/disassembly helpers
parsers and analysis scripts
current R5 raw/report references
historical 3090 closeout references needed for future comparison
```

Do not assume those globs are exhaustive. Use Git history and the R5/migration documents to identify dependencies.

For each discovered item classify it as exactly one of:

```text
GIT_REQUIRED
STORAGE_REQUIRED
REBUILD_OR_VERIFY_ON_DEST
SOURCE_RETAIN
EXCLUDE_SECRET_OR_HOST_PRIVATE
UNKNOWN_PROVENANCE
```

For source uncommitted/local-only AI code, classify separately as:

```text
COMMIT_REQUIRED
ALREADY_SUPERSEDED
LOCAL_DEBUG_ONLY
UNRELATED_TO_AI_WORKLOAD
UNKNOWN_REVIEW_REQUIRED
```

If `COMMIT_REQUIRED`, inspect carefully and commit only reproducibility-critical code/config/docs. Do not `git add -A` blindly.

## Required output directory

Create:

```text
docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V0_SOURCE_EXPORT/
```

Required outputs:

```text
SOURCE_STATE.md
GIT_EXPORT_LIST.txt
GIT_UNCOMMITTED_REVIEW.md
ARTIFACT_TRANSFER_MANIFEST.tsv
STORAGE_TRANSFER_PLAN.md
SOURCE_RETAIN_LIST.md
DESTINATION_ACCEPTANCE_CHECKLIST.md
UNKNOWN_PROVENANCE.md
MIGRATION_SUMMARY.json
```

Add CPU-only helper scripts only if they make the inventory deterministic and reviewable.

## Storage policy

Do not add raw traces, `.ncu-rep`, `.nsys-rep`, model weights, caches, or other bulk artifacts to Git.

For large scientific artifacts, record:

```text
path
role
size
SHA256 or authoritative hash receipt
campaign/GPU
whether needed on destination
transfer status
```

Do not invent an external-storage destination path. If the destination storage mount is not visible from the source Docker, mark the destination path `TO_BE_BOUND_ON_DESTINATION`.

Historical data transfer is copy-not-move.

The RTX3090 recovery endpoint must not be bulk-copied merely because it exists. Use the V0 3090 closeout inventory to recommend the minimal subset useful for future Cache/TLB/AI workload re-analysis.

## Hard prohibitions

```text
NO deletion/move/rename/rewrite of source evidence.
NO retirement of the source Docker.
NO modification of decouple-L1/L2 work.
NO broad GPU run for migration bookkeeping.
NO rerun of RTX3090 Q1/Q2/Route-A.
NO rerun of RTX4080 R5 solely for migration.
NO authority merging across RTX3090 and RTX4080.
NO large/raw/model assets in Git.
NO credentials, SSH keys, tokens, private addresses, or secrets in Git.
NO guessed external-storage path.
```

If existing destination-side Llama work is already running, do not interfere with it from this source-export task.

## Completion

Before commit:

1. verify no existing scientific evidence changed;
2. verify no unrelated decouple-L1/L2 files changed;
3. verify no bulk artifact or secret is staged;
4. review every uncommitted source item classified `COMMIT_REQUIRED`;
5. ensure all unknowns are explicit rather than guessed.

Then commit and push this branch and stop.

Final report must include:

```text
branch and final commit
changed files
GIT_REQUIRED count
STORAGE_REQUIRED count and total bytes
REBUILD_OR_VERIFY_ON_DEST count
SOURCE_RETAIN count
UNKNOWN_PROVENANCE count/list
uncommitted source review summary
which R5 raw/profiler artifacts require preservation
which historical 3090 subset is recommended for destination availability
whether existing model assets appear already handed off (only if verifiable)
whether any GPU workload was launched for this migration task
explicit confirmation that no source evidence was deleted/moved/rewritten
exact recommended first command/stage for the destination Docker
```

Do not continue into destination acceptance or cleanup in the same task.