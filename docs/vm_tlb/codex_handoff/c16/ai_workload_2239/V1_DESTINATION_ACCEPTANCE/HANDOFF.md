# C16 AI Workload 2239 Destination Acceptance — V1 Handoff

## 0. Purpose

This branch accepts the new destination Docker as the primary execution environment for future AI-workload memory characterization, NVBit trace collection, NCU profiling, Cache/TLB analysis, and later AI-workload-driven architecture studies.

This is **not** a retirement of the source Docker. The source Docker remains active for decouple-L1, L2, and other GPU-memory-architecture work.

V1 performs destination admission only. It does not authorize a new broad AI workload campaign.

---

## 1. Authority chain

Repository:

```text
https://github.com/swayhrl/accel-sim-framework.git
```

Destination acceptance branch:

```text
hrl/c16-ai-workload-2239-destination-acceptance-v1
```

Source-export authority:

```text
branch: hrl/c16-ai-workload-2233-to-2239-handoff-v0
commit: 9db359a41d41568b572dc7b6f0147bcf98a280b9
```

RTX4080 clean Llama scientific boundary:

```text
branch: hrl/c16-4080-u5-u9-r5-clean
commit: b75f26674a09705659e770ab2134351414aa3c93
status: READY_FOR_MULTIMODEL_REVIEW
R4: MECHANISM_ONLY_NON_AUTHORITATIVE
```

RTX3090 historical closeout authority remains separate:

```text
branch: hrl/vm-c16-g-3090-campaign-closeout-v0
commit: 649af1b9d65a774d4aa8c32a15f9b6f4da0dd4d9
```

Do not merge RTX3090 and RTX4080 authority.

---

## 2. Long-term responsibility split

### Source Docker

Retain for:

```text
decouple-L1
L2
other GPU memory microarchitecture work
source-side historical evidence that has not yet been copy-closed
```

### Destination Docker

Primary future environment for:

```text
AI workload characterization
Llama and later multi-model workloads
NVBit trace collection
NCU profiling
Cache/TLB workload analysis
AI workload memory-behavior studies
later AI-workload-driven optimization
```

### External storage

Use as the long-term data plane for large assets after its actual destination mount is discovered and admitted.

Git remains the control plane for code, scripts, manifests, receipts, provenance, and analysis summaries.

Do not put model weights, large raw traces, `.ncu-rep`, `.nsys-rep`, or equivalent bulk payloads in Git.

---

## 3. V1 objective

V1 must establish a destination receipt proving what the destination actually has.

The required gates are:

1. Git identity and clean working tree.
2. Destination host/container/GPU identity.
3. Actual external storage mount, writable scratch location, filesystem type, and free capacity.
4. Exact Llama model admission for revision `4e20de362430cd3b72f300e6b0f18e50e7166e08`, or an explicit FAIL/BLOCKED result.
5. Frozen-input admission, including the existing four-hash contract; do not invoke a tokenizer to recreate inputs.
6. Runtime identity: Python, PyTorch, CUDA runtime/toolkit, transformers, attention backend assumptions, and GPU residency policy.
7. NVBit 1.7.5 / tracer identity verification or explicit rebuild-required state.
8. NCU identity/version/permission state, without launching broad profiling.
9. Read-only reconciliation of any already-present R5/U8/N1 artifacts against the source-export manifest.
10. A storage namespace plan for future AI workload data.

A destination environment may be accepted as a **new independently recorded environment** even if some package versions differ from the historical 4080 R5 source environment. In that case, record the difference explicitly and do not claim binary/runtime equivalence.

---

## 4. Important source-export facts

Read before admission:

```text
docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V0_SOURCE_EXPORT/SOURCE_STATE.md
docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V0_SOURCE_EXPORT/ARTIFACT_TRANSFER_MANIFEST.tsv
docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V0_SOURCE_EXPORT/STORAGE_TRANSFER_PLAN.md
docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V0_SOURCE_EXPORT/UNKNOWN_PROVENANCE.md
docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V0_SOURCE_EXPORT/MIGRATION_SUMMARY.json
```

