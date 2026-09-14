# C16 AI-workload analysis handoff V0

## 0. Purpose

This handoff separates the ongoing C16 AI-workload memory-analysis line from the source Docker workspace and moves its future execution to a second Docker workspace on the same RTX4080 node.

The source Docker is **not retired**. It remains active for other architecture work, including decouple-L1, L2, and related GPU-memory-system research. The destination Docker becomes the primary execution environment for AI workload characterization, NVBit/NCU tracing, Cache/TLB workload analysis, and later AI-workload-oriented optimization studies.

This document defines a **non-destructive, provenance-preserving migration**. Git is the control plane for code/docs/manifests. Large models, raw traces, profiler reports, and other bulky artifacts must stay outside Git and be managed through hash-closed storage manifests.

Connection addresses, credentials, SSH keys, tokens, and private infrastructure details must not be committed to this repository.

---

## 1. Working branch and source authorities

Working branch:

```text
hrl/c16-ai-workload-2233-to-2239-handoff-v0
```

This branch is based on the current clean RTX4080 Llama authority:

```text
branch: hrl/c16-4080-u5-u9-r5-clean
commit: b75f26674a09705659e770ab2134351414aa3c93
status: READY_FOR_MULTIMODEL_REVIEW
```

The existing RTX4080 R5 state remains authoritative for its own campaign boundary:

```text
U5 PASS
U6 PASS
U7 PASS
U8.5 PASS
U9 PASS
R4 quantitative data remains mechanism-only / non-authoritative
```

Historical RTX3090 Route-B evidence remains a separate frozen campaign. Its closeout inventory authority is referenced, not merged into RTX4080 authority:

```text
branch: hrl/vm-c16-g-3090-campaign-closeout-v0
commit: 649af1b9d65a774d4aa8c32a15f9b6f4da0dd4d9
```

Underlying immutable RTX3090 authorities remain exactly as already recorded by that closeout package.

Do not reinterpret, merge, or overwrite scientific authority across RTX3090 and RTX4080 campaigns.

---

## 2. Workspace responsibility split

### Source Docker

The source Docker remains active and is not a deprecated environment.

Primary responsibilities after migration:

```text
decouple-L1
L2 / shared-L2 architecture work
GPU memory-system architecture development
other non-AI-workload C16 work as explicitly assigned
```

During migration it additionally acts as the **source-of-record for any AI-workload code/docs/assets that have not yet been safely handed off**.

It must retain original evidence until copy/verification closure is complete.

### Destination Docker

The destination Docker becomes the primary workspace for:

```text
AI workload characterization
Llama and future multi-model workload runs
NVBit trace collection
NCU profiling
Cache/TLB-oriented workload analysis
AI workload memory-footprint/reuse/page behavior analysis
future AI-workload-oriented architecture optimization experiments
```

The destination has access to a larger external storage server. Exact hostnames, mount paths, credentials, and access details are environment-local information and must be discovered and recorded in local receipts, not hard-coded into public repository files.

### Shared rule

The two Docker workspaces may share Git history but must not share undocumented mutable local state as scientific evidence.

Every scientific run must be attributable to:

```text
Git commit
runtime/environment receipt
model/input identity
GPU identity
capture tool identity
raw artifact path
raw artifact hash/size
analysis producer commit
```

---

## 3. Migration object classes

Every AI-workload artifact found during migration must be classified into exactly one of the following classes.

### GIT_REQUIRED

Small, reviewable, reproducibility-critical material that belongs in Git, for example:

```text
Python/shell analysis and capture scripts
NVBit tool source and build glue owned by this project
NCU wrapper scripts
parsers and summarizers
frozen experiment configuration files
schema definitions
small JSON/CSV receipts
manifests
handoff documents
scientific closeout summaries
```

Do not commit generated bulk data merely because it is text.

### STORAGE_REQUIRED

Large or generated scientific assets that must be available to the destination but must not be committed to Git, for example:

