# C16 Full-Authority Recovery V3 — Stage Acceptance Gates

This document defines objective exit criteria for every recovery-v3 stage. A stage is not complete because a command exited 0; it is complete only when its evidence contract is satisfied.

The local/control-host large-data placement contract is defined in `C16_RECOVERY_V3_LOCAL_STORAGE_LAYOUT.md`. Large campaign data must use `/root/share/c16_recovery_v3`; `/workspace` remains for code and compact Git metadata.

## R0 — Authority / matrix reconciliation

### Required work

- Read and reconcile current C16 Master, Lane-A, Lane-G, Lane-C, Lane-H contracts.
- Build the authoritative model/scenario matrix from `C16_FULL_AUTHORITY_RECOVERY_V3_MATRIX.json` plus any stricter active-repo evidence.
- Import accepted checkpoints without rerunning them.

### PASS criteria

- `R0_AUTHORITY_MATRIX.tsv` exists.
- Every model row is tagged `C16_AUTHORITATIVE` or `USER_EXTENSION`.
- Every scenario is tagged `REQUIRED`, `CANARY_ONLY`, `OPTIONAL_IF_STABLE`, or `NOT_APPLICABLE`.
- Llama S0 points to accepted commit `2e955e...` and is `INHERITED_COMPLETE`, not scheduled for rerun.
- Missing Qwen7 raw / Qwen3 rows from the prior reduced campaign are restored.
- No model/scenario is silently dropped.

### FAIL / recovery

If contracts conflict, preserve the stricter scientific constraint and document the conflict. Do not ask the user unless the conflict changes model identity or scientific intent in a way that cannot be resolved from project authority.

---

## R1 — Exact identity + asset recovery

### Required work per deployment

Freeze:

```text
model_id/package_id
revision/content manifest
config hash
tokenizer/input contract
weight format
quantization
dtype/backend expectation
asset byte count
per-file manifest
```

Before any large local fetch, complete the local storage preflight from `C16_RECOVERY_V3_LOCAL_STORAGE_LAYOUT.md` and create:

```text
/root/share/c16_recovery_v3/models
/root/share/c16_recovery_v3/hf-cache
/root/share/c16_recovery_v3/staging
/root/share/c16_recovery_v3/raw
/root/share/c16_recovery_v3/receipts
```

### PASS criteria

One of:

- `IDENTITY_AND_ASSET_LOCAL_HASH_CLOSED`
- `IDENTITY_RECOVERED_READY_FOR_EXACT_FETCH`

and:

```text
LOCAL_BULK_ROOT=/root/share/c16_recovery_v3
LOCAL_BULK_WRITABLE=PASS
LOCAL_BULK_FILESYSTEM_SEPARATE_FROM_CONSTRAINED_ROOT=PASS
```

For `READY_FOR_EXACT_FETCH`, Codex must continue to fetch/transfer; it is not a terminal blocker.

### Required recovery attempts before any terminal exception

1. repo current metadata;
2. git history;
3. retained package manifests/receipts;
4. bounded local/control-host asset roots including `/root/share/c16_recovery_v3`;
5. bounded GPU-host roots;
6. authoritative upstream metadata;
7. network-capable local-host exact-revision fetch under `/root/share/c16_recovery_v3` + transfer.

### Nonrecoverable terminal exceptions

- `USER_ACTION_GATED_ACCESS`
- `IDENTITY_UNRESOLVED_AFTER_AUTHORITY_SEARCH`

These are allowed only with a receipt listing every source searched and the exact missing fact/action.

---

## R2 — Package transfer + runtime preflight

### Required work

- Keep local model/cache/staging files under `/root/share/c16_recovery_v3`.
- Copy exact assets from local/control host to GPU host if not already present.
- Rehash all required files on both sides.
- Validate known-good runtime/toolchain.
- Validate free disk / VRAM before model load.

### PASS criteria

