# CODEX NEXT STAGE — 109 Kernel Target Selection V1

## Status

ACTIVE after reading the coordination handoff.

Stage:

```text
AWMA_KERNEL_TARGET_SELECTION_V1
```

Node:

```text
109 / RTX4080
```

This stage is **offline only**. The RTX4080 must remain unused for profiling or detailed capture.

## Start point

Previous accepted census result:

```text
branch = hrl/awma-qwen25-s2-census-109-v1
HEAD   = 678d7b491d4788369ca0c22717453b20846ab195
```

Create a fresh branch/worktree from that commit:

```text
hrl/awma-kernel-target-selection-109-v1
```

Do not modify the previous accepted census worktree.

## Frozen workload identity

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

Accepted census facts:

```text
34,677 total CUDA kernel activities
34,072 inside explicit inference ranges
408 Prefill launches
33,664 Decode launches
1,052 launches per Decode step
```

Important family-level GPU-time results:

```text
Prefill:
CUBLAS_GEMM        70 launches    66.48% GPU time
PYTORCH_FLASH_FWD  10 launches    14.31% GPU time

Decode total:
CUBLAS_GEMV        5,408 launches 49.76% GPU time
PYTORCH_FLASH_FWD  1,536 launches  9.87% GPU time
```

Q05 is already accepted as representative within its repeated Prefill FlashAttention family. This stage is not about re-choosing Q05.

## Objective

Use the existing accepted launch inventory to choose deterministic next simulation/capture candidates for broader AI-workload translation characterization.

At minimum prepare candidates for:

```text
A. dominant Prefill CUBLAS_GEMM behavior
B. dominant Decode CUBLAS_GEMV behavior
C. representative Decode FlashAttention behavior distinct from Prefill Q05
```

No new GPU run or detailed trace capture is authorized.

## D0 — Reuse only accepted census data

Primary source:

```text
docs/vm_tlb/review_packs/AWMA_QWEN25_S2_KERNEL_CENSUS_109_V1/
```

Full launch inventory is on node164 with SHA already recorded in the accepted report/review pack.

Verify:

- inventory path;
- file SHA;
- workload receipt;
- exact inference-range identity.

Do not regenerate the census.

## D1 — Refine implementation-family grouping

For the following families, group launches by the strongest deterministic implementation identity available:

```text
Prefill CUBLAS_GEMM
Decode CUBLAS_GEMV
Decode PYTORCH_FLASH_FWD
```

Prefer grouping key:

```text
exact kernel symbol/demangled implementation
+ grid
+ block
+ other launch-shape fields that are stable and available
```

Keep exact symbol and normalized family both.

Do not infer high-level operator roles such as:

```text
Q projection
K projection
V projection
O projection
MLP up/down/gate
Transformer layer N
```

unless existing accepted NVTX/operator evidence proves them.

If not proven, keep:

```text
operator_role = UNKNOWN
layer = UNKNOWN
```

This does not prevent selecting an implementation representative.

## D2 — Quantify subfamily recurrence and time importance

For every exact-implementation + launch-shape subfamily under the three target families, compute:

```text
launch_count
launch_count_share within phase/family
accumulated GPU duration
GPU-time share within phase/family
GPU-time share within entire phase
mean duration
median duration
p25/p75
min/max
```

For Decode, additionally compute:

```text
launches per decode step
step-to-step recurrence
shape stability across all 32 steps
```

The purpose is to distinguish:

- one highly repeated dominant implementation;
- several materially different implementation/shape clusters;
- rare outliers.

## D3 — Deterministic occurrence identity

For each candidate subfamily, build a deterministic occurrence list using the accepted run.

At minimum record:

```text
phase
decode_step if applicable
global launch index
exact kernel function
normalized family
grid
block
duration
occurrence index within exact function/shape
```

The next detailed capture stage must be able to select the target without relying on an unstable historical dynamic kernel ID alone.

Preferred future capture identity:

```text
frozen workload identity
+ phase
+ exact function
+ exact launch shape
+ occurrence index
```

If occurrence numbering is ambiguous because the same exact function/shape appears in multiple phases, make the phase part explicit.

## D4 — Representative candidate selection

Select a small candidate set, not every kernel.

### A. Prefill CUBLAS_GEMM

Choose at least one primary candidate that is representative of a high-time recurring GEMM subfamily.

Prefer a candidate whose duration is near the median of the selected recurring subfamily rather than automatically selecting the longest outlier.

Also identify whether the previously collected Native `PREFILL_HEAVY_GEMM` target can be matched to this census by exact function/shape/occurrence evidence.

Allowed result:

```text
NATIVE_TARGET_MATCH_PROVEN
NATIVE_TARGET_MATCH_NOT_PROVEN
```

Do not force a match from approximate duration alone.

### B. Decode CUBLAS_GEMV