Key current boundaries:

```text
RTX4080 R5 = READY_FOR_MULTIMODEL_REVIEW
R4 quantitative data = non-authoritative
RTX4080 N1 NCU report/CSV = receipt-bound but source path was inaccessible to source-export container
RTX4080 U8 NVBit raw root = manifest-bound but source path was inaccessible to source-export container
RTX4080 R5 U5/U6/U9 raw/static-map/stdout = UNKNOWN_PROVENANCE until path+SHA receipt is located
exact Llama asset on destination = not yet proven by source-export
frozen input payload path on destination = not yet proven by source-export
RTX3090 minimum comparison subset = about 763,868,911 bytes, comparison-only, not required for destination admission
```

Do not convert any UNKNOWN_PROVENANCE item to PASS from summary text alone.

---

## 5. Destination storage admission

Do not assume any historical path such as `/data/c16` exists or has the same meaning.

Discover the actual destination-visible storage mounts using non-destructive commands. Record only what is scientifically useful:

```text
mount path
filesystem type
read/write capability
total capacity
free capacity
ownership/permissions needed by this Docker
```

Do not commit private network topology, passwords, tokens, SSH keys, or unrelated host inventory.

A temporary read/write test is allowed only inside a newly created migration scratch directory on the selected external mount. Create a small file, hash it, read it back, then remove that temporary test file. This is not scientific evidence.

Recommended logical namespace after mount admission:

```text
<EXTERNAL_AI_ROOT>/
├── models/
├── inputs/
├── runtime/
├── tools/
├── raw/
│   ├── rtx4080/
│   └── rtx3090_history/
├── profiler/
│   ├── ncu/
│   └── nsys/
├── manifests/
├── analysis/
└── scratch/
```

Do not physically migrate large source data in V1.

---

## 6. Model admission

The destination may already contain the model, but presence must be proven rather than assumed.

Required identity:

```text
model: meta-llama/Llama-3.2-1B
revision: 4e20de362430cd3b72f300e6b0f18e50e7166e08
```

Use existing Git admission scripts/receipts where applicable. Verify repository/snapshot identity and immutable model metadata/files sufficient to bind the local asset to that exact revision.

Do not silently redownload, update, retokenize, or replace model files during admission.

If a full-byte model hash closure is impractical or no prior manifest exists, record exactly which immutable file hashes/metadata are used and classify the admission strength.

Allowed result states:

```text
EXACT_ASSET_ADMISSION_PASS
PRESENT_BUT_IDENTITY_NOT_CLOSED
MISSING
BLOCKED
```

---

## 7. Frozen input admission

Use the frozen input contract already referenced by the 4080 migration code.

Do not regenerate token IDs from the text with a tokenizer.

Locate the existing payloads if present and verify the four expected hashes from the existing admission logic/receipt.

Allowed result states:

```text
FROZEN_INPUT_ADMISSION_PASS
PARTIAL_PRESENT
MISSING
BLOCKED
```

---

## 8. Runtime/toolchain admission

Record destination reality rather than inheriting source claims.

At minimum record:

```text
Python version
PyTorch version
torch.version.cuda
CUDA toolkit / nvcc
nvdisasm
transformers
GPU model
GPU UUID
compute capability
CUDA_VISIBLE_DEVICES policy
CUDA_MODULE_LOADING
relevant PATH / LD_LIBRARY_PATH closure
NVBit version/archive/core library identity if present
tracer source/binary hash if present
NCU version and binary hash if practical
```

Do not commit secrets or broad environment dumps containing credentials.

If destination runtime differs from R5 source runtime, mark:

```text
NEW_DESTINATION_RUNTIME_NON_EQUIVALENT_TO_R5
```

