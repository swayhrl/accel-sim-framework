# CODEX Goal — 174-new CPU-only Qwen3-30B Streaming Implementation Prep V1

## Status

Execution-ready CPU-only engineering task.

This Goal prepares code, schemas, tests, and runtime/provisioning contracts so node109 can later perform bounded Qwen3-30B GPU validation with minimal implementation work.

It does **not** authorize any Qwen3-30B GPU execution.

## Accepted upstream authority

Consume and preserve:

```text
asset archive:
d048d1a5348ff3ace248d1e62cdd8e071a82d5d1
QWEN3_30B_A3B_CANONICAL_ARCHIVE_PASS

control prep:
674d7acda0aaf072b7cd12cac84da9264b559cb2
Q30_CONTROL_PREP_PASS
```

Immediate review-pack authority:

```text
docs/vm_tlb/review_packs/C16_QWEN3_30B_CONTROL_PREP_174NEW_V1/
```

Canonical model:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Prospective input authority:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/prospective_inputs/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

---

# A. Hard execution boundary

This entire Goal runs on 174-new and is CPU-only.

Do not:

```text
SSH to node109 for writes
copy the 61 GB model to node109
modify /data/c16 on node109
run CUDA workloads
run Qwen3-30B on any GPU
run NCU / NVBit / NSYS
modify the node164 canonical model
retokenize or replace the five frozen Q30 input bindings
```

If a library tries to initialize CUDA during tests, disable CUDA visibility for the test process and keep the test CPU-only.

Reading canonical metadata, safetensors headers, index files, and the accepted control-prep pack is allowed. Avoid repeatedly reading the full 61 GB payload when headers/manifests are sufficient.

---

# B. Authority preflight

Before implementation, fail closed on upstream authority drift.

Verify at least:

```text
control-prep SHA256SUMS
Q30_CONTROL_PREP_PASS
model revision = ad44e777...
18,867 layout entries
48 decoder layers
5 frozen input bindings + receipts
canonical model path exists and is readable
canonical archive receipt/inventory remains consistent
```

Record all consumed file SHAs in the final review pack.

Do not regenerate upstream authorities merely because they are inconvenient.

---

# C. Implement a dedicated Q30 streaming utility package

Add a self-contained package under a path such as:

```text
util/vm_tlb/c16/qwen3_30b/
```

Use clear modules rather than one monolithic script. The exact file split may vary, but functionality must cover:

```text
authority loading/validation
model-layout access
runtime/meta-model compatibility
per-layer materialization plan
shard-aware tensor loading
semantic-streaming execution interfaces
TARGET_LAYER_STATE schema and serializer
full-layer replay harness interfaces
node109 provisioning verification
CLI entry points
unit/integration tests
```

Do not implement a new mathematical version of Qwen3 attention or MoE. Reuse the exact Transformers/runtime module semantics and make the streaming layer responsible for materialization/state orchestration only.

---

# D. Exact runtime/meta-model compatibility on CPU

Create an isolated CPU-only preparation environment outside the existing production environments.

Rules:

1. Read the archived `config.json`, including any recorded `transformers_version` metadata.
2. Do not simply install `latest`.
3. Select and pin an exact compatible Transformers/tokenizers/safetensors/accelerate stack.
4. Record package versions and installation provenance.
5. Use CPU/meta-device only.

Instantiate the exact Qwen3-MoE config/model structure on `meta` or equivalent zero-allocation mode.

Enumerate persistent model parameter/state names and compare against the canonical 18,867 tensor index/layout.

Required closure:

```text
index tensor -> runtime state target
runtime persistent state -> index tensor or explicitly justified non-checkpoint state
```

Produce a machine-readable compatibility report.

Unexpected missing model parameters, renamed tensors, or incompatible module structure are blockers until explained.

This CPU runtime check does not establish the final node109 CUDA deployment identity. Label it accordingly:

```text
CPU_META_RUNTIME_COMPATIBILITY_ONLY
GPU_RUNTIME_VALIDATION_PENDING
```

---

# E. Per-layer materialization and shard access plan

Using `Q30_MODEL_LAYOUT.tsv` plus the canonical index/header authority, generate deterministic plans for:

```text
embedding
layers 0..47
final norm
lm_head
```

For every layer include at least:

```text
layer_id
exact tensor names
expert ids
component classes
source shard(s)
bytes by tensor/component
layer total bytes
number of shards touched
stable plan digest
```

Generate a shard-aware read plan that minimizes unnecessary open/seek/read operations without changing tensor identity or execution order.

The plan may reorder host-side tensor reads, but must not reorder model computation.

