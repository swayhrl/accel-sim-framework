# C16 Lane G Retry570 — NVBit 1.7.5 model-level capture handoff

## 0. Purpose

The minimal capture infrastructure is now qualified. This handoff advances Lane G from a tiny deterministic `index_select` canary to a **model-level, scientifically usable targeted trace capture** while preserving the validated runtime/measurement boundary.

This handoff intentionally does **not** authorize an unbounded all-kernel/all-instruction trace. “Full capture” here means: capture the complete occurrences of the frozen target within the complete frozen model workload window, with a bounded and validated target filter, reproducible model/input identity, clean prewarm/measurement isolation, and complete artifact closure.

### Anchors

- repository: `swayhrl/accel-sim-framework`
- active lane branch: `hrl/vm-c16-g-retry570-v0`
- qualified checkpoint: `d001a349156c51aa6de15f30b9aedaa70f534442`
- capture qualification status: `NVBIT_RETRY570_NVBIT175_MINIMAL_CAPTURE_QUALIFIED_STOP_FOR_REVIEW`
- minimal capture manifest SHA256: `f60b57cfc1ef172bd8c66ac16c7fede9208b530745f0948e6693095f6306d196`
- handoff branch: `hrl/vm-c16-g-retry570-chatgpt-handoff-v3`

Read this file from the handoff branch, but continue coding/running on the existing active Lane G worktree. Do not checkout/reset/merge the handoff branch merely to consume this document.

---

## 1. What is already proven

Do not regress or repeat these gates without a concrete reason.

### Runtime/toolchain

Known-good profile:

```text
GPU                RTX3090 / SM86
driver             570.124.04
CUDA               12.4
nvcc               12.4.131
nvdisasm           12.4.127
PyTorch            2.5.1+cu124
NVBit              1.7.5
module loading     effective EAGER
```

NVBit 1.8 is not the active candidate for this lane: its core first-use/module bookkeeping path did not reach READY under the bounded qualification. Do not reopen 1.8 debugging during this campaign.

### Q0/Q1/Q2 minimal capture

- Q0 runtime/prewarm: PASS.
- `PREWARM_TRACE_COUNT=0`.
- Q1 independent process run 1: PASS, 7,360 records.
- Q1 independent process run 2: PASS, 7,360 records.
- each raw trace: 481,651 bytes.
- each trace: 192 explicit address-bearing `LDG.E` rows.
- exact full `indexSelectLargeIndex` mangled identity was bound.
- Q2 schema/target/lifecycle/truncation validation: PASS.
- post-run GPU process count = 0.
- `MEASUREMENT_ACTIVE` absent after cleanup.

This proves the runtime, capture arm/disarm lifecycle, targeted tracing, trace writer/parser, and minimal reproducibility. It does **not** yet prove model-level identity or scientific capture correctness.

---

## 2. Important historical model contract — use as input, not as assumed truth

The retained model package/status records a frozen historical Llama contract:

```text
M1 S0/TEXT
B1 / T128 / decode4
no tokenizer execution
no context resize
```

Historical model disambiguation identified a real NVTX-contained target kernel:

```text
indexSelectLargeIndex
nsys grid ID 1
```

and historically proposed:

```text
LDG.E static ordinal 348
INSTR_BEGIN=348
INSTR_END=351
```

**Do not blindly reuse static ordinal 348 after switching to NVBit 1.7.5.** A vendor-version change is an implementation change. Model-level target/function identity and the instruction mapping must be requalified under the exact NVBit 1.7.5 tracer build before scientific capture.

The old ordinal 34 attempt remains invalid and must never be resurrected.

---

## 3. Campaign definition

The first formal model campaign should use **one frozen Llama workload only**. Do not start Llama and Qwen in parallel.

Initial model campaign:

```text
model family: historical frozen Llama package already retained by Retry570
input binding: M1 S0/TEXT
batch: B1
prompt/context length: T128
decode steps: 4
```

Codex must recover the exact existing package/model/config hashes from the retained authoritative Retry570 artifacts. Do not recreate model inputs from memory and do not run tokenizer/network downloads.

If an exact required model artifact is missing locally/remote, stop with a concrete missing-artifact report rather than substituting another model/checkpoint/token sequence.

---

## 4. M0 — freeze the model-level campaign identity

Before any NVBit model run, construct a machine-readable campaign identity receipt containing at least:

- model artifact path(s), size(s), SHA256,
- config/token/input artifact SHA256,
- exact frozen B1/T128/decode4 parameters,
- torch/CUDA/NVBit/tool hashes,
- `libtorch_cuda.so` SHA256,
- GPU UUID/model/SM/driver,
- effective CUDA module-loading mode,
- Lane G tracer source commit and binary SHA256,
- known-good runtime profile SHA256,
- output/trace directory and free-space receipt.