Choose at least one primary candidate representing the dominant repeated GEMV subfamily across Decode steps.

Prefer an implementation/shape that recurs across many or all 32 steps and contributes materially to total Decode GPU time.

### C. Decode FlashAttention

Prefill Q05 does not represent Decode launch shapes.

Group Decode FlashAttention variants and choose one representative candidate for the dominant recurring Decode shape/subfamily.

If two materially different Decode FlashAttention shapes each contribute significant time/count, report both as candidates rather than forcing one.

## D5 — Q05 ten-Prefill-occurrence clarification

Using only existing census evidence, list the 10 Prefill `PYTORCH_FLASH_FWD` occurrences with:

```text
global launch index
exact function if available
grid/block
duration
occurrence index
nearest reliable NVTX range labels if present
```

Do not infer Transformer layer numbers if not proven.

The purpose is simply to make the statement “Q05 is one of 10 repeated Prefill FlashAttention launches” fully auditable.

If the existing evidence cannot explain why the count is 10 relative to model layer count, explicitly state:

```text
LAYER_MAPPING_NOT_PROVEN
```

No new GPU run is authorized merely to resolve layer mapping in this stage.

## D6 — Candidate ranking criteria

For each candidate, report the evidence behind selection using quantitative fields rather than a subjective score.

Required criteria:

```text
family GPU-time contribution
subfamily GPU-time contribution
launch recurrence
shape recurrence
duration typicality
deterministic occurrence identity
existing Native evidence alignment
expected simulator-native capture feasibility
```

Do not produce a single opaque weighted score unless every weight has a clear scientific reason. A compact evidence table is preferred.

## D7 — Prepare future capture specifications, but do not execute them

For each selected primary candidate, prepare a machine-readable target descriptor containing only verified fields, for example:

```text
model
revision
scenario
phase
exact kernel function
normalized family
grid
block
occurrence index
reference launch index
reference duration
```

These descriptors are **candidate specifications**, not accepted simulator inputs.

Label them clearly:

```text
CANDIDATE_ONLY_NOT_CAPTURED
```

Do not invoke NVBit or simulator-native producer.

## Explicitly forbidden scope

Do not run:

```text
NSYS
NCU
NVBit
C16WARP1
simulator-native trace capture
new model inference for profiling
new kernel capture
Accel-Sim mechanism experiment
```

The GPU should remain at idle/baseline usage apart from unrelated system activity.

## Required outputs

Report:

```text
docs/vm_tlb/codex_handoff/awma/
KERNEL_TARGET_SELECTION_109_V1_REPORT.md
```

Review pack:

```text
docs/vm_tlb/review_packs/
AWMA_KERNEL_TARGET_SELECTION_109_V1/
```

At minimum include:

```text
README.md
SOURCE_ANCHORS.md
CENSUS_REUSE_RECEIPT.md
PREFILL_GEMM_SUBFAMILIES.tsv
DECODE_GEMV_SUBFAMILIES.tsv
DECODE_FLASH_SUBFAMILIES.tsv
PREFILL_FLASH_10_OCCURRENCES.tsv
TARGET_CANDIDATES.tsv
TARGET_SELECTION_RATIONALE.md
NATIVE_TARGET_ALIGNMENT.md
candidate_targets/
  PREFILL_GEMM_PRIMARY.json
  DECODE_GEMV_PRIMARY.json
  DECODE_FLASH_PRIMARY.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

If more than one Decode Flash primary candidate is scientifically required, use clearly numbered descriptors.

## Report must answer directly

1. Which exact/shape subfamily dominates Prefill CUBLAS_GEMM time?
2. Which exact/shape subfamily dominates Decode CUBLAS_GEMV time?
3. How many materially different Decode FlashAttention shape/subfamilies exist?
4. Which deterministic occurrence should be the next primary Prefill GEMM capture target?
5. Which deterministic occurrence should be the next primary Decode GEMV capture target?
6. Which deterministic occurrence(s) should represent Decode FlashAttention?
7. Does the existing Native Prefill Heavy GEMM target provably match a selected census occurrence?
8. What can and cannot be said about the 10 Prefill FlashAttention launches and layer mapping?

## Execution policy

Routine offline parsing/grouping/demangling/data-quality issues are solve-and-continue.

Stop for scientific review only if:

- the accepted census inventory fails hash/workload verification;
- selecting a deterministic occurrence would require guessing identity fields;
- existing evidence is insufficient and answering the question would require a new GPU run;
- another explicit scientific boundary is reached.

## Completion

Expected marker:

```text
AWMA_KERNEL_TARGET_SELECTION_V1_COMPLETE_WITH_SCOPE
```

Then:

```text
review pack
→ report
→ hashes
→ commit
→ push
→ remote verify
→ clean worktree
→ STOP
```

Do not start capture of the selected candidates.
