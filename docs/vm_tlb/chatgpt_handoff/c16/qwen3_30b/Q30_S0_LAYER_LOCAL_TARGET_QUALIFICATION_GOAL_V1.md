# Qwen3-30B-A3B S0 Layer-Local Target Qualification Goal V1

## Goal mode

Use the accepted exact Layer-24 replay states to identify and freeze a small, scientifically justified portfolio of Q30 CUDA kernel targets for later high-quality NCU and NVBit capture.

This is a **qualification** stage.

It may use bounded NSYS/NCU/NVBit diagnostics, but it must **not** start the large formal trace campaign.

Expected successful final decision:

```text
Q30_S0_LAYER_LOCAL_TARGET_QUALIFICATION_PASS
```

This decision means the target identities/profiling procedure are ready for a later formal capture Goal. It does not mean formal traces are already complete.

---

# 0. Required upstream authority

Scientific execution authority:

```text
branch:
hrl/c16-qwen3-30b-gpu-streaming-replay-109-v1

commit:
ba4358b8059be4fb5756f49852e50ecfe7dea9a3
```

Accepted review pack:

```text
docs/vm_tlb/review_packs/C16_QWEN3_30B_GPU_STREAMING_REPLAY_109_V1/
```

Require its SHA256SUMS to pass before qualification.

