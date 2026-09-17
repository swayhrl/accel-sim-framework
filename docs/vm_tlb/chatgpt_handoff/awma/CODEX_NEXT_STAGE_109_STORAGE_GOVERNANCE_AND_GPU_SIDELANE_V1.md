# CODEX_NEXT_STAGE_109_STORAGE_GOVERNANCE_AND_GPU_SIDELANE_V1

Node: 109 / RTX4080
Mode: Goal / long-running / solve-and-continue
Status: ACTIVE

Stage:

```text
AWMA_STORAGE_GOVERNANCE_AND_GPU_CAPTURE_SIDELANE_V1
```

This stage has two sequential phases:

```text
Phase A: storage governance and node164 data-plane qualification
Phase B: bounded simulator-native capture side lane for already-selected Qwen2.5 targets
```

Phase B is forbidden until Phase A reaches:

```text
AWMA_164_DATA_PLANE_QUALIFIED_V1
```

Do not disturb the concurrently active 174-new Q05 translation-timeline stage.

---

## 0. Read first

Fetch coordination branch:

```text
hrl/awma-storage-governance-gpu-sidelane-handoff-v1
```

Read in order:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/STORAGE_GOVERNANCE_POLICY_V1.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
this file
```

Accepted parent for 109 target selection:

```text
branch = hrl/awma-kernel-target-selection-109-v1
HEAD   = e90fd76d3704df4a367bb04de09aee42d0cab803
status = AWMA_KERNEL_TARGET_SELECTION_V1_COMPLETE_WITH_SCOPE
```

Create a fresh execution branch/worktree from that accepted commit.

Recommended:

```text
hrl/awma-storage-governance-capture-sidelane-109-v1
```

Do not modify the frozen producer branch in place.

Accepted simulator-native producer authority remains:

```text
5143b4e10aaf2fc47bb60492155d2464b0b726fd
```

If the execution branch's producer source differs from this accepted source, compare exact source hashes/diff. Use a clean producer worktree at the accepted producer authority for capture rather than silently changing producer semantics.

---

# Phase A — Storage Governance

## A0. Preflight and no-delete audit

Record:

```text
109:
  df -h
  relevant /data/c16 usage
  current capture/staging roots
  GPU lock state

174-new via ssh hrl174new:
  df -h
  mount information for /root/share/mnt164
  durable root existence

node164 durable root:
  /root/share/mnt164/huangrulin/c16_ai_workload/
```

Confirm the role contract:

```text
109 = producer + temporary local staging
174-new = analysis/simulator, not large-data authority
164 = durable large-data authority
```

Do not delete or relocate accepted scientific artifacts during this stage.

## A1. Audit/reuse existing data-plane code before adding new code

Search the repository for existing C16/AWMA data-plane utilities, schemas and receipts.

Prefer reusing/extending accepted utilities over creating a parallel second transfer system.

Required functional capabilities, whether existing or newly added:

```text
finalize capture
publish/resume partial transfer
independent destination verify
no-overwrite admission
transfer receipt / ACK
catalog entry generation
quarantine on mismatch
```

If code is needed, prefer a shared role-neutral location such as:

```text
util/vm_tlb/c16/data_plane/
```

Do not create host-specific duplicate implementations unless unavoidable.

## A2. Durable namespace policy

Do not mass-move historical data.

Preserve existing accepted Q05 producer path under node164 `raw/`.

For new publication, use the policy in:

```text
STORAGE_GOVERNANCE_POLICY_V1.md
```

Recommended transfer staging:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/captures/inbox/<RUN_ID>.partial
```

Recommended accepted raw destination remains compatible with existing producer authority:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/raw/<RUN_ID>
```

If current accepted tooling already uses another safe durable subpath, preserve it and document the mapping rather than performing disruptive path surgery.

## A3. 1-2 GiB end-to-end storage canary

Create one deterministic 1-2 GiB fixture on 109 local disk.

Test:

```text
109 source
 -> ssh hrl174new
 -> /root/share/mnt164/.../captures/inbox/...partial
