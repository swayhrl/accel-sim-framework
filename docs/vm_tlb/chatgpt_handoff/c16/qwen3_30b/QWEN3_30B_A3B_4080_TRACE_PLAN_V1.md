# C16 Qwen3-30B-A3B on RTX4080: High-Quality NCU/NVBit Plan V1

Status: **PLANNING_ONLY / NOT YET AUTHORIZED FOR EXECUTION**

This document freezes the proposed scientific and engineering route for characterizing `Qwen/Qwen3-30B-A3B@ad44e777bcd18fa416d9da3bd8f70d33ebb85d39` when the full BF16 model cannot reside on the RTX4080.

The core idea is:

> **Do not shrink the model to fit the GPU. Decouple semantic execution from simultaneous weight residency. Use exact layer streaming to reconstruct the original model state, then replay exact target layers/kernels on the RTX4080 for high-quality NCU and NVBit capture.**

This is not intended to produce full-model end-to-end performance numbers on the RTX4080. It is intended to produce high-quality, provenance-closed **kernel-local / layer-local memory evidence** for TLB/cache characterization.

---

## 1. Current asset state and execution boundary

Expected source payload after the current download finishes:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/
```

Expected model identity:

```text
model_id:
Qwen/Qwen3-30B-A3B

revision:
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Current reported checkpoint size is approximately 61 GB across 16 shards.

Do not start the execution plan in this document until:

1. all model shards are complete;
2. each shard is receipt/SHA closed;
3. the full model asset inventory is closed;
4. the model is copied to node164 as a canonical asset;
5. the source and node164 inventories match exactly.

The intended canonical archive path is:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
assets/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

The canonical archive should use the same model-asset rules already used for the six existing C16 canonical model archives:

```text
.partial copy
→ independent destination inventory
→ exact relative-path/size/SHA equality
→ MODEL_ARCHIVE_RECEIPT.json
→ no-overwrite promotion
```

After archival, provision a local working copy to node109 SSD for execution. Do not execute large repeated layer loads directly over SSHFS.

Suggested node109 working path:

```text
/data/c16/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

---

## 2. Scientific objective

The objective is not simply to "make Qwen3-30B run".

The objective is to obtain high-quality, exact-identity evidence for representative Qwen3-30B-A3B memory behaviors, especially:

```text
Attention / KV access
Router behavior
MoE expert weight access
Expert token distribution
Prefill vs Decode
Context scaling
Active-expert working-set scaling
4K / 64K page footprint
128B line footprint
Object composition
NCU L1/L2/DRAM traffic
```

The evidence should be suitable for cross-model C16 comparisons with:

```text
Llama-3.2-1B
Qwen2.5-0.5B
Qwen2.5-7B raw
Qwen2.5-7B AWQ
Qwen3-8B
DeepSeek-V2-Lite
```

but the final claim scope for RTX4080 layer replay must remain explicit.

---

## 3. Why full-model residency is not required

The checkpoint is much larger than RTX4080 memory, but Qwen3-30B-A3B is a layered MoE model.

Planning assumptions to verify from the archived `config.json` before execution include:

```text
~48 decoder layers
128 experts / MoE layer
top-8 experts / token
hidden size around 2048
MoE intermediate size around 768
```

These constants are planning assumptions only. The execution implementation must re-read and hash the actual archived config and must not silently rely on this document if the config differs.

The key observation is that a **single decoder layer**, including all experts of that layer, is far smaller than the full model and is expected to fit comfortably in 16 GB.

Therefore:

```text
full model simultaneous residency
    is not required for
exact per-layer mathematical execution
```

provided that:

1. original BF16 weights are used;
2. original layer implementation is used;
3. exact hidden state entering each layer is preserved;
4. exact position / attention / KV state is preserved;
5. routing is computed by the original router;
6. all experts needed by that layer are available;
7. no model architecture, precision, context, batch, backend or routing semantics are changed.

---

# 4. Core execution architecture

The plan is split into two distinct modes.

## 4.1 Mode A — Semantic Layer Streaming

Purpose:

> Reconstruct the exact original full-model semantics without requiring all model weights to be resident on the GPU simultaneously.

Conceptually:

```text
Embedding
   ↓
