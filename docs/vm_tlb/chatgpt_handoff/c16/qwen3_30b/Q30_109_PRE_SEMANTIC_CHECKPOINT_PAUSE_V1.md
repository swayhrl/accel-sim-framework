# Q30 Node109 Pre-Semantic Checkpoint / Pause V1

## Purpose

This document defines a clean pause point for the Qwen3-30B-A3B node109 GPU bring-up so the RTX4080 can be released to other work without losing completed preparation.

The current run has already completed or nearly completed the following expensive but reusable preparation:

- node109 platform / disk / GPU preflight;
- exact 61 GB working-copy transfer from node164 canonical authority;
- promotion from `<revision>.partial` to the final local model directory;
- Q30_S0_TEXT token-ID / receipt localization and SHA closure;
- isolated Q30 GPU runtime creation;
- official Qwen3MoE runtime API confirmation;
- one bounded canonical Layer-0 BF16 materialize/release canary.

The correct pause boundary is **before starting the full 48-layer S0 semantic streaming run**.

---

## Required work before pausing

Finish only the following bounded closure tasks:

1. Complete the final symmetric SHA verification between the node109 working copy and the node164 canonical payload.
2. Record `Q30_WORKING_COPY_PASS` only if the exact regular-file set, size, and SHA match.
3. Freeze the Q30 GPU runtime/deployment identity, including:
   - Python;
   - Torch and Torch CUDA;
   - Transformers;
   - Safetensors;
   - Accelerate;
   - Tokenizers;
   - driver;
   - GPU UUID;
   - CUDA toolkit/runtime;
   - attention implementation;
   - Qwen3 MoE/expert implementation path;
   - relevant environment variables;
   - Git commit/source authority.
4. Close the exact meta/runtime/index state-key mapping at 18,867 keys.
5. Record the completed Layer-0 canonical materialize/release canary, including:
   - tensor count;
   - materialized bytes;
   - device;
   - peak allocated/reserved memory if available;
   - post-release allocated memory;
   - PASS/FAIL.
6. Record the frozen Q30_S0_TEXT input authority SHA values already localized on node109.
7. Create a hash-closed checkpoint review pack and commit/push it.

Do **not** start the 48-layer Prefill/Decode semantic streaming run merely to reach a larger milestone.

---

## Checkpoint classification

Successful pause state:

```text
Q30_PRE_SEMANTIC_GPU_BRINGUP_CHECKPOINT_PASS
```

with sub-gates:

```text
Q30_WORKING_COPY_PASS
Q30_GPU_RUNTIME_PREP_PASS
Q30_META_INDEX_CLOSURE_PASS
Q30_LAYER0_MATERIALIZATION_CANARY_PASS
Q30_S0_INPUT_LOCAL_AUTHORITY_PASS
```

Explicitly record:

```text
Q30_SEMANTIC_STREAMING_S0 = NOT_STARTED
Q30_TARGET_LAYER_STATE = NOT_STARTED
Q30_EXACT_LAYER_REPLAY_CANARY = NOT_STARTED
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING = NOT_CLAIMED
```

This is an accepted intermediate checkpoint, not a scientific profiling-ready state.

---

## Required checkpoint review pack

Create:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_PRE_SEMANTIC_CHECKPOINT_109_V1/
```

Include at least:

```text
README.md
FINAL_DECISION.json
WORKING_COPY_RECEIPT.json
WORKING_COPY_VERIFY.tsv
GPU_RUNTIME_AUTHORITY.json
META_INDEX_CLOSURE.tsv
LAYER0_MATERIALIZATION_CANARY.tsv
S0_LOCAL_INPUT_AUTHORITY.tsv
RESUME_POINTERS.json
OPEN_ISSUES.md
SHA256SUMS
```

`RESUME_POINTERS.json` must bind:

- model revision;
- local model path;
- local working-copy inventory/receipt SHA;
- local runtime path;
- runtime authority SHA;
- Q30_S0 token IDs path/SHA;
- Q30_S0 receipt path/SHA;
- upstream hardening commit `6034071c76279952c1476626552a9eaaaab6ef0b`;
- the next exact stage: `Q30_S0 semantic streaming -> real target states -> RTX4080 exact-layer replay`.

---

## GPU release procedure

After the checkpoint review pack is committed and pushed:

1. Ensure no Q30 CUDA process remains.
2. Ensure no Python process is holding model tensors on the GPU.
3. Verify with `nvidia-smi` that Q30 GPU memory is released.
4. Release `/data/c16/locks/c16_gpu_campaign.lock` if this run holds it.
5. Do not delete the local 61 GB working copy.
6. Do not delete the isolated Q30 GPU runtime.
7. Do not delete localized Q30_S0 frozen-input authority.
8. STOP.

The later resume must start from these durable local assets and the checkpoint receipt; it must not recopy/recreate them unless verification fails.

---

## Resume boundary

When node109 becomes available again, resume from:

```text
Q30_S0_TEXT B1 / T128 / Decode4
```

and perform:

```text
48-layer real BF16 Prefill
-> four Decode steps with exact per-layer KV
-> freeze Prefill Layer-24 call-boundary state
-> freeze Decode Step-3 / Layer-24 call-boundary state
-> fresh-process complete-layer replay for both
-> replay determinism + router/expert/output equivalence
```

Only after those pass may the state advance to:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

No NCU/NVBit/NSYS is authorized at this checkpoint.