```text
MODEL_ASSET_HASH_MATCH=PASS
INPUT_RECEIPT_HASH_MATCH=PASS
NVBIT_VERSION=1.7.5
EFFECTIVE_MODULE_LOADING=EAGER
NVDISASM_CHILD_PATH=PASS
GPU_IDENTITY=PASS
STALE_GPU_PROCESSES=0
MEASUREMENT_ACTIVE=ABSENT
CAPTURE_ALLOWED=YES
LOCAL_BULK_ROOT=/root/share/c16_recovery_v3
LOCAL_BULK_WRITABLE=PASS
ROOT_FS_NOT_USED_FOR_LARGE_ASSET_STAGING=PASS
```

### Recovery

- GPU-host upstream network failure must trigger local-host exact fetch under `/root/share` + rsync, not a blocker.
- PATH/runtime problems use the hardened preflight/bootstrap and focused tests.
- Disk pressure triggers rolling local copyback/remote cleanup of already-closed artifacts.
- Local root-disk pressure must never trigger a fallback large download/copy into `/workspace`; repair placement/cache settings instead.

---

## R3 — Native baseline + lightweight census

### Required work per deployment/scenario

1. warmup + unprofiled measured baseline under the authoritative scenario;
2. output/checksum/terminal correctness;
3. no CPU fallback unless the deployment contract explicitly includes it;
4. lightweight kernel census with phase/NVTX linkage when available;
5. runtime implementation audit.

### PASS criteria

- workload completes under frozen model/scenario;
- actual token counts are recorded;
- output/checksum stable across required repeats;
- device/backend/dtype/quantization match the frozen identity;
- `KERNEL_CATALOG.tsv` or equivalent is complete for prefill/decode ROI;
- phase launch counts are explicit;
- semantic coverage gaps remain explicit UNKNOWN rather than guessed;
- profile perturbation is measured/labeled if profiled duration is retained.

### Resource skip

`SKIPPED_RESOURCE` is allowed only after identity-preserving remedies fail and an evidence receipt proves the frozen scenario cannot fit the available resource. Continue all other rows.

---

## R4 — Target-plan freeze

### Required work

- Search for a valid existing C-lane target plan matching the exact deployment/scenario.
- If absent, generate a deterministic recovery-v3 plan from the frozen R3 census.
- Separate prefill and decode targets.
- Preserve special semantics/certainty-like units when visible: KV management, router/dispatch, E/O, rare implementation, heavy duration mass.

### PASS criteria

- `TARGET_PLAN.tsv/json` is versioned and SHA frozen **before** any formal NVBit capture.
- Every row has:
  - deployment/scenario/phase;
  - full kernel/function identity or second-pass validation key;
  - semantic/shape/dtype key;
  - selection reason;
  - expected capture cost;
  - target role.
- plan is immutable after first formal capture; changes require a new version.
- no cross-model static ordinal reuse.

### Minimum diversity

For each deployment with both prefill and decode, the plan must not collapse to a single phase-only kernel if census shows distinct major behaviors. At least one qualified target per active phase and relevant target class must be represented, subject to bounded budget.

---

## R5 — NVBit static map + canary + reproducibility

### Required work per selected target class

1. direct NVBit 1.7.5 static instruction map;
2. select address-bearing memory instruction/range;
3. canary capture;
4. independent-process reproducibility capture.

### PASS criteria

For launched targets:

```text
FULL_FUNCTION_IDENTITY=CLOSED
STATIC_RANGE=CLOSED
OPCODE/MEMORY_SPACE=CLOSED
HAS_ADDRESS_RECORDS=true
CANARY_RECORDS>0
REPRO_RECORDS>0
SCHEMA_VALIDATION=PASS
PREWARM_TRACE_COUNT=0
MEASUREMENT_WINDOW_CLEAN=PASS
```

Raw trace SHA equality is not required between independent processes because addresses/context may differ. Structural identity/range/schema/phase contract must agree.

### Structural zero

Zero is accepted only when an independent census proves the exact target did not launch in that phase. Then use `STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED` and, if the plan requires that phase, discover/requalify the actual phase-specific target.

---

## R6 — Formal bounded capture