Layer 0 weights → GPU
Layer 0 exact execution
Layer 0 weights released
   ↓
Layer 1 weights → GPU
Layer 1 exact execution
Layer 1 weights released
   ↓
...
   ↓
Layer N-1
   ↓
Final norm / lm_head
```

This pass is allowed to use host-side storage to hold inactive layer weights and non-target KV state because **Mode A is not itself used for GPU memory characterization**.

Its scientific purpose is to reconstruct:

```text
exact hidden states
exact router decisions
exact expert token assignments
exact target-layer input state
exact layer-local KV state
exact decode-step state
```

Mode A performance, memory bandwidth and GPU allocator behavior are explicitly **not** formal full-model performance evidence.

### Required output from Mode A

For selected candidate target layers / steps, freeze a `TARGET_LAYER_STATE` containing at least:

```text
model revision
runtime revision
scenario binding
phase
layer id
decode step if any
input hidden_states bytes/hash
attention mask identity
position ids / cache position
layer-local past KV bytes/hash if applicable
router logits/results if captured for validation
expert assignment summary
RNG state if relevant
```

The state snapshot must be sufficient to reproduce the exact selected layer execution independently.

---

## 4.2 Mode B — Exact Target Layer Replay

Purpose:

> Recreate the selected original model layer on the RTX4080 with original weights and exact input state, then capture NCU/NVBit evidence only from representative kernels.

For each target:

```text
load exact target layer weights
+ restore exact TARGET_LAYER_STATE
+ instantiate exact runtime implementation
+ execute full layer
+ validate output equivalence
+ profile selected kernel(s)
```

The target replay must execute the **full layer context**, not merely invoke a standalone GEMM with synthetic inputs, unless a separate micro-harness is explicitly classified as diagnostic.

This ensures that:

```text
Norm
Attention
Residual
Router
Dispatch
Expert computation
Combine
```

are generated by the same runtime path that would be used in the full model.

---

# 5. Runtime authority

Qwen3 runtime behavior can change substantially across framework versions and MoE implementations.

Therefore the runtime is part of deployment identity.

The first deployment should be conservative and explicit, for example:

```text
qwen3_30b_a3b_hf_baseline_bf16
```

Before execution, freeze:

```text
Python version
PyTorch version
CUDA runtime
Transformers version
safetensors version
attention backend
MoE implementation path
BF16 dtype
use_cache behavior
kernel extension state
```

Do not mix results from:

```text
HF eager expert execution
grouped_mm
Triton fused MoE
vLLM fused MoE
SGLang fused MoE
GPTQ
AWQ
```

under one deployment label.

Each materially different runtime path is a separate C16 deployment.

If the archived model config indicates a historical/reference Transformers version, prefer establishing the first baseline in an isolated environment close to that runtime rather than modifying the already-qualified Qwen2 environment.

Suggested isolated environment namespace:

```text
/data/c16/env/qwen3_30b_hf_baseline/
```

Do not destabilize the current Qwen2/Llama runtime used by other C16 work.

---

# 6. Exact per-layer weight loading

Use the checkpoint index to map tensor names to safetensors shards.

Do not load the entire 61 GB checkpoint into host RAM just to extract one layer.

Implement a deterministic tensor loader:

```text
checkpoint index
   ↓
required tensor names for target layer
   ↓
safetensors safe_open / mmap
   ↓
load only required tensors
   ↓
