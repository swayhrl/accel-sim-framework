# C16 NVBit 1.7.5 recovery campaign — Llama first, then all remaining models

## 0. Purpose

The previous multi-model attempt produced a truthful blocker closeout, but it did **not** complete the scientific trace-acquisition goal. This handoff reopens that goal with two corrections:

1. the historical six-window diagnostic budget remains immutable evidence, but it must **not** permanently forbid a newly authorized scientific capture campaign; and
2. “asset unavailable” must only be declared after a broader, evidence-backed repository/server asset-recovery pass, not merely after scanning `/root/autodl-tmp/c16_retry570`.

The execution order is deliberate:

```text
FIRST: finish Llama formal target capture end-to-end
THEN: recover/freeze assets for Qwen/DeepSeek/GLM and finish every remaining model
```

Use Goal mode. Do not stop after producing another blocker pack if the next bounded recovery step is available.

### Active branch/checkpoint

```text
repo:   swayhrl/accel-sim-framework
branch: hrl/vm-c16-g-retry570-v0
base:   556ab6ca39425cf1c7642db6f1327594309071b3
```

### Evidence inherited and accepted

Infrastructure qualification remains valid:

```text
NVBit                   1.7.5
GPU/SM                  RTX3090 / SM86
driver                   570.124.04
CUDA                     12.4
PyTorch                  2.5.1+cu124
effective module loading EAGER
Q0 runtime/prewarm       PASS
Q1 tiny real capture     PASS x2
Q2 trace schema/lifecycle PASS
```

The previous Llama S0/S1/S2 evidence is also accepted **if its hashes and frozen identities still validate**:

```text
model      meta-llama/Llama-3.2-1B
revision   4e20de362430cd3b72f300e6b0f18e50e7166e08
workload   S0/B1/T128/Decode4/TEXT
target     full mangled indexSelectLargeIndex
NVBit1.7.5 authoritative target range [101,102)
opcode     LDG.E.U16
historical ordinal 34 excluded
historical candidate 348 not reused
S1 full-model no-trace runtime PASS
S2 static-map / target requalification PASS
```

Do not redo S0/S1/S2 merely for ritual. Revalidate hashes/receipts, then continue at Llama S3.

---

## 1. Budget semantics correction — do not mutate history

### Historical ledger is immutable

The six consumed `NVBIT` windows under historical deployment

```text
c16_llama32_1b_frozen_compatible
```

must remain unchanged. Do not delete, reset, rewrite, reclassify, or decrement those entries.

### New user authorization

This handoff is a **new explicit user-authorized scientific/recovery campaign**. It therefore gets a new ledger/deployment namespace instead of inheriting the exhausted diagnostic namespace.

Use a new campaign scope, e.g.:

```text
campaign_id: c16_nvbit175_multimodel_recovery_v2
```

and model-specific deployment IDs such as:

```text
c16_nvbit175_recovery_llama32_1b_v1
c16_nvbit175_recovery_qwen_0p5_v1
c16_nvbit175_recovery_qwen_7b_awq_v1
c16_nvbit175_recovery_deepseek_v1
c16_nvbit175_recovery_glm_v1
```

Do not reuse the old exhausted deployment ID for new scientific capture.

### Authorized bounded capture windows

The user authorizes:

- up to **8 NVBit capture windows for Llama S3-S5 recovery**;
- after Llama is complete, up to **8 NVBit capture windows per additional model** after that model's S0-S2 qualification succeeds.

These are campaign-scoped windows. They are not permission for broad debugging or 300-second “wait and see” experiments.

Use the minimum windows needed. Typical expectation:

```text
S3 canary                  1
S4 independent repro       1-2
S5 complete prefill/decode 1-2
bounded repair reruns       remaining reserve
```

Metadata-only inventory, hash validation, source-only fixes, and no-GPU asset discovery do not consume a capture window. A GPU/NVBit process that enters the formal capture path does.

Every window must be ledgered under the new deployment/campaign namespace.

---

# PART A — Llama must be completed first

## L0. Revalidate inherited evidence

Before creating the first new capture lease, verify without rerunning S1/S2 unless required:

