# CODEX 109 — C16 Pre-Capture Target Planning V1

Ownership: ChatGPT
Execution node: 109 / RTX4080
Status: may run now in parallel with 174-new data-pipeline integration

## Goal

Prepare a high-quality, executable multi-model trace campaign so that once Pipeline V1 is qualified, formal NVBit/NCU capture can begin immediately and finish within a few hours for all RTX4080-admitted deployments.

This round is NOT the formal trace campaign. It is target selection, resource admission, lightweight runtime census, and capture-plan freeze.

## Read first

```text
docs/vm_tlb/chatgpt_handoff/c16/trace_campaign/TRACE_QUALITY_CONTRACT_V1.md
```

Also review the frozen RTX3090 lessons at commit:

```text
649af1b9d65a774d4aa8c32a15f9b6f4da0dd4d9
```

especially:

```text
Q2_ANCHOR_MEMORY_CHARACTERIZATION_V1.md
ROUTE_B_SELECTION_SENSITIVITY_V1.json
ROUTE_B_Q2_BRIDGE_CLOSEOUT_V1.json
```

The point is to avoid selecting a valid but scientifically weak anchor again.

## Branch/worktree

Create a fresh branch/worktree. Suggested branch:

```text
hrl/c16-trace-campaign-precapture-109-v1
```

Do not modify ChatGPT-owned handoff files.

## Part A — exact asset / input / environment inventory

Inventory the live 109 state without moving data.

Models of interest:

```text
Llama-3.2-1B
Qwen2.5-0.5B-Instruct
Qwen2.5-7B-Instruct raw
Qwen2.5-7B-Instruct-AWQ
Qwen3-8B
DeepSeek-V2-Lite
```

For each record:

```text
model_id
revision
live path
payload bytes
asset receipt path/SHA
weight format / declared dtype
config essentials
historical input-binding status
available scenario IDs
```

For Qwen2.5 0.5B/raw/AWQ, independently inventory the seven transferred historical bindings under `/data/c16/inputs/.incoming/...` and their transfer receipts.

For Qwen3-8B and DeepSeek, preserve `NO_HISTORICAL_FROZEN_BINDING`; do not create new tokens in this round.

## Part B — RTX4080 resource admission

Do not assume a model fits from file size alone.

Admission policy:

```text
NO CPU offload
NO device_map auto spilling
NO dtype substitution to make it fit
NO scenario shortening to make it fit
NO backend substitution unless separately declared as a different deployment
```

For each candidate deployment, start from S0 or the smallest valid frozen scenario and record:

```text
load PASS/OOM
peak allocated/reserved GPU memory
post-load free memory
runtime dtype
attention backend
output checksum/status
```

Classify:

```text
ADMITTED_4080
NOT_ADMITTED_MEMORY
NOT_ADMITTED_RUNTIME
UNKNOWN_NOT_ATTEMPTED
```

Expected priority:

```text
Qwen2.5-0.5B first
Qwen2.5-7B-AWQ second
Qwen2.5-7B raw admission attempt only after the first two
Qwen3-8B / DeepSeek only bounded admission attempts if safe and meaningful
```

Fail closed on OOM; do not keep retrying with changed scientific configuration.

## Part C — cheap native + NSYS census

For every `ADMITTED_4080` deployment, run lightweight native/NSYS census on frozen scenarios needed to answer implementation/shape questions.

At minimum prioritize:

```text
S0_TEXT        canary only
S1_CODE        B1 T256 D16
S2_CODE        B1 T2048 D32
S2_STRUCTURED  B1 T2048 D32
S2_TEXT        B1 T2048 D32
S3_TEXT        B1 T8192 D16 (only if resource-admitted)
S4_STRUCTURED  B4 T2048 D16 (only if resource-admitted)
```

Do not blindly repeat scenarios if a prior run in this round proves exact runtime signature equivalence and there is no scientific value; document any skipped duplicate.

The launch catalog must record at least:

```text
model/deployment
scenario
phase (Prefill / Decode)
decode_step where identifiable
launch ordinal
exact function name
code-object identity where available
grid/block
stream
duration
phase duration share
implementation signature
```

Use NVTX/runner evidence when available to classify semantic strata conservatively:

```text
ATTENTION_PROJECTION
ATTENTION_CORE
FFN_DENSE
EMBEDDING_OUTPUT
KV_MANAGEMENT
QUANT_DEQUANT
NORM
ROPE
OTHER_COMPUTE
UNKNOWN
```

UNKNOWN must remain UNKNOWN if unsupported.

## Part D — static memory-reference map

For the important launch classes found in Part C, build an RTX4080-local static memory-reference map.

For each candidate function record:

```text
full function identity
code-object SHA/identity
static instruction index/offset
opcode
GLOBAL/other memory space
load/store/atomic
width
MREF ordinal/count
```

No 3090 static index may be reused as authority.

## Part E — bounded NCU candidate characterization

Use NCU only on a bounded candidate set sufficient for target ranking.

Freeze the exact metric list before collection.

Record memory-relevant metrics available on the RTX4080, prioritizing:

```text
L1/TEX traffic
L2 traffic
DRAM bytes/throughput
selected memory stall/exposure metrics
```

Do not profile every launch. Profile candidate strata/launches that are plausible formal trace targets.

## Part F — trace portfolio selection

For each admitted deployment, produce a formal candidate portfolio of approximately 4–6 targets, not one target.

Selection must follow `TRACE_QUALITY_CONTRACT_V1.md`.

Required portfolio roles when present:

```text
1. FFN/GEMM heavy target
2. Attention projection or equivalent
3. Attention core / score/value target
4. Decode KV-facing / KV management target
5. deployment-specific special target:
   - QUANT_DEQUANT for AWQ
   - EMBEDDING_OUTPUT or other special memory kernel otherwise
6. RANDOM_AUDIT / low-mass audit target
```

A target must include a specific phase/scenario/launch binding.

For decode KV-growth studies, nominate early and late decode-step instances when the same class appears across steps.

For each selected target record:

```text
target_id
scientific role
model/revision
scenario
phase/decode_step
function/code-object
launch selector
static MREF set to capture
phase duration share
stratum duration mass
NCU memory evidence
expected raw-size class
expected runtime bound
object-map requirement
fallback if target identity changes
```

## Part G — formal capture matrix freeze

Produce a single executable matrix for the next round:

```text
CAPTURE_CAMPAIGN_V1.tsv
```

with statuses:

```text
READY_FOR_FORMAL_TRACE
READY_FOR_NCU_ONLY
CANARY_ONLY
DEFER_RESOURCE
REJECT_WEAK_TARGET
```

The matrix must be small enough that the first RTX4080 formal campaign can finish in a few hours.

Default limits:

```text
4–6 NVBit targets per admitted deployment
<= 4 GiB or <= 20 min per target
<= 64 GiB total first-campaign raw budget
```

## Part H — time/cost estimate

Based on measured native/NSYS/NCU timings, estimate wall-clock for the formal campaign:

```text
per model
per scenario
per NVBit target
transfer overhead
expected total
```

Give best/expected/worst bounded estimates.

## Explicitly forbidden in this round

```text
formal large NVBit capture
ad-hoc arbitrary static-instruction trace collection
new Qwen3/DeepSeek tokenization
CPU offload
model mutation
changing dtype/backend to avoid OOM
scientific raw transfer to 174-new outside Pipeline V1
claiming one target represents a whole phase/model
```

A tiny NVBit no-match/identity canary is allowed only if necessary to prove exact target binding, and must be classified DIAGNOSTIC.

## Deliverables

Suggested review pack:

```text
docs/vm_tlb/review_packs/C16_TRACE_CAMPAIGN_PRECAPTURE_109_V1/
```

Must include:

```text
README.md
MODEL_RESOURCE_ADMISSION.tsv
INPUT_BINDING_INVENTORY.tsv
SCENARIO_RUNTIME_MATRIX.tsv
KERNEL_LAUNCH_CATALOG.tsv
SEMANTIC_STRATA.tsv
STATIC_MREF_MAP.tsv
NCU_CANDIDATE_METRICS.tsv
TRACE_TARGET_CANDIDATES.tsv
CAPTURE_CAMPAIGN_V1.tsv
CAMPAIGN_TIME_BUDGET.md
REJECTED_TARGETS.tsv
OPEN_ISSUES.md
SHA256SUMS
```

## Acceptance criteria

PASS only if:

```text
ASSET_IDENTITY_PASS
INPUT_AUTHORITY_PASS
RESOURCE_ADMISSION_CLOSED
RUNTIME_CENSUS_PASS
PHASE_DURATION_DENOMINATORS_CLOSED
STATIC_MAP_4080_LOCAL_PASS
TARGETS_NOT_CANARY_ONLY_PASS
PORTFOLIO_COVERAGE_DECLARED
TRACE_BOUNDS_DECLARED
FORMAL_CAPTURE_MATRIX_FROZEN
CAMPAIGN_TIME_BUDGET_BOUNDED
```

If an important duration stratum cannot be exactly mapped, mark the selection blocked/partial for that stratum rather than substituting an easy kernel.

## STOP

STOP after the formal campaign matrix is frozen and pushed.

Do not start the large formal NVBit campaign until ChatGPT reviews the target matrix and Pipeline V1 has passed.