```text
model snapshots / model weights
raw NVBit traces
raw JSONL traces
.ncu-rep
.nsys-rep
large profiler CSV exports
large static/disassembly dumps when generated
large recovery datasets
wheel/archive payloads when already reproducibly hash-identified
```

These require size + SHA256 + provenance + source path + destination path/status in a transfer manifest.

### REBUILD_OR_VERIFY_ON_DEST

Machine/runtime state that must not be blindly copied as authority:

```text
CUDA-visible GPU binding
NVIDIA driver
CUDA toolkit executables
Python environment
PyTorch runtime libraries
NVBit extracted/build tree
NCU installation
LD_LIBRARY_PATH/PATH state
container runtime/mount layout
```

The destination may reuse bytes only when exact hashes and compatibility are verified. Otherwise rebuild/reinstall and produce a new destination receipt.

### SOURCE_RETAIN

Evidence or project material that should remain in the source Docker even if a copy is made elsewhere. Original scientific evidence is copy-not-move until explicitly retired under a later reviewed plan.

### EXCLUDE_SECRET_OR_HOST_PRIVATE

Never commit or transfer through Git:

```text
SSH private keys
API tokens
credentials
private host inventory not required for scientific reproduction
shell history
personal configuration
unrelated project data
```

---

## 4. V0 migration boundary

V0 is a **source-side inventory and Git handoff preparation stage**.

V0 does not authorize deleting or moving source files and does not authorize changing existing scientific conclusions.

V0 does not require stopping or modifying any already-running destination-side RTX4080 experiment.

V0 must not launch a new GPU experiment solely for migration bookkeeping.

Allowed V0 work:

```text
inspect Git/worktree state
inventory AI-workload-owned files
identify unpushed/uncommitted reproducibility-critical code
classify migration objects
hash normal-sized source assets
reuse already-closed hashes for very large scientific assets when authoritative receipts exist
prepare Git export list
prepare external-storage transfer manifest/plan
prepare destination acceptance checklist
prepare source-retain list
record unknown provenance
commit small reproducibility-critical material
push the migration branch
```

Forbidden in V0:

```text
delete source evidence
move source evidence
rewrite raw evidence
change frozen RTX3090 authority
change frozen RTX4080 R5 authority
mix RTX3090 and RTX4080 evidence as one campaign
git-add model weights or raw profiler/trace payloads
commit secrets or private keys
invent destination storage paths
re-run Q1/Q2/Route-A for migration
re-run R5 merely to create migration receipts
launch broad new NCU/NVBit campaigns as part of migration
```

---

## 5. V0 required deliverables

Create a new directory:

```text
docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V0_SOURCE_EXPORT/
```

At minimum produce:

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

### SOURCE_STATE.md

Record:

```text
current branch/HEAD used for inventory
relevant worktrees
AI-workload code roots
current RTX4080 authority references
current RTX3090 closeout reference
known local raw/model roots without exposing secrets
whether each root is Git-tracked, local-only, or external-storage-backed
```

### GIT_EXPORT_LIST.txt

List every reproducibility-critical file that the destination must obtain through Git.

The list should prefer existing canonical paths rather than copying files into duplicate migration directories.

### GIT_UNCOMMITTED_REVIEW.md

Audit uncommitted/local-only AI-workload code on the source workspace. For each item classify:

```text
COMMIT_REQUIRED
ALREADY_SUPERSEDED
LOCAL_DEBUG_ONLY
UNRELATED_TO_AI_WORKLOAD
UNKNOWN_REVIEW_REQUIRED
```

Do not blindly commit the whole worktree.

### ARTIFACT_TRANSFER_MANIFEST.tsv

Use at least these fields:

```text
artifact_id
class
campaign
gpu
role
source_path
size_bytes
sha256
hash_basis
source_authority
required_on_destination
destination_path
transfer_status
notes
```

For very large assets whose bytes have an existing authoritative closed hash, `hash_basis` may state that receipt. Do not silently recompute or substitute a different file.

### STORAGE_TRANSFER_PLAN.md

Separate at minimum:

```text
A. already present on destination
B. must be copied from source
C. can be reconstructed/downloaded from immutable identity
D. historical 3090 data needed only for cross-platform comparison
E. not required for destination continuation
```

Prefer external storage for future raw data. New destination scientific runs should write to a documented external-storage campaign root when practical, with local scratch treated as disposable only after hash/copy closure.

### SOURCE_RETAIN_LIST.md

Explicitly record what remains on the source Docker and why. Source retention is expected, because the source Docker continues decouple-L1/L2 and may also contain original historical authority.

### DESTINATION_ACCEPTANCE_CHECKLIST.md

Destination acceptance must include at least:

```text
pull exact migration commit
clean Git status / isolated worktree
record GPU UUID/model/driver
record CUDA/Python/PyTorch/Transformers/NVBit/NCU identities
verify external storage access and free space
verify model asset identity/hash/revision
verify frozen input/token identities
verify required scripts are present from Git
verify raw/output roots are distinct from source authority
verify no secret/private path was imported into Git
verify current R5 authority files resolve
run CPU-only parser self-checks first
only then run a separately authorized bounded GPU smoke/canary if scientifically needed
```

A destination environment passing this checklist becomes a **new recorded execution environment**, not a transparent continuation of source-local state.

---

## 6. RTX3090 historical data handling

The RTX3090 campaign is now an historical frozen dataset for later comparison/analysis.

Use the closeout inventory at commit:

```text
649af1b9d65a774d4aa8c32a15f9b6f4da0dd4d9
```

as the starting manifest for determining what historical raw/derived material may be useful on the destination.

Do not bulk-copy the entire ~75 GB recovery endpoint by default.

First select the minimal comparison/re-analysis subset needed for future AI workload Cache/TLB work, while preserving the original closeout manifest and authority. Any copy must be copy-not-move and SHA-verified.

The unresolved 3090 CUTLASS identity rows remain unresolved. Destination RTX4080 data must not be used to retroactively repair them.

---

## 7. RTX4080 data handling after migration

The current clean Llama R5 result is already an accepted 4080 campaign boundary. Preserve it.

Future destination runs should use a clean campaign layout that separates:

```text
00_manifest
01_raw
02_static_maps
03_profiler_reports
04_derived
05_analysis
06_logs
07_docs
```

Raw data and profiler reports remain outside Git; manifests, small receipts, analysis code, and summary products go to Git when appropriate.

Do not treat runtime GPU addresses or a static target from RTX3090 as cross-GPU identity. Each new model/runtime campaign must record its own target mapping.

---

## 8. Recommended migration sequence

```text
M0: source inventory and classification                <- this V0
M1: commit/push all approved GIT_REQUIRED material
M2: destination pulls exact commit
M3: destination storage/model/runtime acceptance
M4: copy only required historical/bulk assets with SHA closure
M5: destination bounded AI-workload smoke/canary
M6: freeze destination baseline and make it the default AI-workload lane
M7: later review source-side duplicate cleanup separately
```

Do not collapse M0-M7 into one opaque migration.

---

## 9. Stop conditions

Stop and report instead of improvising if:

```text
scientific authority conflicts
an uncommitted file cannot be classified
required bytes exist only in an unknown location
source and destination copies differ in SHA
large data would need to be committed to Git to proceed
an external-storage path is uncertain
migration would require deleting source evidence
RTX3090 and RTX4080 provenance become mixed
GPU execution is required merely to establish file provenance
```

---

## 10. V0 completion report

At V0 completion report:

```text
branch
final commit
all new/modified Git files
number of GIT_REQUIRED items
number and bytes of STORAGE_REQUIRED items
number of REBUILD_OR_VERIFY_ON_DEST items
all UNKNOWN_PROVENANCE items
all uncommitted source items reviewed
which model assets are already present on destination, if independently verifiable
which 3090 historical assets are recommended for later transfer
which 4080 R5 raw/report artifacts require storage preservation
whether any GPU workload was launched for migration
whether any source evidence was deleted/moved/rewritten
recommended exact next step for destination acceptance
```

After commit/push, stop. Do not start destructive cleanup.