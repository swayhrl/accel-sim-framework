# CODEX Goal — Node109 Qwen3-30B GPU Semantic Streaming + Exact Replay V1

## Goal mode

This is the first real RTX4080 execution stage for the accepted Qwen3-30B-A3B authority.

The objective is **not** to collect formal NCU/NVBit traces yet.

The objective is to prove that the original BF16 model can be executed with exact layer streaming on the 16 GB RTX4080 and that frozen real target-layer states can be replayed as complete exact runtime layers with equivalent outputs/router behavior.

Expected successful final state:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

Do not claim this status unless every acceptance gate below passes.

---

# 0. Upstream authority

Consume and bind these accepted commits:

```text
asset archive:
d048d1a5348ff3ace248d1e62cdd8e071a82d5d1

control/input/layout prep:
674d7acda0aaf072b7cd12cac84da9264b559cb2

CPU implementation prep:
b988e4052b5b92a0c46d658fdfa6c8c5102be739

CPU integration hardening:
6034071c76279952c1476626552a9eaaaab6ef0b
```

Read the upstream review packs and verify their `SHA256SUMS` before GPU execution.

Model identity:

```text
Qwen/Qwen3-30B-A3B
revision: ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Do not change model revision, expert count, top-k, precision, context, or batch to make execution easier.

---

# 1. Node109 preflight and GPU ownership

Before touching the GPU:

1. record hostname/user/date;
2. record `nvidia-smi` GPU model, UUID, driver, memory state and active processes;
3. verify sufficient local free disk for the 61.08 GB model plus runtime/state artifacts;
4. inspect the C16 GPU lock;
5. verify no active scientific GPU campaign conflicts with this Goal.

All GPU actions must execute while holding:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

Use normal `flock`/equivalent ownership. Never remove or bypass an active lock simply because the user reported the GPU idle.

If another workload appears, wait. Do not kill it.

Expected platform identity:

```text
RTX4080 16 GB
GPU UUID: GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59
driver: 580.178.04
CUDA toolkit: 12.8
```

If these differ, record the actual platform and STOP before scientific acceptance until the difference is reviewed.

---

# 2. Provision exact local working copy

Canonical source authority is node164 through node174-new:

```text
hrl174new:/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Destination on node109:

