# CODEX NEXT STAGE — 174-new Local Storage Audit V1

## Status

ACTIVE after reading the coordination handoff.

Stage:

```text
AWMA_174NEW_LOCAL_STORAGE_AUDIT_V1
```

Node:

```text
174-new / port 2239
```

This stage is **read-only inventory + cleanup-candidate classification only**.
It must not delete, move, compress, prune, garbage-collect, or rewrite accepted scientific data, repositories, worktrees, simulator outputs, caches, or node164 durable artifacts.

The objective is to answer quantitatively:

1. What is actually consuming local/host-backed storage visible from 174-new?
2. Which large paths are active/reproducibility-critical and must stay?
3. Which large paths are merely working copies/caches/build products?
4. Which local copies have independently verified durable equivalents on node164?
5. How much space could be released later under a separate explicitly authorized cleanup stage?

## Coordination branch

Read from:

```text
hrl/awma-174-local-storage-audit-handoff-v1
```

Read first:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/STORAGE_GOVERNANCE_POLICY_V1.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
```

Then execute this file only.

## Relationship to existing tracks

Current relevant state:

```text
Track A — Q05 translation timeline
COMPLETE / report received

Track C — node109 producer storage governance + GPU side lane
ACTIVE

Track D — node174 durable-consumer audit
WAITING_FOR_PRODUCER_CANARY after completing its independent existing-data audit
```

This new stage is Track E and is independent of Track C's producer capture progress.

Do not modify Track C or Track D worktrees.
Do not wait for the producer canary in order to inventory local storage.

## Frozen storage role

```text
109 = GPU producer + short-lived staging
174-new = simulator / analysis / worktree host, NOT durable large-data authority
164 = durable large-data authority
```

Node164 mount/root:

```text
/root/share/mnt164
/root/share/mnt164/huangrulin/c16_ai_workload/
```

Node164 contents must not be counted as 174-new local usage.

## D0 — Mount topology and scope

First establish the exact filesystem topology from inside 174-new.

Capture at least:

```text
hostname
uname -a
df -hT
findmnt -T /
findmnt -T /root/data if present
findmnt -T /root/share if present
findmnt -T /root/share/mnt164
mount entries relevant to /root, /root/data, /root/share, /root/share/mnt164
```

Classify each visible filesystem/mount as one of:

```text
CONTAINER_LOCAL_OR_OVERLAY
HOST_BACKED_LOCAL
NODE164_REMOTE_DURABLE
OTHER_REMOTE_OR_EXTERNAL
UNKNOWN
```

Important:

- Do not infer ownership from path names alone.
- `/root/share/mnt164` is explicitly node164 remote durable storage and must be excluded from local-capacity totals.
- If `/root/share` or `/root/data` are host-backed local mounts, inventory them separately from the overlay so totals are not double-counted.
- If multiple paths expose the same underlying filesystem/device, report one physical capacity and separate logical path usage.

Output:

```text
MOUNT_TOPOLOGY.txt
FILESYSTEM_SCOPE.tsv
```

## D1 — Read-only top-level usage inventory

For every filesystem classified as local/host-backed local, perform a read-only usage inventory without crossing into other mounts.

Prefer tools/flags such as:

```text
du -x
--one-file-system
find -xdev
```

where appropriate.

Do not recursively traverse node164 while computing local usage.

At minimum identify top consumers under relevant roots such as:

```text
/root
/root/workspace
/root/data
/root/share
/tmp
/var/tmp
/var/cache
/root/.cache
```

but use mount topology to avoid duplicate accounting.

Produce at least:

```text
TOP_LOCAL_PATHS.tsv
```

with columns similar to:

```text
filesystem_id
path
bytes
human_size
category_guess
notes
```

Report at least the largest 50 local paths/directories, with enough depth to explain the dominant storage consumers rather than only one top-level aggregate.

## D2 — Large-file inventory

Identify large local files without crossing filesystem boundaries.

Default reporting thresholds:

```text
>= 1 GiB: list individually
>= 256 MiB: summarize counts/bytes by parent category
```

If there are too many entries, retain complete raw listing outside Git only if necessary and commit deterministic summaries.

Output:

```text
LARGE_LOCAL_FILES.tsv
LARGE_FILE_SUMMARY.tsv
```

For each >=1 GiB item include where obtainable:

```text
path
size
mtime
filesystem_id
owner
category
related run/branch if recognizable
node164 counterpart status
classification
```

Do not hash every large file merely for completeness. Hash only when needed to establish a cleanup-candidate relationship to an accepted node164 durable artifact and when the cost is bounded.

## D3 — Git repository and worktree audit

Inventory the AWMA/Accel-Sim repository/worktree footprint visible from 174-new.

At minimum record:

```text
repo/worktree path
size
branch
HEAD
clean/dirty
active/inactive role if provable
build-output size
untracked-large-data size where detectable
```

Explicitly protect:

- current accepted/frozen baseline worktrees;
- active Track C/D/E worktrees;
- worktrees associated with accepted evidence whose reproducibility depends on local-only generated build/tool state unless a source-backed rebuild path is proven;
- any dirty worktree;
- old174/shared research worktrees unrelated to AWMA unless separately proven disposable.

Output:

```text
WORKTREE_STORAGE.tsv
```

No `git worktree remove`, `git clean`, `git gc`, `git repack`, reset, prune, or build cleanup is authorized.

## D4 — Classify storage by retention semantics

Classify meaningful local consumers using these statuses:

```text
KEEP_ACTIVE
KEEP_REPRODUCIBILITY
KEEP_SHARED_OTHER_PROJECT
WORKING_COPY
CACHE_REGENERABLE
BUILD_REGENERABLE
DUPLICATE_VERIFIED_ON_164
SAFE_CANDIDATE_AFTER_ACK
UNKNOWN_REVIEW_REQUIRED
DO_NOT_TOUCH
```

A path may be marked `DUPLICATE_VERIFIED_ON_164` only when all of the following are established:

```text
known scientific/artifact identity
node164 durable path exists
size closes
accepted manifest/hash/receipt closes the durable copy
local copy is not the only source of uncommitted metadata or provenance
```

Do not mark something safe based only on same/similar filename.

A cache/build directory may be marked regenerable only if the source/toolchain required to rebuild it is identified or the cache is conventional and not a scientific artifact.

## D5 — Specific AWMA local-vs-164 checks

Cross-check the major AWMA artifacts already known to be durable on node164:

```text
accepted Q05 simulator-native trace
Q05 natural-completion simulation raw
Q05 translation-timeline raw
S2 full kernel inventory / census raw
```

Determine whether 174-new holds any additional local copy of those artifacts and its size.

If yes, classify the local copy using evidence above.
If no, record `NO_LOCAL_DUPLICATE_FOUND`.

Also check for large local directories matching or related to:

```text
awma
c16
tlb
trace
traceg
simulation
replay
telemetry
nvbit
nsys
ncu
```

This is navigation only; classification must use content/provenance, not names alone.

## D6 — Cleanup candidate report; NO deletion

Produce:

```text
CLEANUP_CANDIDATES.tsv
CLEANUP_SUMMARY.md
```

`CLEANUP_CANDIDATES.tsv` should contain at least:

```text
path
bytes
classification
node164_counterpart
verification_basis
risk
proposed_action_if_later_authorized
estimated_reclaimable_bytes
```

`CLEANUP_SUMMARY.md` must report separately:

```text
local/host-backed physical filesystems and free space
largest consumers
bytes that are definitely KEEP
bytes classified as candidate but require explicit later authorization
bytes under UNKNOWN_REVIEW_REQUIRED
conservative reclaimable estimate
upper-bound reclaimable estimate
```

The conservative reclaimable estimate may include only high-confidence categories such as:

```text
DUPLICATE_VERIFIED_ON_164
CACHE_REGENERABLE
BUILD_REGENERABLE
```

provided no active/dirty worktree or scientific-authority conflict exists.

The upper-bound estimate may include additional working copies, but must not be presented as safe-to-delete.

## D7 — Local-only authority check

Write:

```text
LOCAL_ONLY_AUTHORITY_CHECK.md
```

Explicitly answer:

1. Is any accepted AWMA large scientific artifact known to exist only on 174-new local/host-backed storage?
2. Is any local path the sole known copy of an uncommitted scientific manifest/receipt/raw dataset?
3. Are there dirty worktrees containing large uncommitted scientific outputs?
4. Are there large UNKNOWN paths that prevent a safe cleanup decision?

If any accepted/local-only authority is found, mark it `DO_NOT_TOUCH` and surface it prominently.

## D8 — Safety rules

Strictly forbidden in this stage:

```text
rm / unlink / rmdir
mv of scientific or worktree data
compression to replace originals
git clean
git gc / prune / repack
git worktree remove
package/cache purge
docker prune or container cleanup
truncation
changing symlinks
mass chmod/chown
rewriting historical node164 paths
```

Do not delete even files classified as safe candidates.

The only permitted writes are:

- small audit outputs/review-pack/report files;
- normal Git commits for those audit outputs;
- bounded temporary files required by audit tooling, removed only if they are created by this stage and have no scientific content.

## D9 — Deliverables

Report:

```text
docs/vm_tlb/codex_handoff/awma/
LOCAL_STORAGE_AUDIT_174NEW_V1_REPORT.md
```

Review pack:

```text
docs/vm_tlb/review_packs/
AWMA_LOCAL_STORAGE_AUDIT_174NEW_V1/
```

Required minimum files:

```text
README.md
MOUNT_TOPOLOGY.txt
FILESYSTEM_SCOPE.tsv
TOP_LOCAL_PATHS.tsv
LARGE_LOCAL_FILES.tsv
LARGE_FILE_SUMMARY.tsv
WORKTREE_STORAGE.tsv
CLEANUP_CANDIDATES.tsv
CLEANUP_SUMMARY.md
LOCAL_ONLY_AUTHORITY_CHECK.md
GIT_STATE.txt
SHA256SUMS
```

If a complete raw `du/find` listing is large, keep it outside Git or omit it; commit the deterministic summaries only.

## Completion marker

```text
AWMA_174NEW_LOCAL_STORAGE_AUDIT_V1_COMPLETE_WITH_SCOPE
```

Completion means:

```text
read-only inventory complete
+ cleanup candidates classified
+ no deletion performed
+ report/review pack/hash closure
+ commit/push/remote verify
+ worktree clean
+ STOP
```

Do not automatically execute cleanup. A separate ChatGPT-issued cleanup stage is required after review.