Require the existing formal storage gate before model capture. Do not proceed if the required free-space threshold is not satisfied.

M0 output:

```text
MODEL_CAMPAIGN_IDENTITY_FROZEN=PASS
```

---

## 5. M1 — model no-trace runtime/prewarm canary

### Goal

Prove the exact frozen Llama process completes its bounded startup/prewarm/model path with NVBit 1.7.5 + original Lane G tracer while tracing is disabled.

Use:

- NVBit 1.7.5 only,
- effective EAGER,
- original Lane G tracer binary/source hashes,
- impossible/no-match dynamic range so no trace is emitted,
- `MEASUREMENT_ACTIVE` absent throughout.

### Required observations

Record at least:

- process start,
- model load complete,
- prewarm begin/end,
- first CUDA kernel completion,
- model forward/decode progression markers already available in the frozen workload,
- terminal output/checksum or equivalent deterministic output identity,
- trace-file count before/after = 0,
- wall accounting,
- cleanup state.

Do not invent a new long timeout. Use a bounded model canary budget justified by retained historical behavior and report target/remote/local wall separately. If it cannot complete, capture the last concrete progress marker and stop before enabling capture.

M1 PASS means only:

```text
NVBIT175_LLAMA_RUNTIME_READY=PASS
```

It does not yet authorize a scientific target capture.

---

## 6. M2 — rebind the target under NVBit 1.7.5

### Goal

Confirm that the model still launches the exact target function expected from the historical disambiguation and establish an authoritative NVBit-1.7.5 target/instruction mapping.

### Step M2A — exact function identity canary

Run one bounded model canary with tracing restricted to the complete mangled `indexSelectLargeIndex` function/kernel identity, but do **not** yet narrow to historical static ordinal 348.

Required evidence:

- exact full mangled name,
- kernel/grid/launch identity available to the tracer,
- number of target launches during the frozen workload,
- each target launch completes,
- model process completes,
- bounded trace size,
- parser accepts output,
- prewarm has zero trace before arm.

If the full-function trace is too large, stop the run at a predefined conservative size threshold and retain the partial diagnostic only as non-scientific mapping evidence; do not silently truncate and call it scientific.

### Step M2B — derive static memory-instruction mapping

From the NVBit 1.7.5 target-function evidence, determine the target memory instruction(s) by actual 1.7.5 instruction enumeration/trace metadata.

The result must explicitly state whether historical ordinal 348 remains equivalent under the exact 1.7.5 tracer build.

Possible outcomes:

```text
HISTORICAL_348_RECONFIRMED
NEW_175_STATIC_ORDINAL=<n>
MAPPING_INCONCLUSIVE
```

Only the first two permit narrow scientific capture.

Do not use SASS text line counters as NVBit static ordinals.

M2 output must freeze:

- target full mangled identity,
- target kernel/launch identity,
- authoritative NVBit 1.7.5 static ordinal/range,
- opcode (`LDG.E` or actual observed equivalent),
- source/binary/tool hashes used to derive it.

---

## 7. M3 — narrow single-window model capture canary

### Goal

Perform the first model-level **targeted** capture using the requalified NVBit 1.7.5 instruction range.

Lifecycle must be exactly:

```text
process start
 -> runtime/profile verification
 -> EAGER init
 -> model load
 -> no-trace prewarm
 -> assert trace count == 0
 -> LANE_G_MODEL_RUNTIME_READY
 -> acquire measurement lease
 -> create MEASUREMENT_ACTIVE
 -> CAPTURE_BEGIN
 -> execute the frozen B1/T128/decode4 model window
 -> CAPTURE_END
 -> disarm measurement
 -> close trace
 -> parse/validate
 -> cleanup
```

Do not create `MEASUREMENT_ACTIVE` before model prewarm/READY.

### M3 PASS requirements

- model completes normally,
- frozen model/input identity matches M0,
- capture contains only the requalified target/range,
- at least one valid address-bearing target record exists,
- no prewarm trace,
- no append after CAPTURE_END,
- final newline/truncation guard PASS,
- parser/schema PASS,
- trace size is within estimated/storage bounds,
- post-run GPU/diagnostic processes = 0,
- `MEASUREMENT_ACTIVE` absent.

This is still a canary scientific window until reproducibility is established.

---

## 8. M4 — reproducibility qualification

Repeat the exact M3 campaign in **two independent processes** using the same frozen model/input/tool/profile identity.

Required comparison:

- target function identity identical,
- static instruction/range identical,
- number of target launches identical unless the model contract explicitly permits otherwise,
- record count compared and explained,
- opcode/schema identical,
- deterministic model output/checksum identical where applicable,
- trace bytes/hashes may differ due to virtual/runtime addresses; do not require raw SHA equality,
- derived normalized statistics should agree exactly or within a declared deterministic expectation.