- exact model path exists;
- model revision/config/package/token receipt hashes match the prior closeout;
- known-good runtime profile matches;
- NVBit 1.7.5 archive/core/tool hashes match;
- S1 receipt/hash exists and says full-model no-trace PASS;
- S2 static-map receipt/hash exists;
- target function equals the full mangled identity retained in the prior closeout;
- authoritative static range is exactly `[101,102)` and opcode `LDG.E.U16`;
- current disk free space satisfies campaign storage policy;
- no stale GPU/diagnostic process;
- `MEASUREMENT_ACTIVE` absent.

If any inherited artifact fails hash validation, repair/reconstruct the smallest affected evidence. Do not silently fall back to ordinal 34 or 348.

## L1. Create the new Llama recovery deployment/lease scope

Create a new campaign/deployment ledger entry without altering historical rows.

The new scope must record:

```text
parent_historical_deployment = c16_llama32_1b_frozen_compatible
historical_rows_preserved = true
new_campaign = c16_nvbit175_multimodel_recovery_v2
new_deployment = c16_nvbit175_recovery_llama32_1b_v1
authorization = user-approved recovery capture
max_nvbit_capture_windows = 8
```

Add focused tests proving that the implementation cannot mutate the historical ledger while permitting the new namespace.

## L2. Llama S3 — narrow formal capture canary

Use:

```text
model/revision: frozen Llama identity above
workload:       B1/T128/Decode4/TEXT
NVBit:          1.7.5
loading:        EAGER
target:         exact full mangled indexSelectLargeIndex
static range:   [101,102)
opcode:         LDG.E.U16
```

Protocol:

```text
process start
 -> validate identity/runtime
 -> zero-trace prewarm
 -> READY
 -> assert trace_file_count == 0
 -> acquire NEW recovery lease
 -> create MEASUREMENT_ACTIVE
 -> CAPTURE_BEGIN
 -> one narrow target occurrence/window
 -> CAPTURE_END
 -> remove measurement marker / finish lease
 -> parse/validate
 -> cleanup
```

Require:

- target record count > 0;
- address-bearing memory rows > 0;
- exact function/range binding;
- no prewarm trace;
- parser/schema PASS;
- final newline/truncation guard PASS;
- normal process exit;
- post-run GPU/diagnostic count 0;
- `MEASUREMENT_ACTIVE` absent.

If S3 fails, diagnose the smallest capture-specific boundary. Do not reopen NVBit 1.8 or discard the validated `[101,102)` mapping without contrary evidence.

## L3. Llama S4 — independent reproducibility

Run the same narrow canary in at least one additional independent process.

Require agreement in:

- exact model/revision/input contract;
- target full function identity;
- static range `[101,102)`;
- schema/header;
- phase/ROI identity;
- structural record-count expectations.

Raw addresses and raw trace SHA may differ across processes because process-local addresses/context differ.

## L4. Llama S5 — complete frozen workload target capture

After S3/S4 PASS, capture all required occurrences of `[101,102) LDG.E.U16` over the complete frozen B1/T128/Decode4 workload.

Required phase coverage:

```text
PREFILL
DECODE step 1
DECODE step 2
DECODE step 3
DECODE step 4
```

Prefer explicit per-phase files or a sidecar that unambiguously maps each captured target occurrence to phase/decode step.

Do not declare full capture after decode1 only.

Before S5:

1. estimate output size from S3/S4;
2. record free bytes;
3. require projected output + margin to fit;
4. set a formal external timeout based on measured canary/model runtime, not an arbitrary unlimited wait.

A reasonable supervisor policy is:

```text
target cap = max(60 s, predicted_capture_wall * 4 + 30 s), capped at 300 s
remote transaction cap = target cap + cleanup/copy metadata allowance
local SSH cap = remote cap + connection allowance
```

This is a formal capture timeout, not the retired NVBit-1.8 long-watch diagnostic.

## L5. Llama S6 — scientific capture closeout

Generate a dedicated Llama recovery pack containing:

- inherited S0/S1/S2 provenance;
- new budget-scope authorization receipt;
- S3 canary receipt;
- S4 reproducibility matrix;
- S5 prefill/decode-step capture summary;
- target function/static-range receipt;
- parser/schema/address validation;
- raw artifact index;
- remote SHA -> local transfer -> local SHA closure;
- storage accounting;
- final manifest + validation receipt.