```

The test must prove:

1. destination can contain a partial prefix;
2. transfer resumes rather than restarting blindly;
3. final source/destination byte counts match;
4. source SHA256 equals destination SHA256;
5. promotion/rename on node164 succeeds;
6. read-back SHA after promotion still matches;
7. test fixture is removed only after all previous checks PASS.

Do not route the 1-2 GiB fixture through 174-new local disk.

Generate a receipt with:

```text
source path
partial path
final test path
bytes
source sha256
destination sha256
resume evidence
rename evidence
read-back evidence
cleanup evidence
```

Required success marker:

```text
AWMA_164_DATA_PLANE_QUALIFIED_V1
```

If this cannot be closed safely:

```text
STOP_STORAGE_DATA_PLANE_NOT_QUALIFIED
```

and do not start Phase B.

## A4. Storage catalog bootstrap

Create or update deterministic storage catalog support.

Do not recursively rehash unrelated historical multi-terabyte trees.

At minimum index, without moving:

```text
1. accepted Q05 simulator-native trace bundle
2. Q05 natural-completion simulator raw evidence
3. accepted S2 full kernel-launch inventory
4. Qwen2.5 frozen model/input authority references
```

Reuse accepted manifest/hash roots when they already exist.

Each entry must include at least:

```text
artifact/run identity
artifact type
scientific status
model/revision/scenario/phase/target when applicable
producer node
source/durable path
size
sha256 or accepted manifest/hash root
Git report/review-pack reference
retention class
```

Generate a deterministic human-readable snapshot, e.g. TSV/JSON.

## A5. Cleanup candidate report only

Audit obvious large AWMA copies on 109 and 174-new and classify them as:

```text
AUTHORITATIVE
DURABLE_ACCEPTED
WORKING_COPY
LEGACY_DURABLE
SAFE_TO_DELETE_AFTER_ACK
UNKNOWN
```

Do not delete any accepted or working scientific data in this stage.

Only the storage-canary fixture may be deleted automatically after PASS.

## Phase A deliverables

Review pack section must include:

```text
STORAGE_LAYOUT.md
DATA_PLANE_CANARY_RECEIPT.json
STORAGE_CATALOG.tsv
STORAGE_CATALOG_SCHEMA.md
CURRENT_LARGE_ARTIFACT_INDEX.tsv
CLEANUP_CANDIDATES.tsv
DATA_PLANE_SOURCE_DIFF.md
```

Phase A must close before any new large capture.

---

# Phase B — GPU Capture Side Lane

Phase B starts only after `AWMA_164_DATA_PLANE_QUALIFIED_V1`.

This phase is authorized because target selection is already accepted and node109's GPU is currently idle. It is independent of the still-active Q05 translation-timeline analysis on 174-new.

This phase produces **producer-qualified durable capture bundles only**.

It does NOT:

- create SIM_INPUT IDs;
- run Accel-Sim;
- change the current Q05 mechanism conclusions;
- start TLB/PTW sweeps;
- claim cross-kernel scientific generalization.

## B0. GPU lock and workload identity

Before each GPU run:

```text
check /data/c16/locks/c16_gpu_campaign.lock
confirm RTX4080 is not used by another formal campaign
```

Do not interrupt another formal GPU task.

Frozen workload identity:

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT
batch      = 1
input      = frozen TEXT binding
prefill    = 2048
decode     = 32
dtype      = FP16
backend    = SDPA
```

Do not retokenize another text, change dtype/backend/context/batch, or substitute a different model revision.

## B1. Candidate identity requalification

Accepted candidates are navigation/selection authorities from:

```text
e90fd76d3704df4a367bb04de09aee42d0cab803
CANDIDATE_STATUS.json
```

They are currently `CANDIDATE_ONLY_NOT_CAPTURED`.

Requalify each candidate in a fresh exact frozen workload run using the accepted producer's lightweight listing/selection path before formal tracing.

Scientific identity must bind:

```text
frozen workload
phase
decode step where applicable
exact kernel function
grid
block
deterministic occurrence within phase/function/shape
```

The historical `reference_launch_index` is only a navigation aid. Never use global launch number alone as scientific identity.

Authorized candidates, priority order:

### P0 — PREFILL_GEMM_PRIMARY_1

```text
phase = PREFILL
function = cutlass::Kernel2<cutlass_80_tensorop_f16_s16816gemm_relu_f16_256x128_32x3_tn_align8>
grid = 128,3,1
block = 256,1,1
occurrence within phase/function/shape = 12
reference launch = 285  # navigation only
```

Selection importance:

```text
57.31% Prefill GEMM-family GPU time
38.10% total Prefill GPU time
```

### P0 — DECODE_GEMV_PRIMARY_1

```text
phase = DECODE
decode_step = 1
function family exact string from CANDIDATE_STATUS.json: internal::gemvx ... int6
grid = 1216,1,1
block = 16,4,1
occurrence within phase/function/shape = 10
reference launch = 1244  # navigation only
```

Selection importance:

```text
1,536 recurrences across 32 steps
40.64% Decode GEMV-family time
20.22% total Decode GPU time
```

### P1 — DECODE_FLASH_PRIMARY_1

```text
phase = DECODE
decode_step = 1
exact function = flash_fwd_splitkv_kernel<...>
grid = 1,9,14
block = 128,1,1
occurrence within phase/function/shape = 17
reference launch = 1748  # navigation only
```

Selection importance:

```text
82.10% Decode Flash GPU time
```

### P1 — DECODE_FLASH_PRIMARY_2

```text
phase = DECODE
decode_step = 1
exact function = flash_fwd_splitkv_combine_kernel<...>
grid = 2,1,1
block = 128,1,1
occurrence within phase/function/shape = 0
reference launch = 1018  # navigation only
```

Selection importance:

```text
17.90% Decode Flash GPU time
```

Do not capture the secondary `grid=18992,1,1 / block=8,8,1` GEMV in this stage. Keep it in the backlog only.

If any candidate cannot be deterministically requalified:

```text
IDENTITY_NOT_CLOSED
```

Skip only that candidate and continue to the next authorized candidate. Do not guess.