That does not fail V1 by itself. It only means future measurements require a new destination scientific receipt rather than inheriting R5 runtime equivalence.

---

## 9. GPU non-interference gate

The destination may already be running Llama tests.

Before any optional GPU diagnostic:

1. inspect current GPU process/activity state;
2. do not kill, pause, attach to, or alter existing processes;
3. if another workload is active, do not launch a diagnostic and record `GPU_DIAGNOSTIC_DEFERRED_ACTIVE_WORKLOAD`;
4. never use `pkill`, broad process cleanup, reset, or driver manipulation.

V1 does not require a model rerun.

A tiny standalone CUDA/NVBit/NCU fixture is optional only if the GPU is idle and it can be run without disturbing any existing work. If run, it is capability admission only, not scientific workload evidence.

No broad Llama/NVBit/NCU capture is authorized in V1.

---

## 10. Read-only artifact reconciliation

Search only reasonable destination-visible data roots; do not recursively crawl unrelated host filesystems.

Try to locate the already-known receipt-bound objects:

```text
N1 NCU report SHA256 d2e97a920a998d76f14902d21e3d71b6e23d11ad00cf2eed797b4b0758e07102
N1 CSV SHA256 372ee15d20bc6ac44a5178b23e7cbc350d8890e10f354689c76ac87ffcb56d17
U8 NVBit raw-root FINAL_SHA256SUMS manifest SHA256 6c801de25d08a58bf04f8ef6a5349665bfeb3ee6d99e28795e530d935cb30f8e
```

If found, verify read-only and record their destination paths.

For R5 U5/U6/U9 raw/static-map/stdout, require an existing path+SHA receipt or manifest. Do not promote files based only on naming similarity.

Do not copy or move them in V1.

---

## 11. Required V1 outputs

Create:

```text
docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V1_DESTINATION_ACCEPTANCE/RESULTS/
```

At minimum:

```text
DESTINATION_STATE.md
DESTINATION_RECEIPT.json
STORAGE_ADMISSION.json
MODEL_ADMISSION.json
FROZEN_INPUT_ADMISSION.json
RUNTIME_TOOLCHAIN_ADMISSION.md
ARTIFACT_RECONCILIATION.tsv
OPEN_ISSUES.md
V1_DECISION.json
```

`V1_DECISION.json` must end in exactly one of:

```text
DESTINATION_ACCEPTED_FOR_STORAGE_IMPORT_AND_BOUNDED_CANARIES
DESTINATION_ACCEPTED_WITH_NON_EQUIVALENT_RUNTIME
DESTINATION_BLOCKED_MODEL_OR_INPUT_IDENTITY
DESTINATION_BLOCKED_STORAGE
DESTINATION_BLOCKED_TOOLCHAIN
DESTINATION_BLOCKED_OTHER
```

If multiple issues exist, choose the strongest blocking state and list all issues in `OPEN_ISSUES.md`.

---

## 12. Hard prohibitions

```text
NO source evidence deletion/move/rewrite.
NO bulk source-to-destination migration in V1.
NO 3090 full recovery-root copy.
NO RTX3090/RTX4080 authority merge.
NO broad Llama rerun for admission.
NO broad NVBit trace campaign.
NO broad NCU profiling campaign.
NO profiler attachment to an already-running workload.
NO process killing/reset/driver changes.
NO tokenizer-based regeneration of frozen input.
NO silent model redownload/update.
NO secrets/private keys/tokens/passwords in Git.
NO unnecessary private network inventory in Git.
NO large raw/model/profiler payloads in Git.
NO promotion of UNKNOWN_PROVENANCE from filenames or PASS summaries alone.
```

---

## 13. Stop condition

After the V1 reports are generated:

1. self-review them;
2. commit and push this destination-acceptance branch;
3. stop;
4. report for review;
5. do not start storage import, 3090 subset copy, or a new AI workload campaign without a later handoff.
