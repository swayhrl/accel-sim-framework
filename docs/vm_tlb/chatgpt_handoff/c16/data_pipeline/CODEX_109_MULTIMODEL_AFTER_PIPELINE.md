# CODEX 109 — Multi-model Capture After Pipeline V1

Ownership: ChatGPT
Execution node: 109 / RTX4080
Status: do not execute until `C16_DATA_PLANE_V1_QUALIFIED`

## Objective

Start the first formal multi-model capture wave using the qualified data plane. Use existing exact historical model/input authorities, resource-admit scenarios on the 16 GiB RTX4080, capture only scientifically useful bounded data, and publish every admitted run through Pipeline V1.

## Eligible models in Wave 1

```text
Qwen2.5-0.5B-Instruct
Qwen2.5-7B-Instruct raw
Qwen2.5-7B-Instruct-AWQ
```

Existing historical bindings per deployment:

```text
S0_TEXT        B1 / T128  / Decode4
S1_CODE        B1 / T256  / Decode16
S2_CODE        B1 / T2048 / Decode32
S2_STRUCTURED  B1 / T2048 / Decode32
S2_TEXT        B1 / T2048 / Decode32
S3_TEXT        B1 / T8192 / Decode16
S4_STRUCTURED  B4 / T2048 / Decode16
```

Do not retokenize.

## Not yet eligible

```text
Qwen3-8B
DeepSeek-V2-Lite
```

Reason: `NO_HISTORICAL_FROZEN_BINDING`. A separate prospective input-authority stage is required.

## Stage 1 — resource/runtime admission first

For every model/scenario candidate, first record without profiling:

```text
exact model revision
exact input receipt/binding
GPU free/total memory before load
runtime dtype/backend
full CUDA residency or explicit rejection
peak memory
correctness/checksum gate
OOM/failure reason
```

Do not retry by silently changing dtype/backend/context/batch.

Classification:

```text
ADMITTED
NOT_ADMITTED_MEMORY
NOT_ADMITTED_RUNTIME
NOT_ADMITTED_AUTHORITY
```

A non-admitted scenario is evidence; do not force it onto RTX4080.

## Stage 2 — native baseline

For admitted scenarios:

```text
1-2 warmups
3 measured repetitions initially
expand to 5 only if variability requires it
```

Record prefill/decode timing separately when technically possible without perturbing correctness. Bind all result JSON to RUN_MANIFEST.

## Stage 3 — lightweight census

Use the cheapest available qualified mechanism to build launch/kernel census for admitted scenarios.

Prefer complete lightweight census before bounded NCU/NVBit.

Record:

```text
kernel/function identity
launch count
duration distribution
stream
phase/decode-step relation when available
backend implementation identity
```

Do not claim operator semantics that are not evidenced.

## Stage 4 — bounded NCU/NVBit representative capture

Do not trace every launch.

For the first wave, prioritize:

```text
heavy-duration kernels
attention-related implementation kernels
FFN/GEMM-like kernels
embedding/output or KV-management special cases
quant/dequant kernels for AWQ
one audit/random representative where useful
```

Use selector/representative decisions frozen by the coordination state available at execution time. If no selector is yet qualified, capture only a minimal canary/reference set and do not pretend it is an unbiased whole-model estimator.

Every NCU/NVBit capture must be bounded and published through Pipeline V1.

## Efficiency order

Run models in this practical order unless resource evidence says otherwise:

```text
Qwen2.5-0.5B
Qwen2.5-7B AWQ
Qwen2.5-7B raw
```

This maximizes early useful data while avoiding spending the first hours on a marginal-memory raw-7B case.

## Required output

For each deployment:

```text
RESOURCE_ADMISSION.tsv
NATIVE_RUN_INDEX.tsv
CENSUS_INDEX.tsv
CAPTURE_INDEX.tsv
PIPELINE_PUBLISH_INDEX.tsv
```

Update Codex report/review pack with formal vs diagnostic boundaries.

## Acceptance

Wave-1 deployment PASS requires:

```text
model/input authority exact
at least S0 admitted and correct, or explicit deployment-level NOT_ADMITTED reason
all formal runs use Pipeline V1
no ad-hoc raw copy
no retokenization
no silent backend/dtype substitution
all published runs ACKed/cataloged
```

## STOP

STOP after the first-wave admitted scenarios and bounded representative captures are published/cataloged.

Do not invent Qwen3/DeepSeek inputs.
Do not rent a larger GPU in this stage.
Do not perform architecture-mechanism simulation yet.