```text
/data/c16/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Use:

```text
<revision>.partial
→ resume-capable content copy
→ independent exact regular-file set/size/SHA verification
→ no-overwrite promotion
```

Accepted payload authority:

```text
26 files
61,084,187,391 bytes
16 weight shards
61,066,575,648 weight bytes
payload inventory SHA256:
20b21f889daf61d7362d4e0042ff7f3b2517cc1f0a917d3e0667654ded8cb30a
```

Use the accepted provisioning verifier from:

```text
util/vm_tlb/c16/qwen3_30b/provision.py
```

or strengthen it if required. Destination extra files must fail verification.

Do not modify node164 canonical source.

Do not delete the original historical download source in this Goal.

PASS gate:

```text
Q30_WORKING_COPY_PASS
```

---

# 3. Provision frozen S0 input authority locally

Consume only:

```text
Q30_S0_TEXT
B1 / context 128 / decode 4
```

Source authority on node164:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/prospective_inputs/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Copy the exact S0 token-id artifact and receipt to a local node109 provenance directory using exact SHA verification.

Expected token-id SHA256:

```text
5800e1ffaa5546dd2d4331fff1c6687fe46e3b58fe95b1f768405244da3908d6
```

Expected receipt SHA256:

```text
4b69d23ecce9925569b299c28af17de553f416730c9b57552b3f561dd12e05b6
```

Do not retokenize. Do not regenerate token IDs.

Record a local input receipt binding source path, local path, file bytes and SHA256.

---

# 4. Dedicated Q30 GPU runtime

Do not modify:

```text
/data/c16/env/c16-py310
```

Create a dedicated environment, suggested:

```text
/data/c16/env/c16-qwen3-30b-hf451-gpu
```

Use:

```text
/data/c16/env/cpython-3.10.12
```

as the interpreter authority unless the host preflight disproves it.

The CPU compatibility reference was:

```text
Transformers 4.51.0
Safetensors 0.5.2
Accelerate 1.3.0
Torch 2.5.1 API surface
```

On node109 use the CUDA-capable Torch build already validated for the host where practical (historically Torch 2.5.1+cu124), but keep the environment isolated and freeze the actual resolved package set.

Required runtime receipt must include:

```text
Python version/path
Torch version/build
Torch CUDA runtime
Transformers
Safetensors
Accelerate
Tokenizers if installed
GPU model/UUID
NVIDIA driver
CUDA toolkit
relevant environment variables
model revision/config SHA
Git execution commit
attention implementation
Qwen3 MoE/expert implementation class/path
source-file SHA(s) for the relevant Qwen3 runtime implementation
```

Instantiate the exact archived config/model structure on `meta` and require runtime state keys to close against the 18,867 canonical weight-map keys.

Do not silently select a fused/grouped expert path that differs from the chosen baseline. Do not install FlashAttention or another backend merely to improve performance.

Freeze the first baseline deployment identity explicitly, e.g. conceptually:

```text
qwen3_30b_a3b_hf451_bf16_<actual_attention>_<actual_moe_path>
```

PASS gate:

```text
Q30_GPU_RUNTIME_AUTHORITY_PASS
```

---

# 5. Real single-layer CUDA materialization preflight

Before the 48-layer semantic run, use the accepted production materializer path to materialize one complete real decoder layer with all experts onto CUDA.

Use Layer 0 for this preflight.

Require:

```text
exact expected tensor set
strict state_dict key equality
shape equality
dtype equality
BF16 authority preserved
all experts present
successful exact runtime module materialization
successful explicit release back to meta
GPU memory returns to a stable bounded baseline after synchronization/release
```

Record:

```text
materialized tensor count
weight bytes
max_memory_allocated
max_memory_reserved
post-release allocated/reserved
elapsed wall time (diagnostic only)
```

This is a capacity/engineering canary, not formal performance evidence.

If one exact full layer does not fit, diagnose stale allocations/processes first. Do not prune experts or quantize.

---

# 6. Real S0 semantic layer streaming

Run only:

```text
Q30_S0_TEXT
B1
context 128
decode 4
```

Use:

```text
torch.inference_mode()
model.eval() semantics
original BF16 tensors
exact frozen token IDs
exact runtime modules
```

Do not attempt full-model simultaneous residency.

## 6.1 Prefill

Execute semantically:

```text
embedding
→ layer 0
→ layer 1
→ ...
→ layer 47
→ final norm
→ lm_head as required for next-token decision
```

For each decoder layer:

```text
materialize exact full layer with all experts
execute exact runtime forward
capture required semantic receipts
preserve produced KV state
release layer back to meta
continue
```

Inactive layer weights may reside on local SSD/host memory because this semantic run is not memory-performance evidence.

The hidden state may remain on GPU between layers if that is the cleanest exact implementation.

Layer-specific KV may be staged to CPU between uses. Preserve exact dtype/layout/content.

Record for every layer at least:

```text
layer id
input hidden shape/dtype
output hidden SHA/checksum receipt
KV shape/dtype and content receipt where present
router/expert summary
materialized weight bytes
peak allocated/reserved GPU memory
post-release allocated/reserved GPU memory
```

Do not store every large tensor in Git. Large state artifacts remain on the data plane; Git review pack records path/SHA/shape/dtype/bytes.

## 6.2 Decode

Perform four deterministic decode steps using a frozen explicit decoding rule. Prefer the existing C16 deterministic/greedy convention; record the exact rule in the runtime/run receipt.

For each step:

```text
new-token embedding
→ layers 0..47 sequentially
→ restore each layer's exact prior KV
→ execute layer
→ stage updated layer KV
→ final norm/head
→ deterministic next-token decision
```

Do not change context, batch, KV dtype or attention semantics.

Record next-token IDs and semantic checksums for all four steps.

PASS requires successful Prefill + all four Decode steps without model-semantic shortcuts.

PASS gate:

```text
Q30_SEMANTIC_STREAMING_S0_PASS
```

---

# 7. Freeze real TARGET_LAYER_STATE bundles

This Goal is a canary-validation stage, not representative-target selection. Use a fixed canary layer to avoid post-hoc target picking:

```text
layer_id = 24
```

Freeze at least:

```text
PREFILL / layer 24 / input state immediately before full layer forward
DECODE / decode step 3 / layer 24 / input state immediately before full layer forward
```

If the runtime uses additional exact forward-boundary tensors/kwargs beyond the generic contract, include them. The bundle must be sufficient to call the exact complete runtime layer in an independent fresh process without recomputing previous model layers.

Each bundle must bind at least:

```text
schema version
model id/revision
working-copy receipt SHA
runtime/deployment receipt SHA
Git execution commit
input-binding receipt SHA
scenario
phase
layer id
decode step when applicable
hidden_states artifact + SHA/shape/dtype
attention mask or exact mask identity
position_ids/cache_position or equivalent exact artifacts
position embeddings/cos/sin if they are part of the actual layer call boundary
layer-local past KV artifacts + SHA/shape/dtype for Decode
all other tensor kwargs consumed by the actual runtime layer
router/expert source summary used for later validation
source semantic-run receipt SHA
RNG state only if semantically relevant
```

Use the hardened serializer/validator and `.partial` → no-overwrite promotion.

Validate every artifact SHA after freezing.

PASS gate:

```text
Q30_TARGET_LAYER_STATE_PASS
```

---

# 8. Exact complete-layer replay canaries on RTX4080

For each frozen state:

```text
Prefill layer 24
Decode step 3 layer 24
```

run an independent replay process where practical.

Replay procedure:

1. load the exact runtime/deployment identity;
2. instantiate the exact complete layer on meta;
3. materialize all original BF16 layer tensors, including all experts;
4. restore the frozen TARGET_LAYER_STATE;
5. execute the exact full runtime layer once;
6. capture layer output and router/expert evidence;
7. release the layer;
8. repeat the replay once from the same frozen state to test determinism.

The acceptance canary is the **complete layer**, not a standalone GEMM.

Required comparisons against the corresponding semantic-streaming source execution:

```text
output shape/dtype exact
router selected expert IDs exact
expert token counts exact
router/logit evidence exact where captured
layer output bitwise equal by default
```

Also compare the two independent replay repetitions.

If layer output is not bitwise identical, do not silently introduce a loose tolerance and declare PASS. First identify whether the same baseline runtime contains a reproducible nondeterministic operation. Record detailed max-abs/max-rel diagnostics and root cause. Any non-bitwise acceptance requires explicit later review; this Goal itself should remain BLOCKED rather than weakening the equivalence rule.

Record max GPU memory for both Prefill and Decode replay.

PASS gate:

```text
Q30_EXACT_LAYER_REPLAY_CANARY_PASS
```

---

# 9. Preserve replay states

Keep real target-state bundles on node109 data plane under a deterministic run directory, suggested:

```text
/data/c16/qwen3_30b/bringup/<RUN_ID>/target_states/
```

After both replay canaries PASS, copy the selected small state bundles + semantic/replay receipts to node164 through `hrl174new` under a clearly non-Pipeline provenance namespace, suggested:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/qwen3_30b_replay_states/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/<RUN_ID>/
```