Include static memory-budget estimates for S0 bring-up, clearly marked as estimates rather than measured GPU evidence.

Do not designate final scientific profiling targets in this CPU stage. You may identify bring-up/canary layers such as early/middle/late layers, but classify them as `PROVISIONAL_CANARY_ONLY`.

---

# F. Tensor materializer implementation

Implement a reusable materializer that can, from the exact local/canonical safetensors authority:

```text
select a complete module/layer tensor set
validate expected names/shapes/dtypes
locate source shard for every tensor
load tensors to a caller-selected device/dtype without silent conversion
report exact bytes loaded
fail on missing/unexpected/duplicate tensor identity
release materialized state explicitly
```

CPU tests may use tiny synthetic safetensors fixtures.

Do not load the complete 61 GB model into RAM merely to test the loader.

The production code must support a future node109 path where the source is the local working copy, not SSHFS.

---

# G. Semantic streaming runner structure

Prepare the actual orchestration code that node109 will later execute.

The runner should support the intended sequence:

```text
embedding
-> decoder layer 0
-> ...
-> decoder layer 47
-> final norm / lm_head
```

and decode state flow:

```text
per-layer past KV state
-> materialize current layer + its KV
-> exact layer execution
-> store updated KV state
-> release layer/KV from active device
-> next layer
```

Preserve interfaces for:

```text
hidden_states
attention mask
position_ids/cache_position
past_key_values / cache object semantics
router outputs
expert assignments
RNG state if relevant
```

The implementation must call the exact runtime's model/layer code rather than reproduce Qwen3 math manually.

GPU-specific execution may remain untested in this Goal, but the code path should be real production code rather than a placeholder/stub.

---

# H. Tiny-model CPU equivalence regression

Build a small deterministic Qwen3-MoE fixture using the same pinned runtime implementation but tiny dimensions, for example a few layers/experts and a small vocabulary.

The exact tiny config may be chosen by Codex as long as it exercises:

```text
Qwen3 MoE router/top-k
expert dispatch/combine
attention
KV cache / decode path
residual/norm path
```

Use fixed seed and CPU-only execution.

Create two paths from the same exact tiny-model weights:

```text
A. ordinary monolithic runtime execution
B. the new streaming/materialization path
```

Required tests:

1. Prefill equivalence.
2. At least one decode step using cache/KV state.
3. Router selected expert ids exactly match.
4. Expert token counts exactly match.
5. Output shapes/dtypes match.
6. Output numerical equivalence under an explicit deterministic CPU rule.
7. Freeze a tiny TARGET_LAYER_STATE and replay the complete layer independently.
8. Replayed layer output matches the source streaming layer under the same rule.

Prefer exact equality where deterministic CPU execution permits it. If tolerance is needed, record the exact reason and bound; do not hide it behind a generic loose `allclose`.

This regression is engineering validation only and is not Qwen3-30B scientific evidence.

---

# I. TARGET_LAYER_STATE schema V1

Implement and document the future real-state bundle format.

The manifest must bind at least:

```text
schema_version
model_id
model_revision
runtime/deployment receipt SHA
input binding receipt SHA
scenario
phase = PREFILL or DECODE
layer_id
decode_step if applicable
hidden_states artifact + SHA + shape + dtype
attention-mask identity/artifact
position_ids/cache_position identity/artifact
layer-local KV artifact(s) + SHA + shape + dtype when applicable
router/expert validation summary
RNG state/identity if relevant
source semantic-run receipt SHA
source layer-output fingerprint
bundle created_at_utc
```

Use atomic construction semantics such as `.partial` -> validate -> no-overwrite promotion for real bundles.

Provide validator code that rejects:

```text
missing artifact
SHA mismatch
wrong model/revision
wrong layer/scenario
shape/dtype mismatch
unexpected schema version
partial/incomplete bundle
```

Test the serializer/validator with CPU synthetic tensors.

---

# J. Exact-layer replay harness structure

Prepare the replay harness that will later:

```text
load one full exact layer, including all 128 experts
restore TARGET_LAYER_STATE
run the complete runtime layer
capture output/router summaries
compare against source streaming execution
```

The CPU stage only validates this harness with the tiny Qwen3-MoE fixture.

Do not reduce expert count in the future real Q30 replay path.

Freeze a replay comparison policy:

```text
shape/dtype exact
router selected expert ids exact
expert token counts exact
output bitwise hash preferred when deterministic
any non-bitwise fallback requires explicit documented justification and a predeclared strict bound
```

Do not silently downgrade the replay gate.

---

