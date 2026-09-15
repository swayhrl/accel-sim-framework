# Qwen3-30B-A3B Execution Preparation Contract V1

## Objective

Prepare Qwen3-30B-A3B for scientifically valid RTX4080 layer-local/kernel-local characterization without requiring full-model GPU residency.

The preparation stage must produce enough authority that later profiling can run unattended without inventing inputs, changing runtime semantics, or guessing tensor identity.

---

# 1. Node109 local working copy

The canonical node164 archive is the authority, but repeated execution must use local SSD.

Target path:

```text
/data/c16/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Provision through:

```text
<revision>.partial
-> exact file-set/size/SHA verify against node164 canonical inventory
-> no-overwrite promotion
```

Do not execute directly from SSHFS for repeated layer loads.

A working-copy receipt must bind:

```text
canonical archive receipt SHA
canonical inventory SHA
local inventory SHA
file count
total bytes
source path
destination path
verification status
```

---

# 2. Prospective Qwen3 input authority

Qwen3-30B has no historical frozen token binding. Therefore create a new explicit prospective authority.

Preferred source texts are the same C16 semantic classes already used for cross-model work:

```text
TEXT
CODE
STRUCTURED
```

Where exact source text authorities exist from prior C16/Qwen2 bindings, reuse the raw semantic payload, not the old token IDs.

Retokenize only under the pinned Qwen3 tokenizer from the canonical revision and record this as a new prospective binding.

Initial required scenarios:

```text
Q30_S0_TEXT          B1 target-context 128   decode 4
Q30_S1_CODE          B1 target-context 256   decode 16
Q30_S2_TEXT          B1 target-context 2048  decode 32
Q30_S2_CODE          B1 target-context 2048  decode 32
Q30_S2_STRUCTURED    B1 target-context 2048  decode 32
```

S3/S4 may be added only after semantic streaming is stable:

```text
Q30_S3_TEXT          B1 target-context 8192  decode 16
Q30_S4_STRUCTURED    B4 target-context 2048  decode 16
```

If a raw text does not naturally yield enough Qwen3 tokens, use a documented deterministic extension/repetition rule before final tokenization. Do not fabricate arbitrary token IDs solely to hit length.

For each binding freeze:

```text
source text/payload SHA
construction rule
exact tokenizer authority SHA(s)
exact token IDs
token-ID canonical compact-JSON SHA
actual token count
B/context/decode
input class
binding created_at_utc
```

Once frozen, profiling must consume token IDs directly; it must not retokenize during formal runs.

---

# 3. Runtime/deployment authority

Do not modify the existing Qwen2/Llama environment in place.

Create a separate Qwen3 runtime, for example:

```text
/data/c16/env/c16-qwen3-hf-baseline/
```

The exact runtime must be derived from the archived model/config and pinned explicitly.

Record:

```text
Python
PyTorch
CUDA runtime used by PyTorch
Transformers
Accelerate if used
Safetensors
attention implementation
MoE/expert implementation path
GPU model/UUID
driver
CUDA toolkit
relevant environment variables
installed package hashes/lock receipt
Git source commit
```

Do not silently use an optimized grouped/fused expert backend if the baseline runtime selects a different path.

If a later optimized backend is studied, it becomes a separate deployment identity.

---

# 4. Static model-layout authority

Using the exact canonical index and safetensors headers, derive a deterministic layout table without loading all weights into RAM.

Required output should map every model tensor to at least:

```text
tensor name
shard
size
dtype
component class
layer id if applicable
expert id if applicable
semantic role if provable
```

Component classes should include as applicable:

```text
EMBEDDING
ATTENTION
NORM
ROUTER
EXPERT
SHARED_EXPERT_OR_OTHER_MOE_COMPONENT
FINAL_NORM
LM_HEAD
OTHER
```

Generate per-layer and per-expert byte totals and identify exact tensor sets required to materialize one complete decoder layer.

Fail closed if a tensor needed by the runtime cannot be mapped to the frozen index/header authority.

---

# 5. Semantic Layer Streaming

Implement an execution path that preserves original mathematical semantics while loading only currently required weights to the GPU.

Preferred implementation strategy:

```text
instantiate exact model/module structure on meta device
materialize embedding / one decoder layer / final head as needed
load exact tensors from local safetensors
execute on GPU
release inactive weights
```

Do not hold the full 61 GB model in GPU memory.

Mode A may use host/disk staging for inactive weights and layer-specific KV because its timing/memory behavior is not formal evidence.

For Prefill:

```text
embedding
-> layer 0
-> layer 1
-> ...
-> layer N-1
-> final norm/head as needed
```

For Decode:

```text
preserve each layer's exact past-KV state outside GPU when inactive
bring only the current layer's exact state + weights to GPU
execute one decode step in original layer order
store updated per-layer KV back to semantic-state storage
```

The implementation must preserve:

```text
hidden states
position/cache positions
attention masks
rotary semantics
KV dtype/layout
router logits/selection
expert assignment
residual path
normalization
precision
```

---

# 6. Semantic validation

The stage must not trust the streaming runner merely because it executes.

Required validation stack:

## A. Tensor/materialization checks

```text
exact tensor set per materialized module
exact SHA-bound source shard authority
expected shapes/dtypes
no missing/unexpected target-layer tensor
```

## B. Determinism

Repeat at least one S0 prefill and one decode-step semantic run from identical frozen state.

Require identical output checksum / target-layer state checksum where deterministic behavior is expected.

## C. Independent reference where practical

For a bounded S0 case, attempt one exact-runtime reference using a supported sequential/disk/CPU-offload path or another exact semantic reference. This reference is diagnostic only and is not memory-performance evidence.

If such a reference is practical, compare at least:

```text
final/selected hidden-state checksum or tolerance
router selections
expert assignment counts
next-token/logit decision
```

If a full reference is infeasible due host-resource/time constraints, document the reason and strengthen layer-local equivalence tests instead; inability to run a full-resident reference on the 4080 is not by itself a blocker.

---

# 7. TARGET_LAYER_STATE authority

For candidate representative layers/steps, freeze replayable state bundles containing at least:

```text
schema version
model id/revision
runtime/deployment receipt SHA
input binding SHA
scenario
phase
layer id
decode step if applicable
hidden_states artifact + SHA
attention mask identity
position_ids/cache_position artifact/identity
layer-local KV artifacts + SHA where applicable
router output/assignment summary for validation
RNG state if relevant
source semantic-run receipt SHA
```

Target state must be sufficient to re-execute the full selected layer independently.

---

# 8. Exact full-layer replay canary

Before formal NCU/NVBit, select at least:

```text
one Prefill layer
one Decode layer/step
```

For each:

1. materialize the full exact layer with all experts/components;
2. restore exact TARGET_LAYER_STATE;
3. execute the complete layer;
4. compare output to the corresponding semantic-streaming execution;
5. require numeric equivalence under a predeclared rule appropriate for deterministic BF16 execution;
6. record router/expert assignment equivalence;
7. record peak GPU memory to prove replay fits the RTX4080.

Accepted classification:

```text
EXACT_LAYER_REPLAY_CANARY_PASS
```

Formal profiling is not authorized until this passes.

---

# 9. Scientific boundary

This preparation may establish that layer-local replay is exact for the reconstructed layer state.

It does not prove:

```text
full-model resident latency
full-model resident cache state
full-model resident TLB state
cross-layer global reuse order
whole-model end-to-end performance
```

Later NCU/NVBit evidence must carry explicit `FORMAL_LAYER_LOCAL` / `FORMAL_KERNEL_LOCAL` classification until full-resident calibration exists.

---

# 10. Out of scope for preparation

Do not yet run large formal NCU/NVBit campaigns.

Do not:

```text
quantize BF16 authority
prune experts
change top-k
change batch/context merely to fit
profile CPU-offloaded target layers as GPU-memory evidence
use unified-memory oversubscription as formal memory evidence
make full-model performance claims
```

---

# 11. Acceptance

Preparation PASS requires:

```text
Q30_WORKING_COPY_PASS
Q30_INPUT_BINDING_V1_PASS
Q30_RUNTIME_AUTHORITY_PASS
Q30_MODEL_LAYOUT_PASS
Q30_SEMANTIC_STREAMING_S0_PASS
Q30_TARGET_LAYER_STATE_PASS
Q30_EXACT_LAYER_REPLAY_CANARY_PASS
```

Final preparation decision:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

Only then should a formal NCU/NVBit campaign be launched.
