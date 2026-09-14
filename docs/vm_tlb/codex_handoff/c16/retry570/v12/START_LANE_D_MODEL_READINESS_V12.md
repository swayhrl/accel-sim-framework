# START — Lane D next-model readiness V12

Use Goal mode.

This is a CPU/local-prep lane. Its purpose is to ensure Lane A does not run out of GPU-ready scientific rows later.

Read:

```bash
git fetch origin hrl/vm-c16-g-retry570-v0 hrl/vm-c16-g-retry570-chatgpt-handoff-v12

git show origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v12:docs/vm_tlb/codex_handoff/c16/retry570/v12/C16_GPU_FIRST_MULTI_WINDOW_HANDOFF_V12.md
```

Do not run GPU model workloads, nsys, NVBit, or NCU. Do not mutate Lane A's active worktree.

## Goal

Prepare authoritative model/input/binding/runtime rows so Lane A always has something useful to execute when Route-B GPU work temporarily waits on CPU code.

Priority order:

1. Qwen0 S1/CODE — prove frozen identity equality against retained valid native baseline and prepare campaign-G1 invocation inputs.
2. Qwen7 raw S2/TEXT, S2/CODE, S2/STRUCTURED — same frozen-identity comparison and campaign-G1 invocation inputs.
3. Llama S1-S4 — recover/freeze exact Recovery-V3 binding/scenario authority needed for GPU execution.
4. Qwen7-AWQ — local expected payload manifest and exact package closure plan; do not run remote full-tree SHA while GPU queue is nonempty.
5. Qwen3-8B — recover authoritative runtime input/binding from retained evidence; never invent missing tokens or inputs.
6. DeepSeek-V2-Lite — same, using the already hash-closed exact model revision.
7. GLM — recover exact deployment identity/revision before any execution; do not guess.

Qwen3-30B-A3B remains `EXCLUDED_BY_USER_CURRENT_CAMPAIGN`; do not inspect or modify its separate user-managed tree.

## Required output

Maintain a compact local readiness table under:

`/root/share/c16_recovery_v3/receipts/GPU_READY_NEXT.tsv`

Columns:

```text
priority
model
scenario
model_identity_closed
input_authority_closed
binding_closed
native_baseline_reusable
campaign_g1_ready
remote_model_ready
next_gpu_stage
blocking_reason
authority_receipt
updated_at
```

Use only evidence that actually exists.

For rows whose native baseline is proposed for reuse, compare at minimum:

```text
deployment/model/revision/tokenizer revision
scenario shape
input hash
dtype/quantization
implementation/backend
output checksum contract where applicable
```

Any mismatch means `native_baseline_reusable=false`; do not silently reuse or rerun with changed identity.

## Remote I/O rule

Before any upload, remote SHA scan, or other heavy remote I/O, read:

`/root/autodl-tmp/c16_retry570/control/GPU_PIPELINE_STATE.json`

If GPU-ready work exists, defer heavy remote I/O unless Lane A grants a transfer slot.

Local hashing, local manifest generation, authority recovery, and compact binding prep may proceed continuously.

## Git rule

If code or compact receipts must be committed, use a separate worktree/branch. Do not touch Lane A's active branch. Prefer local receipts under `/root/share` for pure readiness state.

## Report

```text
GPU_READY_NEXT_COUNT=
QWEN0_S1_READY=
QWEN7_S2_TEXT_READY=
QWEN7_S2_CODE_READY=
QWEN7_S2_STRUCTURED_READY=
LLAMA_S1_S4_READY_COUNT=
AWQ_READINESS=
QWEN3_8B_READINESS=
DEEPSEEK_READINESS=
GLM_IDENTITY_STATUS=
HEAVY_REMOTE_IO_DEFERRED=
```

Ordinary missing-file/search issues should be solved by inspecting existing receipts/packages before asking the user.