### Required work

Capture every frozen target-plan row required for the deployment/scenario over the complete selected ROI/step coverage.

### PASS criteria

- one capture process on GPU at a time;
- each window obeys <=4 GiB or <=20 min bound;
- phase/step attribution is retained;
- target second-pass identity validation succeeds immediately before capture;
- expected launched targets have records;
- output/checksum unchanged;
- parser/schema/truncation guards pass;
- storage estimate and free-space gate passed before start, including projected local copyback capacity under `/root/share`.

### Partial bound handling

If bound hits, retain `BOUNDED_PARTIAL`, copy it back and keep going. Retry only if a smaller scientifically equivalent window is explicitly permitted by the frozen plan.

---

## R7 — Immediate local copyback + SHA closure

### Required work

After each successful/partial raw capture or large profiler/census payload:

1. remote size + SHA256;
2. transfer to local/control host under `/root/share/c16_recovery_v3`;
3. local size + SHA256;
4. equality check;
5. append local raw-artifact index;
6. only then allow remote raw deletion for space reclamation.

### PASS criteria

- `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0` for the row;
- every required raw/large payload has local path, remote SHA, local SHA, equality=true;
- every large required local path resolves under `/root/share/c16_recovery_v3`;
- local artifact root is durable and indexed;
- raw traces are outside Git;
- `ROOT_FS_LARGE_PAYLOAD_LEAK_COUNT=0` for newly generated recovery-v3 payloads.

### Mandatory behavior

Do not defer all copyback until the end. Use rolling copyback so network/disk problems surface early and remote space remains available.

Do not use `/workspace`, `/tmp`, or `/root/.cache` as overflow storage for large recovery-v3 data.

---

## R8 — Per-deployment/scenario publication

### Required work

Publish compact Git review packs for each completed deployment/scenario.

### PASS criteria

Pack contains or links:

- exact identity receipt;
- input/scenario receipt;
- runtime/preflight receipt;
- native baseline/census summaries;
- target plan + hash;
- static map/target receipts;
- canary/repro matrix;
- formal capture summary;
- raw-artifact local/remote SHA index with `/root/share` local paths;
- cleanup receipt;
- limitations / resource skips.

Manifest validator must prove:

```text
all payloads exist
size matches
SHA256 matches
no duplicate path
raw trace not committed to Git
```

Wave-1 checkpoint publication must occur before Wave-2 completes so downstream lanes can consume it.

---

## R9 — Cross-model final dataset / integrity closeout

### Required work

Create a unified local dataset index with one row per:

```text
deployment × scenario × phase × target/window
```

Fields include:

```text
model identity/revision
wave/authority role
scenario
actual tokens
phase/decode step
target semantic class
full function identity
static range
opcode/memory space
launch count
record count
address-record count
trace bytes
local raw path
raw SHA256
capture status
evidence commit
limitation
```

### PASS criteria

- all successful raw files are locally SHA closed;
- all required large local raw paths resolve under `/root/share/c16_recovery_v3`;
- `ALL_REQUIRED_RAW_UNDER_LOCAL_BULK_ROOT=true`;
- `ROOT_FS_LARGE_PAYLOAD_LEAK_COUNT=0`;
- final report records `/root/share` and root-filesystem free bytes;
- no blocked/skipped row is represented as zero-valued scientific data;
- Llama inherited S0 and newly generated S1–S4 rows are distinguished;
- Qwen raw vs AWQ remain separate deployment identities;
- phase-dependent targets remain separate;
- final manifest validation passes;
- GPU and diagnostic process counts are zero;
- `MEASUREMENT_ACTIVE` absent;
- `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0`;
- active branch pushed;
- final report lists every required model/scenario with COMPLETE / BOUNDED_PARTIAL / SKIPPED_RESOURCE / true user-action exception.

Preferred final status:

```text
C16_FULL_AUTHORITY_RECOVERY_V3_DATASET_COMPLETE
```

If exceptions remain, terminal wording must identify them without claiming the missing rows are scientific measurements.
