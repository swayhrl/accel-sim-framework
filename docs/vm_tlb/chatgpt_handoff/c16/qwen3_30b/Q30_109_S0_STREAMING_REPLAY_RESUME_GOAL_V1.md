# CODEX Goal — Resume Node109 Qwen3-30B S0 Semantic Streaming + Exact Replay V1

## Objective

Resume from the accepted pre-semantic node109 checkpoint and complete the first real Qwen3-30B-A3B RTX4080 semantic/replay gate.

The objective is **not** formal profiling.

The objective is to establish, on the exact preserved deployment, that:

```text
Q30_S0_TEXT
B1 / context 128 / decode 4
```

can execute with exact BF16 layer streaming, that real call-boundary target states can be frozen, and that the selected full original layers can be replayed independently with equivalent output/router behavior.

Successful final status:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

Stop immediately after this readiness gate. Do not launch NCU/NVBit/NSYS or larger scenarios in this Goal.

---

# 0. Resume authority

The mandatory resume checkpoint is:

```text
execution branch:
hrl/c16-qwen3-30b-gpu-streaming-replay-109-v1

checkpoint commit:
d87d7726bc9d5a142519cae95a081b94018c71a2

checkpoint decision:
Q30_PRE_SEMANTIC_GPU_BRINGUP_CHECKPOINT_PASS
```

Consume and SHA-verify:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_PRE_SEMANTIC_CHECKPOINT_109_V1/
```

especially:

```text
FINAL_DECISION.json
RESUME_POINTERS.json
WORKING_COPY_RECEIPT.json
GPU_RUNTIME_AUTHORITY.json
META_INDEX_CLOSURE.tsv
LAYER0_MATERIALIZATION_CANARY.tsv
S0_LOCAL_INPUT_AUTHORITY.tsv
GPU_LOCK_AND_RELEASE_RECEIPT.json
SHA256SUMS
```

Also bind the accepted CPU hardening authority:

```text
6034071c76279952c1476626552a9eaaaab6ef0b
```

Do not redo completed pre-semantic work unless resume validation shows it has been invalidated.

---

# 1. Resume preflight

Before CUDA execution:

1. verify current hostname/user/date;
2. verify RTX4080 UUID remains `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`;
3. verify driver remains `580.178.04` and expected toolkit remains available;
4. inspect `nvidia-smi` for active compute processes and memory use;
5. inspect `/data/c16/locks/c16_gpu_campaign.lock`;
6. verify the preserved runtime and local model/input paths exist;
7. verify the checkpoint review-pack `SHA256SUMS`;
8. revalidate the local model working copy against the frozen local inventory/receipt before GPU execution.

Preferred local model revalidation is a full local SHA pass against the accepted inventory. Do not copy 61 GB from node164 again unless local integrity actually fails.

Require unchanged local model authority:

```text
26 regular payload files
61,084,187,391 bytes
inventory SHA256:
20b21f889daf61d7362d4e0042ff7f3b2517cc1f0a917d3e0667654ded8cb30a
```

Require unchanged S0 artifacts:

```text
token IDs SHA256:
5800e1ffaa5546dd2d4331fff1c6687fe46e3b58fe95b1f768405244da3908d6

