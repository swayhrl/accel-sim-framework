# C16 Multi-model NVBit 1.7.5 full trace campaign handoff

## 0. Goal

This handoff converts the now-qualified Lane G tracing infrastructure into a **complete multi-model trace acquisition campaign**.

The goal is no longer to prove that NVBit can start or that a tiny trace can be produced. Those gates are already closed. The goal is to collect the entire set of traces required by the current AI-workload/TLB-cache study, across every required model that is actually available under a frozen local identity, while preserving exact runtime/model/input provenance and measurement isolation.

This is a goal-mode task: continue through all stages and all models unless a hard invariant would be violated. A failure in one model must not automatically abort unrelated models; close that model as blocked with evidence and continue the remaining campaign.

### Active qualified checkpoint

```text
repo:   swayhrl/accel-sim-framework
branch: hrl/vm-c16-g-retry570-v0
base:   d001a349156c51aa6de15f30b9aedaa70f534442
status: NVBIT_RETRY570_NVBIT175_MINIMAL_CAPTURE_QUALIFIED_STOP_FOR_REVIEW
```

### Infrastructure facts that are CLOSED

- RTX3090 / SM86
- driver 570.124.04
- CUDA toolkit 12.4
- nvcc 12.4.131
- nvdisasm 12.4.127
- PyTorch 2.5.1+cu124
- NVBit 1.7.5
- effective CUDA module loading: EAGER
- Q0 runtime/prewarm gate: PASS
- Q1 minimal deterministic capture: PASS twice
- Q2 trace schema/lifecycle validation: PASS
- Q1 record count: 7360 in both independent processes
- Q1 prewarm trace count: 0
- measurement window clean
- no residual GPU process / no residual MEASUREMENT_ACTIVE

NVBit 1.8 is not part of this campaign. Do not spend campaign time re-debugging it.

---

## 1. What “full trace campaign” means

“Full” does **not** mean unbounded tracing of every instruction of every CUDA kernel in a model. That would destroy storage/runtime practicality and is not the current scientific contract.

For each model, the complete required capture consists of:

1. frozen model/runtime/input identity;
2. no-trace runtime/prewarm proof;
3. complete kernel census / target re-binding under NVBit 1.7.5;
4. authoritative target function identity and static instruction/range mapping for that model/version;
5. a narrow capture canary;
6. an independent reproducibility capture;
7. complete capture of **all occurrences of the requalified target memory instruction/range over the full frozen workload window**;
8. phase attribution at least to prefill vs decode, and decode-step attribution where the frozen workload exposes it;
9. parser/schema/address-coverage validation;
10. remote SHA -> local transfer -> local SHA closure;
11. compact Git publication containing metadata/manifests/receipts, but not raw trace payloads.

The target instruction/range must be requalified per model. Never assume that a static ordinal from Llama or from NVBit 1.8 is valid for another model or another binary.

---

## 2. Campaign roster

Use `docs/vm_tlb/specs/C16_MULTIMODEL_NVBIT175_FULL_TRACE_CAMPAIGN.json` from this handoff branch as the machine-readable campaign seed.

Required roster for this campaign:

1. **Llama-3.2-1B** — existing frozen Lane G target; execute first.
2. **Qwen 0.5-class existing campaign target** — recover exact local model ID/revision/path from retained project assets; no substitution.
3. **Qwen 7B AWQ existing campaign target** — recover exact local model ID/revision/path from retained project assets; no substitution.
4. **DeepSeek required AI-trace target** — exact local variant/revision must be inventoried and frozen before execution; do not guess the variant.
5. **GLM required AI-trace target** — exact local variant/revision must be inventoried and frozen before execution; do not guess the variant.

If the repository/current node contains a stricter already-frozen identity for any of these, that existing identity wins over the generic roster label above.

No network model/tokenizer download is allowed merely to fill a missing model. If an exact required asset is absent, classify that model `BLOCKED_ASSET_UNAVAILABLE`, retain the inventory evidence, and continue the rest of the roster.

Do not silently add extra models. Discovery of another historical model target should be recorded as `OUT_OF_ROSTER_DISCOVERED` for review unless an existing authoritative C16 campaign contract explicitly marks it required.

