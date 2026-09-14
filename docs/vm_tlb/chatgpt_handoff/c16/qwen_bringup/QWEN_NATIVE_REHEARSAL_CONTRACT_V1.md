# C16 Qwen Native Rehearsal Contract V1

Ownership: ChatGPT
Status: pre-capture diagnostic contract

## Objective

Before the formal high-quality NVBit campaign, prove that the two highest-priority deployments can execute their historical frozen scenarios correctly on RTX4080 without retokenization or silent runtime substitution:

1. Qwen2.5-0.5B-Instruct
2. Qwen2.5-7B-Instruct-AWQ

This round is intentionally **not** a formal NVBit capture round. Its purpose is to eliminate model-load/runtime/input/resource surprises before expensive tracing.

## Exact model authorities

### Qwen2.5-0.5B-Instruct

```text
revision:
7ae557604adf67be50417f59c2c2f167def9a775

expected 109 transferred root:
/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775
```

### Qwen2.5-7B-Instruct-AWQ

```text
revision:
b25037543e9394b818fdfca67ab2a00ecc7dd641

expected 109 transferred root:
/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641
```

Do not infer admission merely from path existence. Revalidate model inventory against the already-transferred source/provenance receipts before model load.

## Frozen scenario authorities

For each deployment, use its own exact historical binding already transferred under:

```text
/data/c16/inputs/.incoming/<model_slug>/<binding>/
```

Required historical scenarios:

| Binding | Batch | Prefill | Decode | Input class |
|---|---:|---:|---:|---|
| S0_TEXT | 1 | 128 | 4 | TEXT |
| S1_CODE | 1 | 256 | 16 | CODE |
| S2_CODE | 1 | 2048 | 32 | CODE |
| S2_STRUCTURED | 1 | 2048 | 32 | STRUCTURED |
| S2_TEXT | 1 | 2048 | 32 | TEXT |
| S3_TEXT | 1 | 8192 | 16 | TEXT |
| S4_STRUCTURED | 4 | 2048 | 16 | STRUCTURED |

Never re-tokenize. Use the transferred derived token-ID payload/binding authority for each model/scenario.

## Runtime authority

Historical backend/loader semantics must be recovered from the existing Qwen runtime/model receipts and prior capture code.

Do not silently substitute:

- a different quantization loader;
- a different attention backend;
- a different dtype;
- CPU offload;
- a shorter context;
- a smaller batch;
- a different decode length.

If a deployment/scenario cannot execute under its frozen runtime identity on RTX4080, classify it explicitly rather than altering the experiment.

## GPU isolation

All GPU actions obey `GPU_SERIALIZATION_POLICY.md` and the shared lock:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

This window may coexist with the pre-capture planning window only through serialized GPU ownership.

## Rehearsal sequence

For each deployment:

### R0 asset/input admission

- exact model revision and receipt binding;
- exact historical input/token binding for all seven scenarios;
- no tokenizer execution;
- record loader/backend/runtime versions.

### R1 model-load admission

Load the model once under the historical runtime contract and record:

```text
load status
load wall time
GPU memory after load
peak allocated/reserved memory if available
CPU offload = false
```

### R2 scenario matrix

Run all seven scenarios when resource-admitted.

For every scenario record separately:

```text
binding identity
prefill wall time
decode wall time / total generation wall time
peak GPU memory allocated/reserved
output token IDs
canonical output-token checksum
exception/OOM if any
```

These timings are DIAGNOSTIC resource/runtime measurements, not formal performance conclusions.

### R3 repeatability focus

For `S2_TEXT` and `S3_TEXT`, run at least two additional same-process repetitions after warmup when admitted.

Require output-token checksum stability across repetitions. Timing variability may be recorded but is diagnostic.

### R4 shape-equivalence probe

Compare runtime/kernel-signature summaries available without duplicating the separate pre-capture planning campaign for:

```text
S2_CODE
S2_STRUCTURED
S2_TEXT
```

The three scenarios share B1/T2048/D32. Determine whether native runtime behavior is obviously identical or materially different. Do not run a second full NSYS campaign if the planning window is already producing the authoritative census; consume its result later instead.

## Explicit non-goals

Do NOT in this rehearsal:

- run formal large NVBit traces;
- choose arbitrary convenient LDG/STG targets;
- run NCU if the pre-capture planning window is already doing candidate NCU;
- create new Qwen3/DeepSeek bindings;
- alter scenario shapes to make a model fit;
- claim cross-model memory behavior.

## Classifications

Per scenario use one of:

```text
REHEARSAL_PASS
NOT_ADMITTED_MEMORY
RUNTIME_BINDING_BLOCKED
INPUT_BINDING_BLOCKED
MODEL_ASSET_BLOCKED
EXECUTION_FAILED
```

Per deployment:

```text
READY_FOR_FORMAL_TARGETED_CAPTURE
PARTIAL_SCENARIO_ADMISSION
NOT_READY_FOR_CAPTURE
```

## Required evidence

Create a review pack containing at minimum:

```text
MODEL_ADMISSION.tsv
INPUT_BINDING_MATRIX.tsv
RUNTIME_BINDING.md
SCENARIO_REHEARSAL.tsv
OUTPUT_CHECKSUMS.tsv
MEMORY_ADMISSION.tsv
REPEATABILITY.tsv
OPEN_ISSUES.md
FINAL_DECISION.json
SHA256SUMS
```

Do not put model weights or large runtime output into Git.