If record counts differ, do not average them away. Diagnose the cause before proceeding.

M4 PASS status:

```text
NVBIT175_LLAMA_TARGET_CAPTURE_REPRODUCIBLE
```

---

## 9. M5 — complete frozen-workload capture

Only after M4 PASS, run the full frozen B1/T128/decode4 target capture intended for downstream TLB/Cache analysis.

“Complete” means all occurrences of the **requalified target instruction/range** across the entire frozen workload window, not every instruction from every model kernel.

Before run:

- estimate expected trace bytes from M3/M4 rate × target-launch count,
- require enough free space plus safety margin,
- ensure local receiver/storage capacity,
- set a hard file-size/record-count safety limit that terminates as `BOUNDED_ABORT_NOT_SCIENTIFIC` rather than filling disk.

After run validate:

- model completed,
- no target launch omitted,
- trace file closed cleanly,
- exact record/launch accounting,
- schema/identity/address checks,
- remote SHA -> local copy -> local SHA closure,
- raw trace kept outside Git,
- compact metadata/publication committed.

M5 output status if successful:

```text
NVBIT175_LLAMA_FROZEN_WORKLOAD_TARGET_TRACE_CAPTURED
```

---

## 10. M6 — scientific publication checkpoint

Publish a compact review pack that includes:

- campaign identity receipt,
- runtime profile receipt,
- model artifact/input hashes,
- target mapping report,
- M1 runtime canary receipt,
- M2 target/ordinal requalification receipt,
- M3/M4 reproducibility matrix,
- M5 full frozen-workload capture summary,
- raw-artifact index with remote/local hashes and sizes,
- parser/schema validation receipt,
- storage/cleanup receipt,
- `PUBLISH_MANIFEST.json` + validator receipt,
- updated `LATEST_RUNTIME_STATUS.md`.

Raw model traces remain out of Git.

Stop for review after the first Llama model campaign. Do **not** automatically continue to Qwen/DeepSeek/GLM or other models from the same authorization.

---

## 11. Failure-directed branching

Do not respond to every failure by increasing timeout.

### M1 fails before READY

Investigate model/package/runtime progression only. Do not enable trace.

### M1 passes, M2 target never appears

Treat this as model-level target identity mismatch. Rebuild a bounded nsys/NVBit target census using the frozen model; do not substitute a short name or another kernel.

### M2 function appears but historical ordinal 348 does not match

Derive and freeze the correct NVBit 1.7.5 ordinal. This is an expected requalification possibility, not a failure.

### M3 trace is empty

Investigate filter/range/measurement arm timing. Do not change model identity.

### M3 trace is huge

Stop at the declared safety bound. Reduce capture scope only by evidence-based target/range filtering, not by dropping arbitrary records.

### M4 differs across independent runs

Diagnose launch count, record count, dynamic shape/context, allocator/address normalization, and capture lifecycle. Do not proceed to M5 until understood.

---

## 12. Hard constraints

During the first model campaign:

```text
NVBit must remain 1.7.5
CUDA/driver/PyTorch/model checkpoint must not change
no network model/tokenizer download
no model/input substitution
no NVBit 1.8 debugging
no unbounded all-kernel trace
no C frozen target
no historical 300s watch
no old 6+6 rerun
```

The only new scientific activity authorized by this handoff is the staged first frozen-Llama model campaign M0–M6 above.

---

## 13. Required next report fields

Lead with:

```text
MODEL_CAMPAIGN_IDENTITY_FROZEN=
MODEL_ARTIFACT_SHA256=
INPUT_BINDING=
M1_NVBIT175_LLAMA_RUNTIME_READY=
M1_MODEL_OUTPUT_IDENTITY=
M2_TARGET_FULL_MANGLED_IDENTITY=
M2_TARGET_LAUNCH_COUNT=
M2_NVBIT175_STATIC_ORDINAL=
M2_HISTORICAL_348_STATUS=
M3_SINGLE_WINDOW_CAPTURE=
M3_RECORD_COUNT=
M3_ADDRESS_RECORD_COUNT=
M4_REPRO_RUN1_RECORD_COUNT=
M4_REPRO_RUN2_RECORD_COUNT=
M4_REPRODUCIBLE=
M5_FULL_FROZEN_WORKLOAD_CAPTURE=
M5_TARGET_LAUNCH_COUNT=
M5_RECORD_COUNT=
M5_TRACE_BYTES=
TRACE_SCHEMA_VALIDATION=
MEASUREMENT_WINDOW_CLEAN=
REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=
ACTIVE_GPU_PROCESS_COUNT=
MEASUREMENT_ACTIVE_AFTER_RUN=
PUBLICATION_COMMIT=
PUBLISH_MANIFEST_SHA256=
```

Then report focused tests, artifact hashes, wall times, storage receipts, and any bounded deviations.