copy exact tensors to GPU module
```

For each layer load, record:

```text
layer id
parameter name
source shard
source tensor dtype
shape
byte count
tensor SHA or source-file+offset identity where practical
```

The loader must fail closed if:

```text
missing tensor
unexpected tensor
shape mismatch
dtype mismatch
revision mismatch
```

---

# 7. MoE-specific semantic requirements

Do not approximate the MoE layer by replacing it with a dense block.

Do not prune experts merely to fit the GPU.

Do not preselect experts using a different router.

For an exact target layer:

1. load the original router;
2. load all experts for that layer if they fit;
3. run the original router on the exact hidden state;
4. preserve the exact top-k expert selections;
5. preserve expert weights and expert-token counts;
6. preserve original dispatch/combine implementation.

If all experts of one layer fit on the RTX4080, this is preferred over dynamic expert streaming inside the target layer because it avoids changing the target layer execution path.

If a single full MoE layer unexpectedly does not fit:

```text
STOP target-layer formalization
```

and separately investigate a semantically exact expert-streaming implementation. Do not silently switch to an approximate/pruned expert set.

---

# 8. Prospective Qwen3 input authority

Qwen3-30B-A3B currently has no historical frozen C16 input binding.

Therefore create a new prospective authority rather than borrowing Qwen2 token IDs.

Suggested scenario family:

```text
S0  B1 T128   Decode4
S1  B1 T256   Decode16
S2  B1 T2048  Decode32
S3  B1 T8192  Decode16
S4  B4 T2048  Decode16
```

Reuse existing C16 source-text classes where scientifically useful:

```text
TEXT
CODE
STRUCTURED
```

but tokenize with the exact archived Qwen3 tokenizer and freeze new token IDs.

Each binding must record:

```text
source text SHA
tokenizer identity/revision
exact token IDs
actual token length
scenario
batch
context
decode length
binding SHA
```

No retokenization after binding freeze.

The first execution can prioritize:

```text
S0 canary
S2_TEXT main target
S3_TEXT long-context control
S4_STRUCTURED batch control
```

rather than mechanically profiling every scenario.

---

# 9. Candidate-layer and target selection

Do not choose a layer or kernel simply because NVBit can instrument it.

Use a cheap semantic/native census first.

For Mode A, collect at least:

```text
per-layer runtime
router expert histogram
active expert count
expert token counts
attention shape
kernel signatures if feasible
```

Select representative layers based on behavior, not fixed layer numbers alone.

Suggested selection logic:

```text
one early layer
one middle layer
one late layer
```

only if their runtime/kernel/routing behavior differs materially.

If many layers are behaviorally equivalent, use:

```text
one representative layer
+ one independent audit layer
```

Possible target strata:

```text
ATTENTION_CORE
ATTENTION_PROJECTION
KV_RELATED
MOE_ROUTER
MOE_DISPATCH_COMBINE
MOE_EXPERT_GEMM
OTHER_HEAVY_MEMORY
```

For each phase, choose targets by:

```text
duration mass
memory relevance
semantic uniqueness
routing relevance
context sensitivity
```

---

# 10. NVBit methodology

The current C16 lesson is that "one easy PC" is not sufficient formal evidence.

Qwen3 target capture should reuse the qualified V2 concept:

```text
MREF_SHARDED_COMPLETE_SET
```

for each exact target kernel/launch.

Required flow:

```text
exact target function/code object
   ↓
RTX4080-local static disassembly
   ↓
all GLOBAL static MREF indices
   ↓
deterministic exact target replay
   ↓
per-MREF shard capture
   ↓
EXECUTED_SHARD / ZERO_EXECUTION_PROVEN
   ↓
complete-set manifest
   ↓