Bind these accepted facts:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
Q30_SEMANTIC_STREAMING_S0_PASS
Q30_TARGET_LAYER_STATE_PASS
Q30_EXACT_LAYER_REPLAY_CANARY_PASS
```

Do not regenerate the semantic run or target states unless their preserved authority is invalidated.

---

# 1. GPU ownership and exact runtime

Before every GPU/profiler action:

```text
inspect nvidia-smi
inspect /data/c16/locks/c16_gpu_campaign.lock
acquire the lock normally
verify GPU UUID GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59
```

Never kill or bypass another workload.

Use only the preserved runtime:

```text
/data/c16/env/c16-qwen3-30b-hf451-gpu
```

Do not upgrade packages or change:

```text
BF16
SDPA
128 experts
top-k 8
Transformers 4.51.0
Qwen3Moe implementation
model revision
```

The qualification vehicle is complete Layer-24 replay from the frozen states, not a synthetic GEMM.

---

# 2. Revalidate the two frozen replay states

Before profiling, validate the local state bundles and their manifests/SHA.

Required targets:

```text
PREFILL layer 24
DECODE step 3 layer 24
```

Run one ordinary unprofiled replay for each state and require the accepted replay oracle still closes:

```text
source/replay output exact
router evidence exact
```

This is a bounded resume canary. Do not rerun the whole 48-layer model.

---

# 3. Build a complete kernel-launch census for each full-layer replay

For each of the two exact full-layer replay states, collect a complete GPU kernel launch census from layer entry to layer exit.

Preferred diagnostic vehicle:

```text
Nsight Systems / NSYS
```

if installed and functional.

If NSYS is unavailable, use another non-semantic-changing CUDA/CUPTI launch logging mechanism. Record the fallback explicitly.

Do not use profiler output from a different runtime/deployment.

For every launch record at least:

```text
phase
launch ordinal within exact full-layer replay
kernel/function name
normalized/demangled name where possible
grid
block
duration or diagnostic elapsed estimate
stream
correlation/range identity if available
```

Add semantic-range attribution without modifying Qwen math. NVTX/module hooks may be used around exact runtime components when they do not change computation.

Try to classify launches into:

```text
ATTENTION
KV_OR_POSITION
ROUTER_TOPK
TOKEN_DISPATCH_GATHER
EXPERT_PROJECTION_OR_GEMM
TOKEN_COMBINE_SCATTER
NORM_RESIDUAL
OTHER
```

If exact classification is not provable, use `UNKNOWN_RUNTIME` rather than guessing.

Required output:

```text
PREFILL_KERNEL_CENSUS.tsv
DECODE_KERNEL_CENSUS.tsv
KERNEL_SEMANTIC_CLASSIFICATION.tsv
```

---

# 4. Derive memory-important candidate kernels

From the census, form a bounded candidate set before NCU.

Do not simply pick the longest kernel.

Candidate selection should preserve semantic coverage and prioritize likely memory significance.

Aim for no more than approximately:

```text
4-8 candidate occurrences per phase
```

where justified.

Candidate families should consider:

```text
Attention / KV
MoE expert projection / expert weights
Router/dispatch/combine only if materially GPU-memory relevant
```

Record why each candidate is retained or rejected using descriptive facts:

```text
semantic family
launch ordinal
kernel identity
duration contribution
launch shape
expected object behavior
stability across replay repetitions
```

Do not rank with an opaque score. The objective is a small representative portfolio, not a winner table.

---

# 5. Bounded NCU candidate characterization

Use NCU only on the bounded candidate occurrences from Section 4.

This is qualification evidence, not yet the final formal NCU dataset.

Use fresh exact-layer replay runs and exact launch filtering.

Freeze the actual NCU version and query available metrics first. Do not assume metric names from another GPU/version.

Collect a compact metric set sufficient to distinguish memory behavior, including where available:

```text
kernel duration / cycles
DRAM read/write traffic
L2 read/write traffic or sectors
L1/TEX traffic or sectors
memory-throughput utilization
SM/compute utilization sufficient to distinguish compute-bound vs memory-bound behavior
```

Do not collect an indiscriminately huge metric set that causes excessive replay passes.

For every characterized occurrence bind:

```text
phase
launch ordinal
exact function name
grid/block
NCU filter invocation
actual metric names
metric values
NCU report path/SHA
```

Output:

```text
NCU_CANDIDATE_CHARACTERIZATION.tsv
NCU_METRIC_AUTHORITY.json
```

---

# 6. Freeze exact kernel occurrence identity

For every candidate that remains eligible after census + NCU, define a stable occurrence identity.

It must include at least:

```text
phase
semantic family
exact replay-state manifest SHA
layer = 24
decode step where applicable
kernel/function name
launch ordinal within exact replay
grid/block
runtime source/deployment identity
```

Where tooling permits, also bind:

```text
code object/module identity
function address/handle or equivalent stable runtime identity
```

Do not identify a target solely by a substring kernel name if multiple launches match.

---

# 7. RTX4080-local NVBit static MREF map

For each remaining eligible candidate occurrence, run a bounded NVBit qualification pass that does **not** collect a large dynamic trace.

The purpose is to freeze:

```text
code object / function identity
static GLOBAL memory-reference instructions
operand/read-write metadata where available
static MREF count
instrumentation reachability
terminal completion
```

Reuse the accepted C16 NVBit tooling/methodology where possible.

Do not infer GLOBAL source/destination from address magnitude alone. Use decoded instruction/operand metadata and exact runtime evidence.

If the candidate function contains zero relevant GLOBAL MREFs, mark it accordingly and do not force it into the later trace portfolio.

For each candidate output:

```text
candidate id
function identity
code object identity
static MREF identifiers
instruction text/opcode
read/write classification where supported
GLOBAL qualification basis
NVBit run terminal status
```

Required outputs:

```text
NVBIT_STATIC_MREF_MAP.tsv
NVBIT_QUALIFICATION_SUMMARY.tsv
```

A tiny one-MREF dynamic canary is allowed only to prove instrumentation reachability/terminal closure. Do not yet launch the complete MREF-sharded dynamic trace set.

---

# 8. Freeze the provisional target portfolio

Select a small portfolio for the later formal capture Goal using the evidence above.

Desired semantic coverage, if actually present and stable:

```text
Prefill Attention
Prefill MoE expert-weight path
Decode Attention/KV
Decode MoE expert-weight path
```

Router/dispatch/combine may be added only if census/NCU/static-MREF evidence shows a distinct memory behavior worth characterizing.

It is acceptable for the final portfolio to contain fewer targets if some families are not meaningful/stable.

For each selected target record:

```text
target id
phase
semantic family
exact kernel occurrence identity
census evidence
NCU qualification evidence
NVBit static MREF evidence
scientific reason for inclusion
formal claim boundary
```

Classification at this stage:

```text
QUALIFIED_FOR_FORMAL_LAYER_LOCAL_CAPTURE
```

Do not call the resulting data a formal trace yet.

Required output:

```text
Q30_S0_QUALIFIED_TARGET_MATRIX.tsv
```

---

# 9. Explicit scientific boundaries

This stage is based on:

```text
S0 / B1 / T128
Layer 24 exact replay
```

It can establish exact target identities and profiling feasibility for this deployment/state.

It cannot establish that these launch shapes or expert working sets represent:

```text
S2/T2048
long context
all layers
all routing distributions
full-model resident cache/TLB history
```

The review pack must explicitly recommend whether S2 state generation is required before the formal campaign.

A likely later route is:

```text
S0 target-family qualification
-> generate/validate S2 replay state(s)
-> confirm target-family identity/shape scaling
-> formal NCU + MREF-sharded NVBit portfolio
```

but do not pre-commit to S2 if the actual evidence suggests another better scaling point.

---

# 10. Do not perform in this Goal

Do not:

```text
run full MREF-sharded complete-set traces
collect large NVBit payloads
start a broad formal NCU campaign
expand semantic streaming to S1/S2
change deployment identity
modify frozen replay-state bundles
call qualification outputs final formal scientific traces
make full-model cache/TLB claims
```

Diagnostic NSYS, bounded NCU, static/no-payload NVBit and one-MREF reachability canaries are authorized.

---

# 11. Failure/recovery policy

Recoverable profiler/tooling problems are sub-goals:

```text
NSYS missing -> documented launch-logging fallback
NCU metric unavailable -> query actual metrics and substitute same semantic metric family
kernel-name ambiguity -> use ordinal + grid/block + module/code-object identity
NVBit function ambiguity -> freeze code-object/function/launch identity before instrumentation
profiler perturbation -> use profiler only for qualification; preserve unprofiled replay oracle
```

Do not weaken model/replay identity to obtain profiler data.

If a candidate cannot be uniquely identified or cannot terminal-close under bounded instrumentation, reject that candidate or mark the stage BLOCKED rather than fabricating identity.

---

# 12. Required review pack

Create:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_S0_TARGET_QUALIFICATION_109_V1/
```

