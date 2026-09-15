# CODEX Goal — Node109 Qwen3-30B Streaming Bring-up

## Preconditions

Consume:

```text
CURRENT_STATE_AFTER_Q30_ARCHIVE.md
Q30_EXECUTION_PREP_CONTRACT_V1.md
```

Also consume the final 174-new control-prep pack when available.

This Goal may begin with model provisioning/runtime setup before control-prep finishes, but semantic execution must use frozen Q30 input-binding receipts.

## Goal

Provision the exact Qwen3-30B working copy locally, establish an isolated runtime, implement semantic layer streaming, freeze replayable target-layer states, and prove exact full-layer replay canaries on RTX4080.

Do not start large formal NCU/NVBit capture in this Goal.

---

# A. Local working copy

Source authority:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Destination:

```text
/data/c16/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Use `.partial` + resume-capable content copy + independent exact inventory/SHA verification + no-overwrite promotion.

Do not modify the canonical node164 source.

---

# B. Isolated Qwen3 runtime

Do not modify `/data/c16/env/c16-py310` in place.

Create a dedicated environment, pin exact package versions and emit a runtime receipt.

The runtime must instantiate the exact archived model/config. Derive the compatible Transformers/runtime from actual canonical authority; do not use a newer optimization path simply because it is available.

Record the actual MoE/expert implementation used by the baseline.

---

# C. GPU serialization

If another C16 node109 task is active, acquire the shared GPU campaign lock before every GPU action:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

Do not bypass the lock or kill another scientific process.

CPU/disk preparation may run outside the lock.

---

# D. Streaming implementation

Implement exact semantic execution from local safetensors without materializing the whole model on GPU.

Requirements:

```text
exact BF16 model tensors
exact module/runtime implementation
exact router/top-k semantics
all experts preserved
exact attention backend selected by frozen deployment
exact KV dtype/layout
exact residual/norm/position semantics
```

Use the exact layer tensor manifests from control prep.

Prefer a meta-device skeleton or equivalent mechanism so only active modules are materialized.

Do not read 61GB repeatedly over SSHFS.

---

# E. Initial scenario

First close only:

```text
Q30_S0_TEXT  B1 / context 128 / decode 4
```

Do not expand to S1/S2 until S0 semantic streaming and exact replay canaries pass.

Run a bounded warmup/validation path, not a performance campaign.

Record:

```text
prefill semantic completion
per-layer hidden-state checksum/receipt at selected checkpoints
router/expert assignment summaries
per-layer KV state receipts
next-token/output checksum
decode-step semantic completion
peak GPU memory per materialized layer
```

---

# F. TARGET_LAYER_STATE

Freeze at least two replay states:

```text
one Prefill target layer
one Decode target layer/step
```

Prefer representative middle/deep layers after confirming model structure.

The state receipt must satisfy `Q30_EXECUTION_PREP_CONTRACT_V1.md`.

---

# G. Exact layer replay canary

For each selected state:

1. start in a fresh process where practical;
2. materialize the full exact layer including all experts/components;
3. restore the frozen state;
4. execute the complete layer;
5. compare layer output with the semantic-streaming source run;
6. compare router selections/expert counts;
7. record max GPU memory;
8. repeat once to prove deterministic replay.

Do not profile only a standalone synthetic GEMM as the acceptance canary.

Expected gate:

```text
Q30_EXACT_LAYER_REPLAY_CANARY_PASS
```

---

# H. Optional diagnostic reference

If practical, use an exact-runtime sequential/disk/CPU-offload reference for a bounded S0 case solely as a semantic oracle.

It must be labelled:

```text
DIAGNOSTIC_SEMANTIC_REFERENCE
```

Its timing/cache/memory behavior is never formal evidence.

Do not block the entire stage solely because this optional oracle is too slow or resource-intensive if layer-local equivalence and other semantic gates are strong.

---

# I. Failure/recovery policy

Recoverable engineering failures are sub-goals:

```text
package incompatibility -> isolate/pin compatible runtime
single layer OOM -> verify stale allocations/processes; do not prune/change precision
state serialization bug -> fix serializer and rerun affected semantic state
KV movement bug -> preserve exact per-layer KV and repair state handling
expert mapping mismatch -> return to exact index/layout evidence
```

Do not lower model/runtime/input standards to get a PASS.

Global STOP is justified only if exact semantics cannot be reconstructed after bounded root-cause attempts or if the canonical asset/inventory is invalidated.

---

# J. Deliverables

Create:

```text
docs/vm_tlb/review_packs/C16_QWEN3_30B_STREAMING_BRINGUP_109_V1/
```

Include at least:

```text
README.md
WORKING_COPY_RECEIPT.json
RUNTIME_AUTHORITY.json
STREAMING_IMPLEMENTATION.md
S0_EXECUTION_SUMMARY.tsv
LAYER_MEMORY_SUMMARY.tsv
ROUTER_EXPERT_SUMMARY.tsv
TARGET_LAYER_STATE_INDEX.tsv
EXACT_LAYER_REPLAY_CANARY.tsv
OPTIONAL_REFERENCE.tsv
OPEN_ISSUES.md
SHA256SUMS
```

Expected final status:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

Commit/push and STOP before large NCU/NVBit capture.