---

## 3. Global campaign invariants

These invariants apply to every model and every run.

### Runtime lock

Keep fixed unless this handoff explicitly says otherwise:

```text
GPU/SM               RTX3090 / SM86
Driver               570.124.04
CUDA                 12.4
PyTorch              2.5.1+cu124
NVBit                 1.7.5
CUDA module loading   effective EAGER
Lane G tracer family  current qualified implementation lineage
```

Record hashes for:

- NVBit archive/core,
- tracer `.so`,
- tracer source commit,
- libtorch_cuda.so,
- model config / key local metadata,
- deterministic input artifact,
- parser/validator source.

### Measurement isolation

For every process:

```text
process start
 -> runtime identity validation
 -> EAGER/NVBit startup
 -> no-trace prewarm
 -> READY
 -> assert no trace exists yet
 -> acquire measurement lease / create MEASUREMENT_ACTIVE
 -> CAPTURE_BEGIN
 -> frozen workload ROI
 -> CAPTURE_END
 -> disarm measurement
 -> parser/validation
 -> cleanup
```

Prewarm must never be included in the formal trace window.

### No silent mutation

Do not silently change:

- model or revision,
- tokenizer/input source,
- batch size,
- sequence/input length,
- generation/decode length,
- dtype,
- quantization,
- attention/backend implementation,
- device map / CPU offload,
- TP topology,
- target function,
- target static instruction/range.

If a model cannot fit/run under its existing frozen contract, investigate bounded implementation/runtime issues, but do not solve it by changing the scientific workload without recording a new proposal and stopping that model for review.

---

## 4. Global Stage C0 — campaign inventory and freeze

Before running model traces, build a campaign ledger.

For every roster model, record:

```text
model_key
roster_label
exact_model_id
local_model_path
model_revision_or_content_hash
config_hash
tokenizer_or_input_contract
dtype
quantization
backend/device_map/offload
batch
input_length
generation/decode_length
ROI definition
local asset present?
existing frozen project contract?
status
```

### Existing contracts

- Preserve the current Lane G Llama frozen contract already retained by retry570. Do not reinterpret the old ordinal 34 as valid.
- The historical Llama static ordinal 348 is only a historical candidate until NVBit 1.7.5 model-level requalification confirms it.
- If existing Qwen campaign files already pin exact model variants/inputs, consume them verbatim.
- DeepSeek/GLM labels are not permission to invent exact model variants. Freeze from the assets actually present and from prior authoritative project records.

Generate a machine-readable campaign ledger and a human-readable matrix before C1 begins.

---

## 5. Per-model state machine

Run this state machine independently for each model in roster order.

### S0 — identity freeze

Require:

- exact local model asset exists;
- exact model/revision/content identity recorded;
- deterministic input exists or can be deterministically generated from an already-approved local contract;
- no network fallback;
- workload parameters frozen;
- runtime profile matches known-good infrastructure.

If not satisfiable, close this model as `BLOCKED_ASSET_UNAVAILABLE` or `BLOCKED_IDENTITY_NOT_FROZEN` and continue the next model.

### S1 — full-model no-trace runtime/prewarm canary

Run the complete frozen workload with the original Lane G tracer configured to match nothing / emit no trace.

Require:

- model load completes;
- workload completes;
- first and later kernels make forward progress;
- output/checksum/semantic terminal evidence exists;
- trace count before/during no-trace canary is zero;
- no stale GPU/diagnostic process;
- MEASUREMENT_ACTIVE absent.

If S1 fails, perform bounded diagnosis while preserving the frozen model/runtime contract. Do not proceed to capture for that model until S1 passes.

### S2 — model kernel census and target requalification

For the complete frozen workload, obtain enough low-overhead evidence to bind the target under NVBit 1.7.5:

- full mangled target function/kernel identity;
- kernel launch count in the relevant ROI(s);
- phase membership: prefill/decode and decode step when possible;
- authoritative static instruction ordinal/range for the memory instruction(s) required by the current C16 Lane G scientific target;
- opcode/memory direction/type;
- proof that the selected range contains address-bearing memory records.