input receipt SHA256:
4b69d23ecce9925569b299c28af17de553f416730c9b57552b3f561dd12e05b6
```

Require unchanged runtime authority file hash:

```text
8feb468251b3dda5c37229f962ae9f2f4f6773efb64fd9b62949190a43c7add7
```

Do not reinstall or upgrade the Q30 environment if it remains valid.

Resume only if the GPU is actually available. If another scientific workload is present, do not kill it; wait or produce a clean pause report.

---

# 2. GPU ownership

All Q30 CUDA execution in this Goal must be serialized by:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

Acquire it normally with `flock` or equivalent and record ownership.

The semantic run and replay subprocesses must not deadlock on nested acquisition. If an outer shell/process owns the campaign lock, child GPU processes should execute under that ownership rather than trying to take a second blocking lock.

Do not remove or bypass an active lock.

Create a fresh deterministic data-plane run directory, e.g.:

```text
/data/c16/qwen3_30b/bringup/<RUN_ID>/
```

with subdirectories for:

```text
semantic/
target_states/
replay/
logs/
receipts/
```

Large tensor/state artifacts stay on the data plane, never in Git.

---

# 3. Preserve the accepted deployment exactly

Use the existing runtime:

```text
/data/c16/env/c16-qwen3-30b-hf451-gpu
```

Accepted identity:

```text
Python        3.10.12
Torch         2.5.1+cu124
Torch CUDA    12.4
Transformers  4.51.0
Safetensors   0.8.0
Accelerate    1.1.1
Tokenizers    0.21.0
attention     SDPA
MoE path      official Transformers Qwen3MoeSparseMoeBlock sparse expert loop
```

Do not silently change:

```text
model revision
BF16 precision
attention implementation
MoE implementation
expert count = 128
top-k = 8
batch = 1
context = 128
input token IDs
KV dtype/layout
```

Do not enable FlashAttention, grouped/fused expert code, quantization, expert pruning, Unified Memory oversubscription, CPU-offloaded target-layer profiling, or another deployment to make the run easier.

The semantic streaming pass may stage inactive layer weights and inactive per-layer KV on CPU/local SSD because its timing/cache behavior is not formal performance evidence.

---

# 4. Real S0 Prefill semantic streaming

Execute only the frozen `Q30_S0_TEXT` token IDs under:

```text
torch.inference_mode()
model.eval() semantics
```

Use the exact runtime modules and the hardened shard materializer.

Do not materialize the full 61 GB model in GPU memory or host RAM.

The required logical Prefill path is:

```text
exact embedding
→ layer 0
→ layer 1
→ ...
→ layer 47
→ exact final norm
→ exact lm_head
→ deterministic next-token decision
```

For each decoder layer:

```text
instantiate/materialize the exact complete runtime layer on meta/CUDA
load the exact original BF16 tensor set from the local working copy
execute the exact runtime forward
preserve exact output/KV semantics
collect bounded receipts
release layer weights back to meta
continue
```

No Qwen math may be reimplemented in the streaming runner.

For every layer record at least:

```text
layer id
input hidden shape/dtype
output hidden shape/dtype
output hidden bytewise SHA/checksum receipt
exact materialized tensor count/bytes
KV shape/dtype/bytes/hash where present
router/expert summary
peak allocated/reserved GPU memory
post-release allocated/reserved GPU memory
```

Record wall-clock time only as diagnostic engineering evidence, never as full-model performance evidence.

## Fixed Prefill validation target

At:

```text
phase = PREFILL
layer_id = 24
immediately before the exact complete layer forward
```

freeze the **actual runtime call boundary** into a replayable target bundle.

The target bundle must include all tensors/identities needed by the installed Transformers 4.51.0 layer call, not merely a generic guessed interface.

At minimum bind:

```text
model id/revision
working-copy receipt SHA
runtime authority SHA/deployment identity
Git execution commit
input receipt SHA
scenario = Q30_S0_TEXT
phase = PREFILL
layer = 24
hidden_states bytes/hash/shape/dtype
attention mask artifact/identity if consumed
position_ids/cache_position if consumed
position embeddings/cos/sin if consumed at the layer boundary
past/cache object state if consumed
all other tensor kwargs consumed by the exact runtime layer
RNG state only if semantically relevant
source semantic-run receipt SHA
```

Also save an expected source-layer output artifact/receipt for replay validation. This expected output is a validation oracle and is not part of the pre-forward call boundary itself.

Collect source router evidence for layer 24 without changing model math. Prefer exact runtime outputs/hooks rather than a reimplementation.

---

# 5. Deterministic generation convention

Freeze and record the generation rule before Decode.

Use deterministic greedy selection from the exact logits:

```text
argmax over final-token logits
```

No sampling, temperature, top-p, top-k sampling, or stochastic generation.

Record the token produced by Prefill and every subsequent Decode forward.

Define Decode numbering explicitly as **zero-based forward numbering after Prefill**:

```text
decode_step 0 = first single-token Decode forward after Prefill
decode_step 1 = second
decode_step 2 = third
decode_step 3 = fourth
```

Therefore the fixed Decode replay canary is the fourth Decode forward:

```text
decode_step = 3
layer_id = 24
```

This convention must appear in the semantic-run receipt and target-state receipt.

---

# 6. Four-step exact Decode semantic streaming

Perform exactly four Decode forwards: steps `0,1,2,3`.

For each Decode step:

```text
embed current generated token
→ layer 0
→ restore exact layer-0 past KV/cache
→ exact layer forward
→ save updated layer-0 KV/cache
→ release layer weights
→ ...
→ layer 47
→ final norm
→ lm_head
→ greedy argmax next token
```

Preserve each layer's exact past KV/cache state across steps. Staging per-layer cache to CPU is allowed for semantic reconstruction; changing dtype/layout/content is not.

For every step and layer record bounded receipts for:

```text
hidden shape/dtype/checksum
cache shape/dtype/bytes/checksum
router/expert summary
materialized weight bytes
GPU allocated/reserved peaks
post-release memory
```

Do not reuse a previous layer's cache for a different layer. Preserve layer index identity explicitly.

## Fixed Decode validation target

At:

```text
phase = DECODE
decode_step = 3
layer_id = 24
immediately before complete layer forward
```

freeze the exact actual runtime call boundary using the same state rules as Prefill, including the exact layer-24 prior KV/cache required for this fourth Decode forward.

Also save the corresponding expected source-layer output and router evidence.

PASS gate for this section:

```text
Q30_SEMANTIC_STREAMING_S0_PASS
```

This requires successful Prefill plus all four Decode forwards with no semantic shortcut.

---

# 7. TARGET_LAYER_STATE integrity gate

Use the hardened state serializer/validator from accepted CPU hardening.

Each state bundle must be created through `.partial` then no-overwrite promotion and independently revalidated after finalization.

The two required states are exactly:

```text
PREFILL / layer 24
DECODE / step 3 / layer 24
```

Generate an index that binds each state bundle to:

```text
bundle path
manifest SHA
model revision
runtime authority SHA
working-copy receipt SHA
input receipt SHA
source semantic-run receipt SHA
phase/layer/step
all artifact paths/SHA/shape/dtype/bytes
expected source output path/SHA
router evidence path/SHA
```

No artifact required by the actual forward call may be omitted.

PASS gate:

```text
Q30_TARGET_LAYER_STATE_PASS
```

---

# 8. Fresh-process complete-layer replay canaries

For each target state, execute replay in a fresh Python process where practical while preserving the same campaign GPU lock ownership.

Replay must:

1. use the unchanged preserved Q30 runtime;
2. instantiate the exact complete layer 24 on meta;
3. materialize all original BF16 layer-24 weights, including all 128 experts;
4. restore the exact frozen call-boundary state;
5. invoke the exact Transformers runtime layer;
6. capture output and router/expert evidence;
7. release the layer;
8. repeat from the identical frozen state in another fresh process to test replay determinism.

Perform this for:

```text
Prefill layer 24
Decode step 3 layer 24
```

The canary is the **whole runtime layer**, not a synthetic GEMM or isolated expert.

Required source-vs-replay comparisons:

```text
output shape: exact
output dtype: exact
output bytes: bitwise equal by default
selected expert IDs: exact
expert token counts: exact
router evidence: exact where captured
```

Required replay1-vs-replay2 comparisons are the same.

If output bytes are not bitwise identical:

```text
DO NOT silently loosen tolerance
DO NOT declare PASS based only on close numerics
```

Instead capture:

```text
max absolute error
max relative error
number of differing elements
first mismatch diagnostics
router/expert comparison
runtime/CUDA determinism context
```

and diagnose the root cause. Any non-bitwise acceptance requires explicit later review; this Goal should remain `BLOCKED` rather than weakening the criterion.

Record actual peak allocated/reserved GPU memory for both replay targets and post-release memory.

PASS gate:

```text
Q30_EXACT_LAYER_REPLAY_CANARY_PASS
```

---

# 9. Archive successful replay-state provenance

Only after both semantic and replay gates pass, archive the successful target-state bundles plus small semantic/replay receipts to node164 through `hrl174new`.

Destination namespace:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/
qwen3_30b_replay_states/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/<RUN_ID>/
```