Raw traces remain outside Git.

### Mandatory Llama success status

Do not proceed to the remaining models until either:

```text
LLAMA_FULL_TARGET_TRACE_COMPLETE
```

or a genuinely technical/global blocker exists after using the new recovery scope.

`LEGACY_BUDGET_EXHAUSTED` is no longer an acceptable Llama blocker under this authorization.

---

# PART B — recover and complete every remaining model

Begin only after Llama S6 is complete.

## R0. Broad asset/identity recovery — metadata only

The prior scan only proved that the required assets were absent under `/root/autodl-tmp/c16_retry570`. That is insufficient for a final `ASSET_UNAVAILABLE` claim.

Perform a bounded metadata-only inventory over the following **existing** roots when present:

```text
/root/autodl-tmp
/root/autodl-fs
/root/.cache/huggingface
$HF_HOME
$TRANSFORMERS_CACHE
$HUGGINGFACE_HUB_CACHE
/workspace
/data
```

Also search repository/current Git history and retained project metadata for exact model identifiers/revisions using targeted queries around:

```text
qwen
0.5
7b
awq
deepseek
glm
model_id
model_revision
snapshot
config.json
```

Use bounded metadata operations (`config.json`, manifests, refs, snapshot paths, package receipts, file sizes/hashes). Do not import weights or start GPU work during R0.

Do not scrape shell history or expose credentials/tokens.

### Required R0 outcome per model

One of:

```text
IDENTITY_AND_LOCAL_ASSET_RECOVERED
IDENTITY_RECOVERED_ASSET_MISSING
IDENTITY_UNRESOLVED
```

Do not collapse these states into one generic “asset unavailable.”

## R1. Controlled exact-asset acquisition is now allowed

This handoff **overrides the previous blanket no-download rule**, but only under strict conditions.

If and only if an exact model identity/revision has been recovered from authoritative project evidence and the local asset is missing, Codex may acquire that exact asset from its authoritative upstream source.

Rules:

- no variant guessing;
- no “closest” replacement;
- no automatic smaller model;
- no quantization/dtype substitution;
- pin exact revision/commit when available;
- download into a dedicated campaign cache/package path;
- record source identity, revision, file list/size, and hashes;
- verify disk capacity before download;
- do not overwrite an existing frozen asset;
- deterministic token IDs are preferred when a tokenizer is not scientifically required;
- if access is gated/auth unavailable, classify `BLOCKED_ASSET_FETCH_AUTH_REQUIRED` and continue other models.

If exact identity remains unresolved after the bounded repository/server recovery, do not invent one. Classify `BLOCKED_IDENTITY_UNRESOLVED_REQUIRES_USER` and continue the rest.

## R2. Per-model scientific workflow after identity/asset freeze

For each remaining model in order:

```text
Qwen 0.5-class target
Qwen 7B AWQ target
DeepSeek target
GLM target
```

use the same model-local sequence:

```text
S0 exact identity/input/runtime freeze
S1 full-model no-trace runtime/prewarm
S2 NVBit1.7.5 target function + static memory range requalification
S3 narrow real capture canary
S4 independent reproducibility
S5 complete frozen-workload target capture (prefill + all frozen decode steps)
S6 model closeout + SHA closure
```

Each model gets its own new recovery deployment namespace and up to 8 authorized NVBit capture windows after S0-S2 are qualified.

### Static range rule

Never reuse Llama `[101,102)` or any ordinal/range from another model without direct same-binary requalification evidence.

Each model must produce its own:

```text
full mangled target identity
static memory instruction ordinal/range
opcode/memory type
address-bearing proof
```

## R3. Model fit/runtime problems

If a recovered exact model cannot run under the frozen RTX3090/PyTorch/CUDA contract:

- first diagnose whether the **existing authoritative project contract** already specifies quantization/offload/backend behavior;
- use that exact contract if present;
- do not invent a new scientific workload just to make it fit;
- if the authoritative frozen model genuinely cannot fit this node, classify `BLOCKED_RUNTIME_WITH_FROZEN_IDENTITY` with memory/runtime evidence and continue other models.

---

# PART C — final cross-model completion