Never use short-name matching when a full mangled identity is available.

Never carry a static ordinal from one model to another.

For Llama, explicitly report whether historical 348 is reconfirmed, superseded, or rejected under NVBit 1.7.5.

### S3 — narrow capture canary

Open a minimal formal capture window around one requalified target occurrence.

Require:

- prewarm trace count = 0;
- target trace count > 0;
- exact model/function/instruction identity;
- parser/schema PASS;
- address-bearing memory records present;
- normal process exit;
- clean marker/process state afterward.

### S4 — independent reproducibility

Repeat S3 in a second independent process with identical frozen inputs.

Require agreement in:

- model identity,
- target function,
- target static instruction/range,
- schema,
- ROI/phase,
- expected structural record-count contract.

Raw addresses may legitimately differ across processes. Do not require raw trace SHA equality when address/context values are process-specific.

### S5 — complete frozen workload capture

Capture **all occurrences of the requalified target memory instruction/range** across the complete frozen workload.

At minimum retain phase attribution for:

```text
PREFILL
DECODE (all frozen decode steps)
```

When the frozen input is the current C16 B1/T128/decode4 contract, do not truncate to a single decode step; capture all four decode steps unless an existing authoritative model-specific contract differs.

Prefer separate phase outputs or an unambiguous sidecar mapping rather than a single opaque trace with no phase attribution.

For each phase/model report:

- target launch count,
- trace file count,
- total records,
- address-bearing LDG/STG/ATOM records,
- total bytes,
- parser/schema status,
- target function/range,
- raw SHA256,
- output checksum/terminal evidence.

### S6 — model closeout

For each model generate a compact review pack containing:

- frozen identity receipt,
- runtime/profile receipt,
- S1 no-trace readiness receipt,
- S2 target-map receipt,
- S3/S4 reproducibility matrix,
- S5 capture summary,
- trace validation receipt,
- raw-artifact index with remote/local SHA closure,
- publish manifest.

Raw traces stay outside Git.

Only after S6 is complete should the goal runner move to the next model.

---

## 6. Storage and runtime safety

A complete multi-model campaign can become storage-bound. Treat storage as a hard invariant.

Before every S5:

1. record free bytes;
2. use S3/S4 trace size and target launch count to estimate S5 output;
3. require projected output + safety margin to fit under the existing campaign storage policy;
4. refuse unbounded tracing if the estimate is not safe.

Preserve the existing >=100 GiB formal-campaign free-space gate where applicable. In addition, do not start an S5 whose conservative projected output would consume more than half of currently free space without an explicit staged-copyback plan.

Use compression only if the parser/validation/copyback contract already supports it. Never delete the only copy of a raw trace before remote hash, local transfer, and local rehash all agree.

Every long process uses an external monotonic supervisor and process-group cleanup. Report target, remote transaction, and local SSH wall time separately.

---

## 7. Failure policy for Goal mode

The goal is to maximize completed trustworthy model traces, not to stop at the first obstacle.

For a model-specific failure:

1. identify the smallest failing stage S0–S5;
2. attempt bounded, evidence-preserving fixes that do not alter frozen scientific identity;
3. rerun only the smallest affected gate;
4. if still blocked, publish a model-specific blocker receipt;
5. continue the next model.

Stop the entire campaign early only if a **global invariant** fails, e.g.:

- known-good runtime profile no longer matches;
- disk/storage safety cannot be maintained;
- tracer produces measurement-window contamination globally;
- raw-artifact integrity cannot be guaranteed;
- a proposed fix requires changing CUDA/driver/PyTorch/NVBit away from the frozen matrix.

Do not reopen NVBit 1.8 diagnosis during this campaign.

---

## 8. Cross-model Stage C2 — final integrity audit

After all roster models reach COMPLETE or BLOCKED:

Build a cross-model matrix with one row per model and fields:

```text
MODEL
EXACT_IDENTITY
ASSET_STATUS
WORKLOAD_CONTRACT
S1_RUNTIME_READY
TARGET_FULL_IDENTITY
STATIC_RANGE
PREFILL_CAPTURE
DECODE_CAPTURE
REPRODUCIBILITY
TOTAL_RECORDS
ADDRESS_RECORDS
TRACE_BYTES
REMOTE_LOCAL_SHA_CLOSED
FINAL_STATUS
BLOCK_REASON
```

Verify that no model accidentally reused another model's static ordinal/range without an explicit requalification proof.

Verify all successful captures used NVBit 1.7.5 and effective EAGER loading.

Verify every successful model has zero prewarm trace pollution and clean post-run process/measurement state.

---

## 9. Stage C3 — final campaign publication

Publish a compact top-level campaign pack, for example:

```text
docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/
  lane_g_retry570_nvbit175_full_multimodel_campaign/
```

It should contain:

- campaign roster/ledger,
- cross-model matrix,
- per-model status links,
- total storage/accounting summary,
- SHA-closure summary,
- blocked-model explanations,
- final manifest and validation receipt.

Do not commit raw traces.

Update `LATEST_RUNTIME_STATUS.md` with a concise campaign section.

---

## 10. Goal completion criteria

The goal-mode task is complete when:

1. every required roster model has been attempted;
2. every available/frozen model has either a validated full target trace capture or a precise blocker closeout;
3. no model remains in an ambiguous “not tried” state;
4. all successful raw traces are remote-to-local SHA closed;
5. all successful traces pass schema/identity/measurement-window validation;
6. the cross-model matrix is complete;
7. publication manifest validation passes;
8. no active GPU/diagnostic process remains;
9. `MEASUREMENT_ACTIVE` is absent;
10. active Lane G branch is committed and pushed.

A final status may be either:

```text
C16_NVBIT175_MULTIMODEL_TRACE_CAMPAIGN_COMPLETE
```

or

```text
C16_NVBIT175_MULTIMODEL_TRACE_CAMPAIGN_COMPLETE_WITH_BLOCKED_MODELS
```

The second is acceptable only when every blocker is explicit and evidence-backed.

---

## 11. Required final report

Lead with:

```text
CAMPAIGN_STATUS=
CAMPAIGN_COMMIT=
PUBLISH_MANIFEST_SHA256=
NVBIT_VERSION=1.7.5
EFFECTIVE_MODULE_LOADING=EAGER

LLAMA_STATUS=
LLAMA_TARGET=
LLAMA_STATIC_RANGE=
LLAMA_PREFILL_RECORDS=
LLAMA_DECODE_RECORDS=

QWEN_0P5_STATUS=
QWEN_0P5_EXACT_IDENTITY=
QWEN_0P5_TARGET=
QWEN_0P5_STATIC_RANGE=
QWEN_0P5_PREFILL_RECORDS=
QWEN_0P5_DECODE_RECORDS=

QWEN_7B_AWQ_STATUS=
QWEN_7B_AWQ_EXACT_IDENTITY=
QWEN_7B_AWQ_TARGET=
QWEN_7B_AWQ_STATIC_RANGE=
QWEN_7B_AWQ_PREFILL_RECORDS=
QWEN_7B_AWQ_DECODE_RECORDS=

DEEPSEEK_STATUS=
DEEPSEEK_EXACT_IDENTITY=
DEEPSEEK_TARGET=
DEEPSEEK_STATIC_RANGE=
DEEPSEEK_PREFILL_RECORDS=
DEEPSEEK_DECODE_RECORDS=

GLM_STATUS=
GLM_EXACT_IDENTITY=
GLM_TARGET=
GLM_STATIC_RANGE=
GLM_PREFILL_RECORDS=
GLM_DECODE_RECORDS=

ALL_SUCCESSFUL_TRACES_SHA_CLOSED=
MEASUREMENT_WINDOWS_CLEAN=
ACTIVE_GPU_PROCESS_COUNT=
ACTIVE_DIAGNOSTIC_PROCESS_COUNT=
MEASUREMENT_ACTIVE_AFTER_CAMPAIGN=
BLOCKED_MODELS=
TOTAL_RAW_TRACE_BYTES=
```

Then provide per-model pack paths, tests, manifests, and notable deviations.