Use:

```text
<run>.partial
→ exact regular-file set/size/SHA verify
→ no-overwrite promotion
```

Classification:

```text
REPLAY_STATE_PROVENANCE_ONLY_NOT_PIPELINE_RUN
```

Do not place these artifacts in Pipeline `captures/raw`, and do not register them as a formal capture run.

Do not delete the local target-state copy in this Goal.

---

# 10. Recovery policy

Recoverable engineering failures are sub-goals and may be fixed without weakening identity:

```text
stale GPU allocation → cleanly exit stale Q30 process, recheck lock, retry
isolated runtime import bug → repair only if exact frozen deployment identity remains unchanged
layer materialization lifecycle bug → fix orchestration, not model precision/expert count
cache API mismatch → adapt exact Transformers call/state handling
TARGET_LAYER_STATE missing actual kwarg → extend schema to the actual runtime boundary
state serializer bug → fix and regenerate affected state
```

For semantic or replay failures, preserve diagnostic evidence before retrying.

Never recover by:

```text
quantizing
pruning experts
changing top-k
changing attention backend
changing batch/context
retokenizing
changing model revision
switching to an optimized MoE deployment
using CPU-offloaded target layer as formal GPU evidence
```

Global `BLOCKED` is appropriate if exact semantics/replay cannot be closed after bounded root-cause attempts.