union footprint/object/per-MREF analysis
```

Do not promote a single static MREF canary to whole-kernel formal evidence.

### Formal trace evidence must bind

```text
target-layer-state SHA
layer weight/revision authority
runtime deployment identity
function
code object
launch selector
static MREF complete-set SHA
per-shard binary SHA
terminal status
overflow/drop count
object map SHA
```

### Allowed formal claims from MREF-sharded replay

```text
unique addresses
4K pages
64K pages
128B lines
read/write/atomic mix
per-MREF footprint
object attribution
expert-weight footprint
KV footprint
union footprint
```

### Explicitly forbidden claims

```text
cross-MREF global temporal ordering
cross-shard reuse distance
full-GPU hardware arrival order
full-model L2 state history
full-model TLB state history
```

---

# 11. Address normalization and replay scope

Exact layer replay will generally not reproduce the same absolute virtual address layout that a hypothetical full-resident 80 GB run would have.

Therefore distinguish:

```text
RAW_REPLAY_VA
OBJECT_RELATIVE_OFFSET
PAGE_FOOTPRINT
LINE_FOOTPRINT
```

For cross-run comparisons, prefer:

```text
object-relative offsets
unique page counts
unique line counts
contiguous range structure
object-local page reuse
```

Do not claim that absolute VA placement, allocator placement, TLB set index or cross-object physical placement is identical to a full-resident run unless separately calibrated.

This is a central scientific boundary of the method.

---

# 12. Runtime object map

For each replay build a runtime object map including at least:

```text
WEIGHT
MOE_EXPERT_WEIGHT
ROUTER_WEIGHT
KV_CACHE
ACTIVATION
UNKNOWN_RUNTIME
```

If quantized deployments are added later, extend with:

```text
QUANT_METADATA
```

Record:

```text
address start/end
size
tensor/object name
layer
expert id if applicable
storage identity
alias information
```

Do not force unknown runtime allocations into guessed semantic classes.

`UNKNOWN_RUNTIME` is a valid formal stratum.

---

# 13. NCU methodology

NCU should profile the exact replay application, not a synthetic standalone GEMM whenever possible.

For each selected target, retain two useful views.

## 13.1 Application-context view

Run the full target layer and profile only the selected kernel.

Preferred semantics:

```text
application replay
cache-control none
```

so the target kernel is preceded by the real same-layer operations in each application replay pass.

This gives a useful **same-layer context** measurement.

## 13.2 Cold/isolated control

Optionally capture a cold-cache/control configuration for the same target.

This gives a reproducible comparison point.

Do not interpret either configuration as exact full-model global cache state without an 80 GB calibration run.

### NCU evidence should include

```text
exact argv
metric list
raw .ncu-rep SHA
CSV/export SHA
function identity
launch selector
replay mode
cache-control setting
```

---

# 14. Decode reconstruction

Decode requires special care because target-layer input depends on all preceding generated tokens and all previous layers.

For each required decode step:

1. execute exact prior token steps using semantic layer streaming;
2. maintain each layer's past KV exactly;
3. inactive-layer KV may be stored host-side between uses because Mode A is semantic reconstruction, not profiling;
4. when the target layer is executed, restore its exact layer-local KV on GPU;
5. snapshot the target-layer input state;
6. use that state for exact replay.

Select at least:

```text
early decode
late decode
```

for KV-sensitive targets if the working set changes with decode progression.

Do not assume decode step 1 represents the whole decode phase.

---

# 15. Prefill vs Decode MoE opportunity

This model is particularly useful because MoE active-weight behavior can differ substantially by phase.

Study explicitly:

```text
Prefill:
large token population
→ many expert assignments
→ potentially broad active-expert coverage

Decode B1:
one token per step
→ top-k experts only
→ sparse active expert set
```

Primary C16 questions include:

```text
How does active expert page footprint scale from Decode to Prefill?
How many experts become active as context increases?
Does expert reuse exist across nearby tokens?
How much of the page/line footprint is expert weight vs KV vs attention state?
Does long context shift the dominant pressure from expert weight to KV?
```

---

# 16. Scientific classification of evidence

Do not classify RTX4080 layer replay as full-model full-resident evidence.

Use explicit evidence classes.

Suggested labels:

```text
FORMAL_LAYER_LOCAL
FORMAL_KERNEL_LOCAL
FORMAL_MREF_COMPLETE_SET
DIAGNOSTIC_STREAMING_PASS
CALIBRATED_LAYER_REPLAY
FULL_RESIDENT_CALIBRATION
```

Examples:

```text
Mode A timing:
DIAGNOSTIC_STREAMING_PASS

