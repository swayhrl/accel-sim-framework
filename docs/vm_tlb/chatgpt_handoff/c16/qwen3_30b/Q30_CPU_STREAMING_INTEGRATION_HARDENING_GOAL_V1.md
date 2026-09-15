# Q30 CPU Streaming Integration Hardening Goal V1

## Status

CPU-only engineering Goal for 174-new. This follows accepted CPU preparation at:

```text
b988e4052b5b92a0c46d658fdfa6c8c5102be739
```

It does not authorize GPU execution or formal profiling.

## Objective

Turn the current Q30 CPU-prep scaffold into a production-ready streaming implementation that node109 can consume with minimal first-use debugging.

The implementation must prove the real data path:

```text
sharded safetensors authority
-> exact tensor plan
-> meta-created exact Qwen3 runtime module
-> exact tensor injection
-> execute existing runtime math
-> capture/restore state
-> unload active module
-> proceed to next module/layer
```

No Qwen3 Attention/MoE/router math may be manually reimplemented.

---

# A. Upstream authority

Consume and verify:

```text
asset archive: d048d1a5348ff3ace248d1e62cdd8e071a82d5d1
control prep: 674d7acda0aaf072b7cd12cac84da9264b559cb2
CPU prep: b988e4052b5b92a0c46d658fdfa6c8c5102be739
```

Canonical model:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Frozen prospective input authority:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/prospective_inputs/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Do not modify either namespace.

---

# B. Strengthen exact materialization

Extend `util/vm_tlb/c16/qwen3_30b/` so production code can materialize an exact runtime module from meta/device-empty state.

Required behavior:

1. map each runtime parameter/buffer name to the canonical index/layout authority;
2. request only the exact tensors needed by the current component/layer;
3. open only required safetensors shards;
4. validate expected name, shape and dtype before injection;
5. inject parameters/buffers into the existing Transformers Qwen3-MoE module using supported PyTorch/Accelerate mechanisms;
6. detect missing, duplicate and unexpected tensors fail-closed;
7. explicitly release/unmaterialize the active component/layer before advancing;
8. never instantiate the complete 61 GB checkpoint in host RAM as an implementation shortcut.

Record per-stage planned/resident tensor count and bytes.

Tie handling, buffers and non-parameter state must be explicit. Do not silently assume only `named_parameters()` matters.

---

# C. Production streaming runner

Replace the current thin orchestration with a real streaming lifecycle while still delegating all model math to exact runtime modules.

The production runner should provide separable stages for:

```text
embedding
layer 0 ... layer 47
final norm
lm_head
```

For each decoder layer:

```text
materialize exact layer
-> execute exact runtime layer
-> capture required output/KV/router validation state
-> detach/store semantic state as needed
-> release layer tensors/module residency
```

For Decode, preserve exact per-layer KV/cache semantics outside the active layer and restore only the state required by the current runtime call.

Do not optimize/fuse/change the baseline runtime path in this Goal.

---

# D. TARGET_LAYER_STATE V1 hardening

The serializer/validator must bind at minimum:

```text
schema_version
model_id
model_revision
runtime/deployment authority SHA or immutable identity
input binding path/SHA
scenario
phase = PREFILL | DECODE
layer_id
decode_step when applicable
hidden_states artifact path/size/SHA/dtype/shape
attention-mask identity or explicit artifact
position_ids/cache_position identity or artifact
layer-local KV artifact(s) path/size/SHA/dtype/shape when applicable
router validation summary when available
RNG identity/state if relevant
source semantic-run receipt SHA
created_at_utc
```

Validation must reject:

```text
revision mismatch
runtime mismatch
input-binding mismatch
scenario/phase/layer/decode mismatch
missing/extra required artifacts
SHA mismatch
shape/dtype mismatch
path traversal / duplicate artifact names
partial/incomplete bundle
```

Preserve `.partial -> validated -> no-overwrite final` semantics.

---

# E. Working-copy verifier hardening

`provision.py` must compare the exact regular-file set in both directions.

Require exact equality of:

```text
relative path set
file count
size per file
SHA256 per file
total bytes
inventory digest
```

Destination extra files are a FAIL.

Prepare a resume-capable copy/provision CLI or script for later node109 use, but DO NOT execute it on node109 in this Goal.

---

# F. Tiny sharded exact-runtime integration regression

Create a tiny Qwen3-MoE fixture using the same Transformers runtime class and save it as a genuinely sharded safetensors checkpoint with a real HF weight index.

The integration test must NOT simply execute an already fully resident model as the 'streaming' side.

Required comparison:

```text
A. exact monolithic tiny runtime reference
B. meta-created model/components + production shard materializer + production streaming lifecycle
```

Close all of:

### Prefill

- output/logits bitwise equality when deterministic;
- selected expert IDs exact;
- expert token counts exact;
- router validation exact;
- streamed path demonstrates module/layer materialize then release.

### Decode with KV

Run at least two decode steps from the same prefill state and require:

- output equivalence;
- KV/cache shape/dtype/value equivalence under deterministic runtime;
- position/cache_position equivalence;
- router/expert equivalence.

### Exact complete-layer replay

Freeze a `TARGET_LAYER_STATE` from the production streaming run, start an independent replay process/path, rematerialize the complete exact layer from the sharded checkpoint, restore state, execute it, and require output/router/expert equivalence.

### Residency proof

Emit a deterministic trace/table showing which tensors/bytes are materialized per stage. Demonstrate that the streaming side never depends on all tiny-model checkpoint tensors being resident simultaneously.

---

# G. Bounded real-authority CPU materialization canary

After a host-memory preflight, perform a read-only CPU canary against the real canonical Qwen3-30B archive.

Preferred target:

```text
one complete decoder layer (for example layer 0 or a middle layer)
```

Expected tensor bytes are approximately 1.246 GB from the accepted layer summary; use the exact authority, not this approximate value.

Run the canary in a dedicated subprocess so memory is released on process exit.

Required checks:

```text
exact planned tensor set
all required shards readable
exact name/shape/dtype match
successful injection into exact Qwen3-MoE runtime layer structure
no unexpected/missing parameter/buffer
materialized byte total matches frozen layer plan
subprocess exits cleanly
```

A forward pass on the real full layer is optional in this CPU Goal and must not become a many-minute blocker. The purpose is to prove real checkpoint -> real runtime materialization compatibility.

If host RAM is genuinely insufficient, record the measured preflight and use a bounded partial-component real-authority canary instead; do not OOM the node.

---

# H. Tests and code quality

Add real repository tests for:

```text
exact symmetric provisioning verification
materializer missing/duplicate/unexpected tensor failures
shape/dtype mismatch failure
meta -> materialized -> released lifecycle
TARGET_LAYER_STATE round trip and corruption rejection
sharded tiny Prefill equivalence
sharded tiny multi-step Decode/KV equivalence
independent complete-layer replay equivalence
```

Tests must be CPU-only and deterministic where practical.

Keep implementation modular and readable; avoid one-line compressed production code for the final version.

---

# I. Strict boundaries

This Goal MUST NOT:

```text
write to node109
copy 61 GB to node109
run CUDA
use the RTX4080
run NCU/NVBit/NSYS
modify canonical model files
modify frozen input bindings
quantize/prune/change experts/top-k
claim GPU validation
claim profiling readiness
```

Reading canonical model files from 164 is allowed.

---

# J. Acceptance

PASS requires:

```text
Q30_PRODUCTION_MATERIALIZER_CPU_PASS
Q30_STREAMING_LIFECYCLE_TINY_SHARDED_PASS
Q30_DECODE_KV_TINY_SHARDED_PASS
Q30_TARGET_STATE_HARDENED_PASS
Q30_LAYER_REPLAY_TINY_SHARDED_PASS
Q30_PROVISION_VERIFIER_EXACT_SET_PASS
Q30_REAL_LAYER_MATERIALIZATION_CANARY_PASS
```

If host-memory constraints prevent the full real-layer canary after a documented preflight, use:

```text
Q30_REAL_COMPONENT_MATERIALIZATION_CANARY_PASS_WITH_HOST_LIMIT
```

and report it explicitly; all other gates still must pass.

Final status:

```text
Q30_CPU_STREAMING_INTEGRATION_HARDENING_PASS
GPU_VALIDATION_NOT_STARTED
```

Do not claim `QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING`.

---

# K. Review pack

Create:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_CPU_STREAMING_HARDENING_174NEW_V1/
```

Include at least:

```text
README.md
UPSTREAM_AUTHORITY.tsv
IMPLEMENTATION_CHANGELOG.md
MATERIALIZATION_TESTS.tsv
TINY_SHARDED_EQUIVALENCE.tsv
DECODE_KV_EQUIVALENCE.tsv
TARGET_STATE_VALIDATION.tsv
REPLAY_EQUIVALENCE.tsv
RESIDENCY_TRACE.tsv
PROVISION_VERIFIER_TESTS.tsv
REAL_AUTHORITY_MATERIALIZATION_CANARY.tsv
OPEN_ISSUES.md
FINAL_DECISION.json
SHA256SUMS
```

Commit, push and STOP.