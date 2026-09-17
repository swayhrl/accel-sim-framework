# CODEX_NEXT_STAGE — 109 Qwen2.5 S2 kernel census V1

Status: **ACTIVE**

Task:

```text
AWMA_QWEN25_S2_KERNEL_CENSUS_V1
```

Node:

```text
109 / NVIDIA RTX4080 16GB
Native producer / real-GPU workload owner
```

## Objective

Build a complete lightweight CUDA-kernel launch inventory for the frozen Qwen2.5 workload, then determine how representative Q05 is within Prefill Attention and within the full run.

This task does **not** capture detailed SASS traces for all kernels.

Answer:

1. total kernel launches for the complete B1/T2048/Decode32 run;
2. Prefill versus Decode launch counts and GPU-time shares;
3. Attention-related semantic kernel families and exact CUDA implementations;
4. exact/normalized `flash_fwd` occurrence counts;
5. whether Q05 occurrence 0 is typical in function, launch shape and duration;
6. whether Q05 can represent its FlashAttention family, the broader Attention computation, or the whole model.

## Required read order

Fetch:

```text
hrl/awma-q05-representativeness-handoff-v1
```

Read:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
this file
```

Create a fresh execution branch/worktree from the coordination branch, recommended:

```text
hrl/awma-qwen25-s2-census-109-v1
```

Do not modify the frozen simulator-native producer worktree or accepted capture branch.

## Frozen workload identity

Do not change:

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
batch      = 1
input      = TEXT
prefill    = 2048 tokens
decode     = 32 tokens
dtype      = FP16
backend    = SDPA
scenario   = S2_TEXT
```

Use the already frozen input/token identity from the accepted AWMA workflow.

Do not silently retokenize a different prompt or alter batch, sequence length, dtype, attention backend, decode length or model revision.

Q05 reference identity:

```text
Q05_PREFILL_ATTN_FLASH
function occurrence = 0
pytorch_flash::flash_fwd_kernel<...>
```

## D0 — reuse existing accepted evidence first

Before running the GPU, search existing accepted material on:

```text
109 local storage
node164 durable storage
Git review packs
Native catalogs
NSYS reports
kernel semantic sidecars
```

Look specifically for the exact frozen workload identity and a complete Prefill + Decode32 per-kernel launch list containing enough of:

```text
launch order
kernel name
start/end/duration
grid/block
phase information
```

If complete accepted data already exist, classify:

```text
REUSE_EXISTING_ACCEPTED_CENSUS
```

and perform the analysis without rerunning the GPU.

Record the reused run identity, hashes and why its workload identity is exact.

Do not rerun merely to produce prettier files.

## D1 — only if needed, run one lightweight NSYS inventory

If existing accepted data are insufficient, first obey the current 109 GPU lock/campaign rules and do not interrupt another formal run.

Use the existing verified Qwen2.5 runner and frozen input for exactly:

```text
B1 / TEXT / Prefill2048 / Decode32 / FP16 / SDPA
```

Capture only lightweight information sufficient for a complete kernel-call inventory:

```text
CUDA kernel activities
CUDA runtime launch metadata if needed
existing NVTX ranges if available
```

Prefer profiling only the inference region rather than model download/load/tokenizer initialization.

This stage explicitly forbids:

```text
NCU
NVBit Native memory tracing
C16WARP1 detailed capture
simulator-native tracer
new complete SASS trace capture
```

If NSYS alone cannot provide a semantic field, leave it unknown or use an already trusted runtime/NVTX mapping. Do not escalate to detailed tracing without ChatGPT review.

## D2 — per-launch inventory

For every kernel launch, emit at least:

```text
global launch index
phase = PREFILL or DECODE
decode step if provable
exact kernel name
demangled kernel name
normalized kernel family
grid
block
stream if available
start timestamp
end timestamp
duration
```

Add these only where provenance supports them:

```text
Transformer layer
semantic operator
shape
dtype
```

Do not infer Q/K/V projection or layer ID purely from launch order or a mangled symbol.

Use:

```text
UNKNOWN
```

where semantic attribution is not proven.

## D3 — semantic/family normalization

Create a reproducible mapping into at least:

```text
ATTENTION_PROJECTION
ATTENTION_CORE
ATTENTION_OUTPUT
ROPE
NORM
MLP
ELEMENTWISE
COPY_LAYOUT
KV_MANAGEMENT
OTHER
UNKNOWN
```

Preserve two separate levels:

1. semantic category;
2. exact implementation / normalized CUDA kernel family.

Document every normalization rule. Do not merge distinct implementations only because names look similar.

## D4 — frequency and GPU-time statistics

Compute separately for:

```text
whole frozen scenario
Prefill
Decode total
per Decode step where available
Attention-related subset
```

For every category/family report:

```text
launch count
launch-count share
total GPU duration
GPU-time share
mean duration
median duration
min/max duration
p25/p75 duration
```

Both launch-count share and GPU-time share are required. Do not use one as a substitute for the other.

## D5 — Attention structure

Produce a focused Prefill/Decode Attention inventory and answer:

1. how many Attention-related launches occur in Prefill;
2. how many semantic families are present;
3. how many exact/normalized CUDA implementations are present;
4. which launches can be reliably classified as projection, RoPE/auxiliary, Attention core, output projection, layout/copy or other;
5. how many `flash_fwd` launches occur in Prefill;
6. whether Decode Attention uses the same implementation family or a different one.

Unknown mappings remain `UNKNOWN`.

## D6 — Q05 representativeness

Use Q05 occurrence 0 as the reference.

At minimum report:

```text
exact flash_fwd function launch count
normalized FlashAttention-family launch count
Prefill ATTENTION_CORE launch count
Q05 duration
same-family mean/median/min/max/p25/p75 duration
same exact grid/block count
other grid/block variants
```

Calculate:

```text
Q05 single-launch GPU-time share of Prefill
FlashAttention-family GPU-time share of Prefill
Attention-related GPU-time share of Prefill
```

List all later occurrences of the exact Q05 function and compare:

```text
exact function identity
grid/block
duration
phase
```

If trusted layer mapping exists, additionally report which layers use which FlashAttention implementation.

If trusted layer mapping does not exist, report:

```text
LAYER_MAPPING_NOT_PROVEN
```

Do not mechanically map N similar launches to N model layers based only on model configuration.

## D7 — cross-check with historical Q05 identity

Verify that the launch labeled as `function occurrence 0` in this inventory closes against the already accepted Q05 identity in:

```text
model/revision
scenario/phase
function
occurrence
dtype/backend
launch characteristics where available
```

Do not use a historical dynamic kernel number as the scientific identity. Dynamic numbering can change across runs.

## Required conclusion classes

The report may classify Q05 as:

```text
REPRESENTATIVE_WITHIN_SAME_FLASH_FAMILY
PARTIALLY_REPRESENTATIVE
SPECIAL_CASE
INSUFFICIENT_SEMANTIC_MAPPING
```

Do not force a favorable representativeness result.

The report must separately answer:

- representativeness within the same exact/normalized FlashAttention family;
- representativeness for the broader Attention computation;
- representativeness for the entire model run.

These are different claims.

## Storage

Keep large `.nsys-rep`, exports and raw launch tables on node164 under a dedicated durable directory derived from the existing storage contract.

Do not invent a new storage root and do not commit large raw reports to Git.

Git stores compact summaries, schemas, manifests, hashes and indexes.

## Deliverables

Report:

```text
docs/vm_tlb/codex_handoff/awma/
QWEN25_S2_KERNEL_CENSUS_109_V1_REPORT.md
```

Review pack:

```text
docs/vm_tlb/review_packs/
AWMA_QWEN25_S2_KERNEL_CENSUS_109_V1/
```

At minimum include:

```text
README.md
SOURCE_ANCHORS.md
WORKLOAD_IDENTITY.json
ALL_KERNEL_LAUNCHES.tsv
KERNEL_FAMILY_SUMMARY.tsv
SEMANTIC_KERNEL_SUMMARY.tsv
PHASE_SUMMARY.tsv
ATTENTION_KERNEL_SUMMARY.tsv
FLASH_ATTENTION_OCCURRENCES.tsv
Q05_REPRESENTATIVENESS.md
RAW_DATA_INDEX.tsv
RUN_RECEIPT.json
SHA256SUMS
```

If `ALL_KERNEL_LAUNCHES.tsv` is too large for normal Git hygiene, keep it on node164 and commit a compact index plus deterministic summary; document the choice.

## Execution policy

Routine engineering problems are solve-and-continue:

```text
NSYS export/parsing
NVTX parsing
kernel demangling
Python analysis
paths
Git
schema formatting
```

Stop for scientific review if:

- frozen workload identity cannot be recovered;
- model revision differs;
- dtype/backend/context/decode length would need to change;
- Q05 identity cannot be closed against accepted evidence;
- the only way to answer the core question would require NCU/NVBit/full detailed trace capture;
- another formal GPU campaign prevents a safe run and no accepted existing inventory is available.

## STOP boundary

Success marker:

```text
AWMA_QWEN25_S2_KERNEL_CENSUS_V1_COMPLETE_WITH_SCOPE
```

Then:

```text
review pack
report
hashes
commit
push
remote verify
clean worktree
STOP
```

Do not automatically start simulator-native capture of additional kernels. The next target set must be chosen only after ChatGPT reviews this result together with the 174-new Q05 translation-behavior report.