Exact replay page footprint:
FORMAL_KERNEL_LOCAL / FORMAL_MREF_COMPLETE_SET

NCU layer-context target:
FORMAL_KERNEL_LOCAL

After successful 80GB comparison:
CALIBRATED_LAYER_REPLAY
```

---

# 17. Optional 80 GB calibration stage

For strong paper-level cross-model claims, a later short calibration on an 80 GB GPU is strongly recommended.

The 80 GB GPU is not intended to redo the whole campaign.

Use it only to validate a small number of representative targets, for example:

```text
Prefill Attention
Prefill MoE Expert heavy target
Decode Attention/KV
Decode MoE Expert target
```

Run the original BF16 model fully resident with the same:

```text
model revision
runtime deployment
input binding
scenario
backend
precision
```

Compare RTX4080 exact-layer replay vs 80 GB full-resident execution on:

```text
function/code object
grid/block
static GLOBAL MREF set
normalized page footprint
normalized line footprint
object composition
NCU traffic metrics
router/expert assignment
```

### Calibration outcomes

If the local evidence matches within predefined expected invariants:

```text
LAYER_REPLAY_CALIBRATED
```

may be used for broader kernel-local working-set characterization.

If it does not match:

```text
retain FORMAL_LAYER_LOCAL scope
```

and do not generalize to full-resident global state.

---

# 18. Forbidden shortcuts

The following are **not** acceptable substitutes for the baseline BF16 target deployment:

```text
CPU-offloading one or more model layers during formal target replay
Unified Memory oversubscription for formal memory characterization
expert pruning
reducing number of experts
changing top-k routing
changing dtype
changing context length
changing batch size
changing attention backend
changing MoE implementation silently
using GPTQ/AWQ weights as a replacement for BF16
using Qwen2 token IDs as Qwen3 input authority
using one convenient memory instruction as whole-kernel evidence
```

These may be studied as separate deployments/diagnostics only when explicitly named.

---

# 19. Separate quantized deployment option

A future quantized Qwen3-30B deployment may be scientifically useful because it directly addresses how quantization changes MoE weight working set.

But it must be named separately, e.g.:

```text
qwen3_30b_a3b_gptq_int4
```

or another exact deployment label.

It must not be used to claim BF16 behavior.

A useful future comparison is:

```text
Qwen3-30B-A3B BF16 exact-layer replay
vs
Qwen3-30B-A3B quantized deployment
```

with the same source input binding and scenario.

---

# 20. Data-plane and artifact layout

All new captures must use the qualified C16 Pipeline V1.

Suggested 164 namespace:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/

assets/
  models/qwen3-30b-a3b/<revision>/
  inputs/qwen3-30b-a3b/<binding>/

provenance/
  qwen3_30b/
    runtime/
    layer_state/
    static_maps/
    object_maps/

captures/
  inbox/
  raw/

 derived/
  parsed/
  features/
  datasets/
```

Do not store large formal trace raw in Git.

Git should contain:

```text
schemas
scripts
small manifests
SHA receipts
campaign matrices
review packs
analysis summaries
```

---

# 21. Recommended execution stages

The future execution should be split into clear gates.

## Q30-A — Asset Closeout and Archive

Required:

```text
all shards complete
full source inventory
node164 canonical archive
receipt/SHA closure
node109 local provisioning
```

Decision:

```text
Q30_ASSET_ARCHIVE_PASS
```

## Q30-B — Prospective Input Binding

Required:

```text
Qwen3 tokenizer authority
new exact token-ID bindings
S0/S2 first
S3/S4 as controls
```

Decision:

```text
Q30_INPUT_BINDING_PASS
```

## Q30-C — Semantic Layer Streaming

Required:

```text
exact BF16 layer-by-layer execution
no architecture/routing change
full output/token correctness check
selected layer-state snapshots
router/expert census
```

Decision:

```text
Q30_LAYER_STREAMING_SEMANTIC_PASS
```

## Q30-D — Replay Equivalence

For each selected target layer:

```text
exact state restore
exact layer weights
full layer replay
output equivalence
kernel signature equivalence across repeated replay
```

Decision:

```text
Q30_TARGET_REPLAY_EQUIVALENCE_PASS
```

## Q30-E — NCU Characterization

Required for selected targets:

```text
same-layer application context
bounded NCU metrics
raw report SHA closure
```

Decision:

```text
Q30_NCU_TARGET_PASS
```

## Q30-F — NVBit Formal Trace

Required:

```text
RTX4080-local static map
complete GLOBAL MREF set
MREF-sharded deterministic replay
terminal-close
zero overflow/drop
object map
Pipeline ACK
174-new independent parse/fingerprint
```

Decision:

```text
Q30_NVBIT_FORMAL_LAYER_LOCAL_PASS
```

## Q30-G — Optional 80 GB Calibration

Required only for broader promotion:

```text
full-resident exact model
small representative target set
replay-vs-full-resident comparison
```

Decision:

```text
Q30_LAYER_REPLAY_CALIBRATED
```

---

# 22. Minimum first campaign

Do not start with dozens of targets.

A useful first campaign is:

```text
S2_TEXT Prefill
  1 Attention target
  1 Router/dispatch target
  1 Expert GEMM target

S2_TEXT Decode
  1 Attention/KV early target
  1 Expert GEMM early target
  1 Attention/KV late target
  1 Expert GEMM late target
```

Then add S3 long-context controls only where behavior actually changes.

This is enough to answer whether the method works and whether MoE active-weight/KV footprints are scientifically interesting.

---

# 23. Key acceptance principles

The implementation must optimize for **scientific fidelity**, not for "running somehow".

The following are hard requirements:

```text
exact revision
exact BF16 weights
exact prospective input binding
exact runtime deployment
exact layer state
exact router semantics
exact target function/code object
complete static GLOBAL MREF set
no single-PC substitution
bounded, terminal-closed trace
hash-closed artifacts
Pipeline ACK
independent 174-new recomputation
```

The following are not required for initial success:

```text
full-model residency on RTX4080
full-model RTX4080 latency claim
all 48 layers profiled
all scenarios traced
80GB calibration before any local analysis
```

---

# 24. Final intended claim scope

If Q30-A through Q30-F pass without 80 GB calibration, the valid statement is:

> For exact BF16 Qwen3-30B-A3B layer states reconstructed by semantic layer streaming, representative target layers/kernels were replayed with original weights/runtime on RTX4080 and characterized with complete-set NVBit and NCU under explicit layer-local scope.

The following must not be claimed yet:

> The RTX4080 replay reproduces the exact global cache/TLB state or end-to-end performance of a fully resident 80 GB execution.

If Q30-G calibration later passes, the replay evidence can be promoted to a stronger calibrated scope according to the measured agreement.

---

# 25. Deferred execution trigger

Do not execute this plan merely because this document exists.

Execution begins only after the user reports that the current Qwen3-30B-A3B download is fully complete and the asset is ready for canonical migration.

The intended sequence is:

```text
finish download
→ close source receipts
→ canonical archive to node164
→ provision node109 working copy
→ freeze Qwen3 prospective input binding
→ implement semantic layer streaming
→ qualify exact replay
→ NCU/NVBit formal layer-local campaign
→ optional 80GB calibration
```

Until then this document is the planning authority only.