After all five models have been processed, publish a new recovery campaign pack. Do not overwrite or erase the previous blocked-attempt pack; link it as superseded campaign-attempt evidence.

Final matrix fields:

```text
MODEL
EXACT_IDENTITY
ASSET_SOURCE
WORKLOAD_CONTRACT
RUNTIME_READY
TARGET_FULL_IDENTITY
STATIC_RANGE
PREFILL_RECORDS
DECODE1_RECORDS
DECODE2_RECORDS
DECODE3_RECORDS
DECODE4_RECORDS (when applicable)
TOTAL_RECORDS
ADDRESS_RECORDS
TRACE_BYTES
REPRODUCIBLE
REMOTE_LOCAL_SHA_CLOSED
FINAL_STATUS
BLOCK_REASON
```

### Final success preference

The intended end state is:

```text
C16_NVBIT175_MULTIMODEL_RECOVERY_CAMPAIGN_COMPLETE
```

A blocked-model ending is acceptable only for blockers that remain after the expanded asset/identity recovery and permitted exact-asset acquisition.

---

## 2. Hard global invariants

Never change these silently:

```text
NVBit 1.7.5
CUDA 12.4
driver 570.124.04
PyTorch 2.5.1+cu124
effective loading EAGER
qualified Lane G tracer lineage
measurement-window protocol
raw-trace SHA closure discipline
```

Never mutate historical ledger rows.

Never commit raw traces to Git.

Never allow prewarm trace pollution.

Never abandon the whole Goal because one later model is blocked; continue the others unless a global invariant fails.

---

## 3. Required final report

Lead with Llama first:

```text
RECOVERY_CAMPAIGN_STATUS=
RECOVERY_CAMPAIGN_COMMIT=
PUBLISH_MANIFEST_SHA256=

LLAMA_STATUS=
LLAMA_NEW_DEPLOYMENT_ID=
LLAMA_S3_CANARY=PASS/FAIL
LLAMA_S4_REPRO=PASS/FAIL
LLAMA_TARGET_FUNCTION=
LLAMA_STATIC_RANGE=
LLAMA_PREFILL_RECORDS=
LLAMA_DECODE1_RECORDS=
LLAMA_DECODE2_RECORDS=
LLAMA_DECODE3_RECORDS=
LLAMA_DECODE4_RECORDS=
LLAMA_TOTAL_TRACE_BYTES=
LLAMA_SHA_CLOSED=

QWEN_0P5_STATUS=
QWEN_0P5_EXACT_IDENTITY=
QWEN_0P5_ASSET_SOURCE=
QWEN_0P5_TARGET=
QWEN_0P5_STATIC_RANGE=
QWEN_0P5_PREFILL_RECORDS=
QWEN_0P5_DECODE_RECORDS=

QWEN_7B_AWQ_STATUS=
QWEN_7B_AWQ_EXACT_IDENTITY=
QWEN_7B_AWQ_ASSET_SOURCE=
QWEN_7B_AWQ_TARGET=
QWEN_7B_AWQ_STATIC_RANGE=
QWEN_7B_AWQ_PREFILL_RECORDS=
QWEN_7B_AWQ_DECODE_RECORDS=

DEEPSEEK_STATUS=
DEEPSEEK_EXACT_IDENTITY=
DEEPSEEK_ASSET_SOURCE=
DEEPSEEK_TARGET=
DEEPSEEK_STATIC_RANGE=
DEEPSEEK_PREFILL_RECORDS=
DEEPSEEK_DECODE_RECORDS=

GLM_STATUS=
GLM_EXACT_IDENTITY=
GLM_ASSET_SOURCE=
GLM_TARGET=
GLM_STATIC_RANGE=
GLM_PREFILL_RECORDS=
GLM_DECODE_RECORDS=

ALL_SUCCESSFUL_TRACES_SHA_CLOSED=
MEASUREMENT_WINDOWS_CLEAN=
TOTAL_RAW_TRACE_BYTES=
ACTIVE_GPU_PROCESS_COUNT=
ACTIVE_DIAGNOSTIC_PROCESS_COUNT=
MEASUREMENT_ACTIVE_AFTER_CAMPAIGN=
BLOCKED_MODELS=
```

Then give per-model review-pack paths, test counts, manifests, and any precise blocker evidence.