---

# 11. Explicitly out of scope

Do not start in this Goal:

```text
formal NCU
formal NVBit
NSYS campaign
kernel census for formal target selection
S1/S2/S3/S4
representative final trace selection
full-model performance claims
full-model resident cache/TLB claims
```

Diagnostic `nvidia-smi`, memory counters, logs, checksums and wall times are allowed.

---

# 12. Required final review pack

Create/update the final stage review pack:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_GPU_STREAMING_REPLAY_109_V1/
```

Include at least:

```text
README.md
UPSTREAM_AUTHORITY.tsv
RESUME_FROM_CHECKPOINT.json
GPU_RESUME_PREFLIGHT.json
GPU_LOCK_RECEIPT.json
SEMANTIC_RUN_RECEIPT.json
S0_EXECUTION_SUMMARY.tsv
PREFILL_LAYER_SUMMARY.tsv
DECODE_STEP_SUMMARY.tsv
ROUTER_EXPERT_SUMMARY.tsv
GPU_MEMORY_SUMMARY.tsv
TARGET_LAYER_STATE_INDEX.tsv
EXACT_LAYER_REPLAY_CANARY.tsv
REPLAY_DETERMINISM.tsv
TARGET_STATE_ARCHIVE_RECEIPT.tsv
OPEN_ISSUES.md
FINAL_DECISION.json
SHA256SUMS
```

The pack may reference accepted checkpoint receipts rather than duplicating unchanged evidence, but all references must bind exact commit/path/SHA.

Do not commit large hidden/KV/state binary payloads to Git.

---

# 13. Final acceptance

The accepted checkpoint already supplies:

```text
Q30_WORKING_COPY_PASS
Q30_GPU_RUNTIME_PREP_PASS
Q30_META_INDEX_CLOSURE_PASS
Q30_LAYER0_MATERIALIZATION_CANARY_PASS
Q30_S0_INPUT_LOCAL_AUTHORITY_PASS
```

This resume Goal must newly establish:

```text
Q30_SEMANTIC_STREAMING_S0_PASS
Q30_TARGET_LAYER_STATE_PASS
Q30_EXACT_LAYER_REPLAY_CANARY_PASS
```

Only if all inherited and new gates are PASS may `FINAL_DECISION.json` state:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

The scientific evidence level at that point is still:

```text
FORMAL_LAYER_LOCAL / FORMAL_KERNEL_LOCAL readiness only
```

not full-model-resident performance/cache/TLB evidence.

After final decision:

1. commit and push the execution branch;
2. ensure no Q30 CUDA/Python process remains;
3. release the campaign GPU lock;
4. verify GPU returns to driver baseline;
5. report the final branch/SHA/status and STOP.

Do not automatically continue into profiling.