## B2. Capture feasibility canary and guard

For each identity-qualified candidate, run a bounded producer canary before the formal whole-kernel capture.

Canary goals:

```text
selected kernel is actually instrumented
terminal protocol behaves correctly
no immediate parser/formatter regression
estimate output growth / elapsed capture time
```

Canary is DIAGNOSTIC and may not be promoted as a formal trace if incomplete.

Whole-target guard:

```text
per candidate durable bundle cap = 8 GiB
time cap per capture attempt      = 30 minutes
aggregate new durable raw cap     = 32 GiB
```

If a guard is reached before clean completion:

```text
BOUNDED_PARTIAL_NOT_FORMAL
```

Preserve the diagnostic receipt only if useful; do not admit it as a complete trace.

Do not relax terminal/parser/grammar rules merely to make a candidate fit the guard.

## B3. Formal simulator-native producer capture

For each candidate passing B1/B2, perform a fresh-process whole selected-kernel simulator-native capture using the accepted producer lifecycle.

Required producer-side closure:

```text
exact target identity receipt
terminal = COMPLETE
nonzero scientific data
no drop
overflow = 0
mode-2/base_delta = 0
accepted formatter/trace grammar checks PASS
manifest closes all members
all member sizes/hashes close
```

Do not reintroduce legacy NVBit lifecycle code.

Do not use C16WARP1/Native memory trace as a substitute for simulator-native instruction trace.

If a new SASS form exposes a true semantic/contract gap that would require weakening the frozen trace grammar or inventing an operand/address/width:

```text
STOP_FOR_SCIENTIFIC_REVIEW
```

Do not fake fields.

## B4. Publish immediately through the newly qualified data plane

After each producer bundle closes locally:

```text
109 ready
 -> node164 .partial
 -> independent destination verify
 -> durable promotion
 -> receipt / ACK
 -> mark local copy transferred
```

Do not delete the 109 producer copy in this stage.

Each accepted durable bundle must receive:

```text
RUN/CAPTURE identity
source manifest hash
member hash root
durable path
destination independent verify receipt
storage catalog entry
```

No large raw file is committed to Git.

## B5. Side-lane completion statuses

Per candidate use one of:

```text
PRODUCER_CAPTURE_COMPLETE_DURABLE
IDENTITY_NOT_CLOSED
BOUNDED_PARTIAL_NOT_FORMAL
CAPTURE_CONTRACT_BLOCKED
```

Overall stage may complete even if one candidate is skipped/blocked, provided all statuses are explicit and no invalid partial data is promoted.

No SIM_INPUT admission is required in this stage.

---

# Shared engineering policy

Routine engineering problems are solve-and-continue:

- Python/script defects;
- path handling;
- rsync/resume plumbing;
- manifest/catalog formatting;
- source navigation;
- deterministic occurrence resolution;
- Git/worktree transport;
- bounded disk-space handling.

Stop only if continuing requires changing:

- frozen workload identity;
- selected target semantic identity;
- accepted producer trace semantics;
- terminal/drop/overflow admission rules;
- trace grammar by weakening or fabrication;
- existing accepted durable data;
- another formal campaign's GPU lock.

---

# Required deliverables

Create review pack:

```text
docs/vm_tlb/review_packs/AWMA_STORAGE_GOVERNANCE_GPU_SIDELANE_109_V1/
```

and report:

```text
docs/vm_tlb/codex_handoff/awma/STORAGE_GOVERNANCE_GPU_SIDELANE_109_V1_REPORT.md
```

At minimum review pack contains:

```text
README.md
SOURCE_ANCHORS.md
STORAGE_LAYOUT.md
DATA_PLANE_CANARY_RECEIPT.json
STORAGE_CATALOG.tsv
CURRENT_LARGE_ARTIFACT_INDEX.tsv
CLEANUP_CANDIDATES.tsv
CANDIDATE_CAPTURE_STATUS.tsv
TARGET_IDENTITY_RECEIPTS/
CAPTURE_RECEIPTS/
RAW_DATA_INDEX.tsv
RUN_RECEIPTS.json
SHA256SUMS
```

Update `codex_handoff/LATEST_REPORT.md` if that file is used by the current AWMA handoff convention.

Large data remain on node164.

---

# Final completion marker

Print:

```text
AWMA_STORAGE_GOVERNANCE_GPU_SIDELANE_V1_COMPLETE_WITH_SCOPE
```

and report separately:

```text
storage_data_plane = QUALIFIED | NOT_QUALIFIED

PREFILL_GEMM_PRIMARY_1 = ...
DECODE_GEMV_PRIMARY_1 = ...
DECODE_FLASH_PRIMARY_1 = ...
DECODE_FLASH_PRIMARY_2 = ...
```

Then:

```text
review pack
-> report
-> hashes
-> commit
-> push
-> remote verify
-> git status clean
-> STOP
```

Do not automatically start:

- SIM_INPUT admission for these new captures;
- Accel-Sim replay of these new captures;
- NCU campaigns;
- C16WARP1 campaigns;
- Qwen3/DeepSeek capture;
- TLB/PTW mechanism experiments.
