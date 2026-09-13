# START — post-Llama all-model Goal

Use **Goal mode** after the active branch publishes the Llama S6 closeout.

## Handoff branch

```text
hrl/vm-c16-g-retry570-chatgpt-handoff-v6
```

## Read in this order

```text
docs/vm_tlb/codex_handoff/c16/retry570/POST_LLAMA_MULTIMODEL_MASTER_HANDOFF.md
docs/vm_tlb/codex_handoff/c16/retry570/PHASE_A_IDENTITY_ASSET_RECOVERY_HANDOFF.md
docs/vm_tlb/codex_handoff/c16/retry570/MODEL_CAPTURE_S0_S6_TEMPLATE_HANDOFF.md
docs/vm_tlb/codex_handoff/c16/retry570/PHASE_B_QWEN_0P5_CAPTURE_HANDOFF.md
docs/vm_tlb/codex_handoff/c16/retry570/PHASE_C_QWEN_7B_AWQ_CAPTURE_HANDOFF.md
docs/vm_tlb/codex_handoff/c16/retry570/PHASE_D_DEEPSEEK_CAPTURE_HANDOFF.md
docs/vm_tlb/codex_handoff/c16/retry570/PHASE_E_GLM_CAPTURE_HANDOFF.md
docs/vm_tlb/codex_handoff/c16/retry570/PHASE_F_CROSS_MODEL_DATASET_CLOSEOUT_HANDOFF.md
```

## Fetch/read without touching active worktree

```bash
git fetch origin hrl/vm-c16-g-retry570-chatgpt-handoff-v6
```

Then use `git show origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v6:<path>` for each file. Do not checkout/reset/merge the handoff branch.

## Entry gate

Before Phase A, verify the active branch contains a Llama S6 publication and record:

```text
LLAMA_CLOSEOUT_COMMIT
LLAMA_PUBLICATION_MANIFEST
LLAMA_PREFILL_TARGETS
LLAMA_DECODE_TARGETS
LLAMA_PREFILL_RECORDS
LLAMA_DECODE_RECORDS
```

If Llama publication is still in progress, wait for that active-branch commit rather than rerunning Llama.

## Goal sequence

```text
A identity/asset recovery
 -> B Qwen 0.5 S0-S6
 -> C Qwen 7B AWQ S0-S6
 -> D DeepSeek S0-S6
 -> E GLM S0-S6
 -> F cross-model dataset closeout
```

Do not ask for confirmation after every normal gate. Use bounded fixes and rerun the smallest failed gate.

A single model blocker does not stop later models unless it proves a global runtime/measurement/storage integrity problem.

## Non-negotiable runtime lock

```text
NVBit=1.7.5
effective module loading=EAGER
CUDA=12.4
driver=570.124.04
PyTorch=2.5.1+cu124
```

No NVBit 1.8 re-debugging.

## Critical lesson from Llama

Do not force one target across prefill and decode.

Build separate phase target manifests and classify target absence as structural zero only after kernel census proves the target was not launched.

Zero records never means “decode has no memory traffic”.

## Required final report

Lead with:

```text
POST_LLAMA_CAMPAIGN_STATUS=
POST_LLAMA_CAMPAIGN_COMMIT=
PUBLISH_MANIFEST_SHA256=
LLAMA_REFERENCE_COMMIT=
QWEN0P5_STATUS=
QWEN7B_AWQ_STATUS=
DEEPSEEK_STATUS=
GLM_STATUS=
ALL_SUCCESSFUL_TRACES_SHA_CLOSED=
DOWNSTREAM_CONSUMER_VALIDATION=
MEASUREMENT_WINDOWS_CLEAN=
TOTAL_RAW_TRACE_BYTES=
ACTIVE_GPU_PROCESS_COUNT=
ACTIVE_DIAGNOSTIC_PROCESS_COUNT=
MEASUREMENT_ACTIVE_AFTER_CAMPAIGN=
BLOCKED_MODELS=
```

For every COMPLETE model also report exact identity, phase target manifest, static ranges, prefill records, per-decode-step records where applicable, trace bytes and raw SHA closure.