Use `.partial`, exact file-set/size/SHA verification and no-overwrite promotion.

Classification:

```text
REPLAY_STATE_PROVENANCE_ONLY_NOT_PIPELINE_RUN
```

Do not register these states as capture raw data.

---

# 10. Explicitly out of scope

Do not in this Goal:

```text
run formal NCU
run formal NVBit
run NSYS campaign
select final representative trace kernels
expand to S1/S2/S3/S4
quantize the BF16 authority
prune experts
change top-k
change model revision
change batch/context to fit
use Unified Memory oversubscription as formal evidence
profile CPU-offloaded target layers as GPU memory evidence
make whole-model performance/cache/TLB claims
```

Diagnostic `nvidia-smi`, CUDA memory counters and bounded wall-clock timing are allowed.

---

# 11. Recovery policy

Treat recoverable engineering failures as sub-goals, not immediate global failure:

```text
copy interrupted → resume .partial and reverify
package mismatch → repair isolated Q30 environment only
runtime state mismatch → return to exact canonical index/runtime mapping
layer OOM → inspect stale processes/allocations and release lifecycle
KV interface mismatch → fix exact state orchestration without changing semantics
TARGET_LAYER_STATE missing kwarg → extend schema to actual runtime call boundary
replay mismatch → diagnose source/replay state/runtime identity; do not weaken acceptance
```

Global STOP/BLOCKED is appropriate if exact semantics cannot be reconstructed after bounded root-cause attempts or an accepted upstream authority is invalidated.

---

# 12. Required review pack

Create:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_GPU_STREAMING_REPLAY_109_V1/
```

Include at least:

```text
README.md
UPSTREAM_AUTHORITY.tsv
PLATFORM_PREFLIGHT.json
GPU_LOCK_RECEIPT.json
WORKING_COPY_RECEIPT.json
INPUT_LOCAL_RECEIPT.json
GPU_RUNTIME_AUTHORITY.json
RUNTIME_SOURCE_FINGERPRINT.tsv
REAL_LAYER0_CUDA_MATERIALIZATION.tsv
S0_EXECUTION_SUMMARY.tsv
PREFILL_LAYER_SUMMARY.tsv
DECODE_STEP_SUMMARY.tsv
ROUTER_EXPERT_SUMMARY.tsv
GPU_MEMORY_SUMMARY.tsv
TARGET_LAYER_STATE_INDEX.tsv
TARGET_STATE_ARCHIVE_RECEIPT.tsv
EXACT_LAYER_REPLAY_CANARY.tsv
REPLAY_DETERMINISM.tsv
OPEN_ISSUES.md
FINAL_DECISION.json
SHA256SUMS
```

Do not commit large hidden/KV/target-state binary payloads to Git.

---

# 13. Final acceptance

All of the following must be PASS:

```text
Q30_WORKING_COPY_PASS
Q30_GPU_RUNTIME_AUTHORITY_PASS
Q30_SEMANTIC_STREAMING_S0_PASS
Q30_TARGET_LAYER_STATE_PASS
Q30_EXACT_LAYER_REPLAY_CANARY_PASS
```

Then and only then set:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

This final state means only that exact reconstructed **layer-local/kernel-local** profiling is authorized next.

It does not authorize full-model-resident claims.

Commit, push, report and STOP before starting NCU/NVBit.