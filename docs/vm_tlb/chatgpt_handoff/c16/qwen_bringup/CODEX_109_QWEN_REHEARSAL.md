# CODEX 109 — Qwen Native Bring-up / Long-Scenario Rehearsal

Ownership: ChatGPT
Execution node: 109 / RTX4080

## Objective

While the separate pre-capture planning window selects high-quality trace targets, independently prove that Qwen2.5-0.5B-Instruct and Qwen2.5-7B-Instruct-AWQ can execute their exact historical scenarios on RTX4080, including the long-context/resource-heavy cases.

This window removes model/runtime/resource risk before formal tracing. It is NOT a substitute for the target-selection window and must not start formal NVBit capture.

## Read first

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen_bringup/GPU_SERIALIZATION_POLICY.md
docs/vm_tlb/chatgpt_handoff/c16/qwen_bringup/QWEN_NATIVE_REHEARSAL_CONTRACT_V1.md
```

Also inspect existing Qwen model/input/runtime receipts and historical retry570 capture code only as authority/reference; do not blindly execute 3090-specific runners.

## Branch/worktree

Create a fresh execution branch/worktree. Suggested:

```text
hrl/c16-qwen-native-rehearsal-109-v1
```

Do not modify ChatGPT-owned handoff files.

## Parallel-safety requirement

A separate node109 pre-capture planning Codex may be using the GPU.

CPU-only inventory/hash/script work may run concurrently.

Before every GPU action, acquire:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

If another C16 window owns the lock, WAIT. Do not bypass it and do not kill processes.

## Priority

Execute in this order:

```text
1. Qwen2.5-0.5B-Instruct
2. Qwen2.5-7B-Instruct-AWQ
```

Do not add Qwen2.5-7B raw, Qwen3, DeepSeek, or Llama to this round.

## Required work

### A. exact local admission

For both deployments:

- verify exact model revision and transferred model receipt/inventory;
- verify all seven frozen historical input/token bindings already present on 109;
- independently verify payload SHA/semantic token hash where authority provides it;
- prove tokenizer is not invoked.

### B. historical runtime recovery

Recover the exact intended loader/backend/dtype semantics from the historical Qwen runtime binding receipts and capture code.

For AWQ, do not replace the historical quantized loader/backend with an easier generic path merely to get a PASS.

Record package/tool versions actually used on 109.

### C. model load and full scenario rehearsal

Under the shared GPU lock, load each model and run the seven-scenario matrix from the frozen bindings:

```text
S0_TEXT
S1_CODE
S2_CODE
S2_STRUCTURED
S2_TEXT
S3_TEXT
S4_STRUCTURED
```

Do not alter batch/context/decode lengths.

Record per scenario:

- PASS/failure classification;
- prefill/total or decode timing where cleanly measurable;
- output token IDs/checksum;
- peak GPU allocated/reserved memory;
- OOM/error text if applicable;
- no CPU offload.

### D. repeatability

For admitted `S2_TEXT` and `S3_TEXT`:

- warm once;
- run at least two additional same-process repetitions;
- require output checksum stability;
- record diagnostic timing spread.

### E. save small evidence only

Do not create large profiler traces.

Small logs/JSON/TSV may remain under a dedicated `/data/c16/results/...` rehearsal directory and be hash-indexed in the review pack.

Do not publish FORMAL raw data through Pipeline V1 from this rehearsal. These runs are `DIAGNOSTIC`/resource-admission evidence.

## Fail-closed rules

Do not fix failures by:

```text
retokenizing
changing frozen token IDs
shortening context
reducing batch
reducing decode length
changing dtype
changing quantization mode
CPU offload
changing attention backend without authority
```

Classify and continue to the next independent scenario/model when safe.

## Deliverables

Suggested review pack:

```text
docs/vm_tlb/review_packs/C16_QWEN_NATIVE_REHEARSAL_109_V1/
```

Required:

```text
README.md
MODEL_ADMISSION.tsv
INPUT_BINDING_MATRIX.tsv
RUNTIME_BINDING.md
SCENARIO_REHEARSAL.tsv
OUTPUT_CHECKSUMS.tsv
MEMORY_ADMISSION.tsv
REPEATABILITY.tsv
RAW_LOG_INDEX.tsv
OPEN_ISSUES.md
FINAL_DECISION.json
SHA256SUMS
```

## Acceptance

Target decisions:

For Qwen2.5-0.5B:

```text
READY_FOR_FORMAL_TARGETED_CAPTURE
```

only if exact model/input/runtime admission closes and all high-value scenarios execute without silent substitutions.

For Qwen2.5-7B-AWQ:

same rule; partial scenario admission is acceptable if a frozen high-resource scenario genuinely exceeds the 16GB resource envelope, but it must be explicit.

## STOP

STOP after both deployments have been rehearsed and the review pack is committed/pushed.

Do not run formal NVBit/NCU/NSYS capture in this window.
Do not enter multi-model scientific interpretation.