# K. Node109 runtime bootstrap and working-copy provisioning tools

Prepare, but do not execute on node109:

1. A node109 runtime bootstrap recipe/script that creates a separate Q30 environment and never mutates `/data/c16/env/c16-py310` in place.
2. A resumable working-copy provisioning/verification tool consuming `Q30_NODE109_PROVISIONING_MANIFEST.tsv`.

Provisioning semantics must be:

```text
node164 canonical source
-> <revision>.partial
-> resume-capable copy
-> independent destination file-set/size/SHA validation
-> no-overwrite final promotion
```

Test provisioning logic only on small temporary synthetic directories on 174-new.

Do not contact or modify node109 in this Goal.

The final scripts must default to fail-closed behavior and support an explicit `--dry-run`/plan mode where appropriate.

---

# L. CLI and reproducibility

Provide compact CLI entry points sufficient for the later node109 operator to perform at least:

```text
validate-authority
validate-runtime-map
show-layer-plan
verify-working-copy
run-streaming   (implemented but not exercised on Q30 GPU here)
freeze-target-state
validate-target-state
replay-layer
```

Names may differ, but capabilities must be clear and documented.

Every production command must emit enough identity metadata to bind:

```text
model revision
runtime/deployment
input binding
Git commit
scenario/layer/phase
```

---

# M. Tests

Add automated CPU-only tests.

Minimum test classes:

```text
control-pack authority parser/validation
18,867 layout integrity checks
48-layer plan integrity
synthetic safetensors materialization
missing/duplicate/wrong-shape fail-closed cases
meta-model runtime/index name compatibility
TARGET_LAYER_STATE serialization/validation
atomic partial/final state handling
tiny Qwen3-MoE prefill streaming equivalence
tiny Qwen3-MoE decode/KV equivalence
tiny exact-layer replay equivalence
provisioning synthetic resume/hash/collision tests
```

Tests must not require a GPU.

---

# N. Required review pack

Create:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_CPU_STREAMING_IMPL_PREP_174NEW_V1/
```

Include at least:

```text
README.md
UPSTREAM_AUTHORITY.tsv
CPU_RUNTIME_LOCK.json
META_MODEL_COMPATIBILITY.tsv
LAYER_MATERIALIZATION_SUMMARY.tsv
SHARD_ACCESS_SUMMARY.tsv
STATIC_MEMORY_BUDGET.md
STREAMING_CODE_INDEX.tsv
TARGET_LAYER_STATE_SCHEMA.json
REPLAY_EQUIVALENCE_POLICY.json
TINY_MODEL_EQUIVALENCE.tsv
CPU_TEST_MATRIX.tsv
NODE109_RUNTIME_BOOTSTRAP.md
NODE109_PROVISIONING_TOOL_STATUS.tsv
OPEN_ISSUES.md
FINAL_DECISION.json
SHA256SUMS
```

The review pack must identify all source-code files added/modified and the exact test command/output summary.

---

# O. Acceptance criteria

PASS requires all of the following:

```text
upstream asset/control authorities still verify
CPU meta-model/runtime mapping closes or every non-checkpoint state is explicitly justified
48 exact layer materialization plans generated
real shard-aware materializer implemented
real streaming orchestration code implemented
TARGET_LAYER_STATE schema + validator implemented
exact-layer replay harness implemented
tiny Qwen3-MoE prefill equivalence PASS
tiny Qwen3-MoE decode/KV equivalence PASS
tiny complete-layer replay equivalence PASS
node109 runtime bootstrap prepared but not executed
working-copy provisioner prepared/tested only on synthetic data
all CPU tests PASS
no node109 writes
no GPU workloads
```

Successful final state:

```text
Q30_CPU_STREAMING_IMPLEMENTATION_PREP_PASS
GPU_VALIDATION_NOT_STARTED
```

This is **not** equivalent to:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

That later status requires node109 S0 semantic streaming plus real exact-layer replay canaries.

---

# P. Failure/recovery policy

Treat normal implementation bugs as recoverable sub-goals and continue iterating.

Do not STOP merely because:

```text
an isolated Python environment needs a different compatible pinned package version
one synthetic test exposes a loader/state bug
meta-device construction needs a runtime-specific adapter
state serialization needs repair
```

STOP/fail-closed only for substantive authority problems such as:

```text
canonical asset invalidated
accepted 18,867 tensor layout no longer reconciles with exact runtime in a way that cannot be explained
frozen input authority corrupted
runtime semantics require changing the model identity
```

Do not weaken scientific constraints just to obtain PASS.

Commit, push, report final branch/commit/status/review-pack path, then STOP.