Include at least:

```text
README.md
UPSTREAM_AUTHORITY.tsv
PLATFORM_AND_TOOL_AUTHORITY.json
REPLAY_STATE_REVALIDATION.tsv
PREFILL_KERNEL_CENSUS.tsv
DECODE_KERNEL_CENSUS.tsv
KERNEL_SEMANTIC_CLASSIFICATION.tsv
CANDIDATE_SELECTION.tsv
NCU_METRIC_AUTHORITY.json
NCU_CANDIDATE_CHARACTERIZATION.tsv
KERNEL_OCCURRENCE_IDENTITY.tsv
NVBIT_STATIC_MREF_MAP.tsv
NVBIT_QUALIFICATION_SUMMARY.tsv
Q30_S0_QUALIFIED_TARGET_MATRIX.tsv
SCENARIO_EXPANSION_RECOMMENDATION.md
OPEN_ISSUES.md
FINAL_DECISION.json
SHA256SUMS
```

Do not commit large profiler binaries/reports when they are too large for Git. Keep them on the node109 data plane and record path/SHA/size in the review pack.

---

# 13. Final decision

PASS requires:

```text
both replay states revalidated
complete kernel census for both states
bounded NCU characterization of retained candidates
unambiguous occurrence identity for final targets
NVBit static GLOBAL-MREF map for final targets
terminal instrumentation qualification
small evidence-backed target portfolio frozen
```

Successful status:

```text
Q30_S0_LAYER_LOCAL_TARGET_QUALIFICATION_PASS
```

After PASS, STOP.

Do not automatically start the formal NCU/NVBit capture campaign.
