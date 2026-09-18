# C16 OLMoE variant-aware natural cuBLAS formal closure — node109 V37

## Execution mode

Execute in **GOAL MODE** on node109.

This Goal supersedes only the V36 requirement that one single actual cuBLAS JIT fingerprint must be stable across every fresh process. The V36-observed runtime variant drift is now treated as a deployment property to characterize and capture, not something to hide or force away.

Suggested implementation branch:

`hrl/c16-olmoe-variant-aware-formal-109-v37`

## Accepted upstream

V34:
- `hrl/c16-olmoe-s2-producer-109-v34@ab26365dc663268b0799818db6687ed466e8c925`
- exact S2/T2048 authority
- native BF16 S2/D32
- Layer1 decode32 natural top-8 `[58,59,47,51,25,15,12,48]`
- natural rank-0 expert58
- semantic target `experts[58].down_proj`
- `[1,1024] x [2048,1024] -> [1,2048]`
- lossless dynamic attribution
- same-module replay bitwise equal

V36:
- `hrl/c16-olmoe-nvbit-jit-selector-formal-109-v36@17d8c9bcf3e48828c7eecd2289b4a4c6db7274e4`
- actual NVBit JIT census works
- actual function family = BF16 cuBLAS `internal::gemvx::kernel`
- grid = `512x1x1`
- block = `16x4x1`
- nregs = 168
- shmem = 272 bytes
- variant A observed:
  `...,false,true,true,false,6,false,...`
- variant B observed:
  `...,true,true,true,false,5,false,...`
- variant A static instruction count = 1096
- variant A actual static GLOBAL path and source registers obtained
- variant A same-process typed dynamic input/weight/output evidence PASS
- no formal capture yet

Do not reopen model, input, semantic target, or offline-SM86 selection.

## Scientific policy repair

The formal target remains the **natural expert58 down_proj semantic module**.

The actual implementation is now explicitly typed as a **natural runtime variant family** under the accepted V34 runtime.

Do not:
- force cuBLAS algorithm selection
- set a determinism/workspace environment variable merely to collapse A/B
- change stream policy merely to force one variant
- switch backend
- select only the easier variant and silently generalize to OLMoE

A/B must be treated as separate actual implementation variants until evidence supports variant-invariant conclusions.

The later three-lineage consumer may use an OLMoE lineage-level property only if:
- the property is supported by both formally captured observed variants, or
- it explicitly narrows the claim to one typed OLMoE runtime variant

## Asset/tool retention

Node164 remains sole model authority.

Reuse the retained node109 OLMoE replica after hash closure.

Reuse the retained V36 NVBit actual-function census/static-introspection tool. Improve it surgically rather than rebuilding lifecycle from scratch.

## Stage 0 — bounded natural variant census

Under the exact V34/V36 runtime and exact isolated expert58 replay, run a bounded fresh-process census.

Use at least 12 fresh processes, preferably 16 if inexpensive.

For every process record:
- process ordinal
- exact runtime identity
- CUDA stream identity/count relevant to the replay where observable
- expert58 input/weight/output base address and alignment modulo 16/32/64/128/256 bytes
- workspace address/size if defensibly observable
- actual launched gemvx function name
- normalized static fingerprint
- static instruction count
- grid/block
- nregs/shmem
- output hash / replay equivalence

Do not change runtime to influence selection.

Classify observed variant set:
- `OBSERVED_TWO_VARIANT_SET_A_B` if only the accepted A/B family appears
- `OBSERVED_EXPANDED_VARIANT_SET` if additional function variants appear

A third observed variant is not automatically a scientific stop; type it and determine whether it is another natural member of the same semantic module implementation family. Stop only if the variant set becomes unbounded/unstable enough that a bounded formal strategy cannot be defined.

Analyze correlations descriptively only:
- pointer alignment
- stream/workspace state
- launch ordering

Do not claim causality unless directly proven.

## Stage 1 — complete static introspection for every observed formal candidate variant

For variant A and variant B at minimum:
- obtain actual loaded CUfunction via NVBit
- dump full static instruction stream
- normalize and SHA256 fingerprint
- classify all address-bearing memory paths
- identify exact source address register/operand
- persist complete variant-specific static selector

If a new bounded variant C appears in Stage 0 and occurs non-negligibly, include it in the same process before formalization.

No static index from one variant may be applied to another variant by position alone.

## Stage 2 — same-process typed dynamic attribution for each variant

For each observed formal candidate variant:
- execute the exact expert58 replay in a process where that variant naturally occurs
- record same-process ranges:
  - `EXPERT_DOWN_INPUT`
  - `EXPERT_DOWN_WEIGHT`
  - `EXPERT_DOWN_OUTPUT`
  - `WORKSPACE_IF_PROVEN`
  - `OTHER_OR_UNCLASSIFIED`
- instrument a bounded complete-enough dynamic pass to prove the variant is actually the expert58 compute/memory kernel
- record which static memory instructions touch which typed ranges

Variant B must independently close; do not inherit variant A attribution.

## Stage 3 — variant-aware formal selector policy

Modify the known-good tracer minimally so every fresh formal process performs a pre-instrumentation runtime classification:

1. identify actual launched function
2. compute/verify normalized static fingerprint
3. map it to a known variant-specific selector table
4. instrument only when the current process matches the requested formal variant
5. if a different known variant occurs, classify attempt as:
   `NATURAL_VARIANT_MISMATCH_RETRY`
   and do not formalize that attempt
6. if an unknown fingerprint occurs, classify:
   `UNKNOWN_RUNTIME_VARIANT`
   and preserve evidence; do not trace using stale selectors

The selector authority is:
- exact function-family identity
- exact normalized static fingerprint
- variant-specific static index/PC
- variant-specific source address register
- exact same-name occurrence for the isolated replay

Do not use process-local CUfunction handle as durable identity.

## Stage 4 — variant-specific canaries

For both A and B:
- naturally obtain that variant
- run bounded warp-regsource canaries
- fresh process/output
- exact fingerprint guard
- exact static selector
- drop=0
- overflow=0
- terminal closure
- same-process typed address mapping

If a process naturally selects the other known variant, retry without changing cuBLAS settings.

Set a bounded retry policy based on Stage 0 observed frequencies. Do not spin indefinitely.

Canary PASS for each variant must prove the selector reaches the intended actual expert58 JIT kernel.

## Stage 5 — formal capture strategy

Preferred scientific closure is **two separately admitted formal runs**:

### Formal A
One complete formal run for natural variant A.

### Formal B
One complete formal run for natural variant B.

For each:
- one variant-specific selected static memory instruction per independently replayed shard
- each fresh process must pass the requested variant fingerprint guard
- known-other-variant processes are retries, not failed formal shards
- complete selected static set
- executed/zero partition
- drop=0
- overflow=0
- terminal closure
- same-process ADDRESS_CONTEXT
- typed membership

Do not merge A/B static indices into one fake global static set.

Do not construct cross-variant VA unions or chronology.

If Stage 0 discovers an additional non-negligible natural variant C:
- do not silently ignore it
- capture it formally only if necessary to support an OLMoE lineage-level claim
- otherwise explicitly type V37 as partial observed-variant coverage and leave the later consumer claim narrow

## Stage 6 — formal analysis per variant

For each formally captured variant report independently:
- static selected count
- executed / zero
- active-lane event total
- per-executed-shard event distribution
- per-shard 128B line distribution
- per-shard 4K / 64K / 2M page distributions
- typed membership fractions:
  - EXPERT_DOWN_WEIGHT
  - EXPERT_DOWN_INPUT
  - EXPERT_DOWN_OUTPUT
  - WORKSPACE_IF_PROVEN
  - OTHER_OR_UNCLASSIFIED
- full-scope result

Then produce a **variant-robustness comparison**:
- features shared by A and B
- features that differ
- ratios/ranges
- whether the downstream Q30/DeepSeek comparison fields are invariant enough to treat as an OLMoE lineage-level pattern

Do not average A/B into one estimator unless an explicit weighting population is measured and justified.

## Stage 7 — serial admissions

Mandatory:
`FORMAL_ADMISSION_CONCURRENCY=1`

Admit A completely:
`manifest -> transfer -> destination verify -> catalog -> positive ACK`

Only after A positive ACK, admit B completely.

No concurrent catalog mutation.

## Stage 8 — downstream authorization

If both A and B formal runs PASS and ACK:
authorize:

`OLMOE_TWO_NATURAL_JIT_VARIANTS_FORMALLY_CLOSED_FOR_THREE_LINEAGE_CONSUMER`

If only one variant is formally captured:
- do not claim OLMoE lineage-level invariant behavior
- type the uncovered variant gap
- authorize the later consumer only for a narrowed deployment-variant comparison if scientifically defensible

No more OLMoE operators/scenarios after A/B closure.

## Claim boundaries

Allowed after dual-variant closure:
- OLMoE expert58 natural down_proj has properties shared by both observed A/B runtime variants
- later consumer may compare those robust properties against Q30 and DeepSeek

Not allowed:
- A/B exhaust all possible cuBLAS implementations universally
- observed frequency is a population probability unless sampling protocol supports it
- pointer alignment caused variant selection unless proven
- matched-input causal comparison across Q30/DeepSeek/OLMoE
- cache/TLB causality from these traces

## Required review pack

Create:
`docs/vm_tlb/review_packs/C16_OLMOE_VARIANT_AWARE_FORMAL_109_V37/`

Include at least:
- `UPSTREAM_V36_AUTHORITY.json`
- `VARIANT_CENSUS.tsv`
- `VARIANT_CENSUS_SUMMARY.json`
- `VARIANT_A_STATIC_PATH_AUDIT.json`
- `VARIANT_B_STATIC_PATH_AUDIT.json`
- `VARIANT_A_STATIC_SELECTOR.tsv`
- `VARIANT_B_STATIC_SELECTOR.tsv`
- `VARIANT_A_TYPED_ATTRIBUTION.json`
- `VARIANT_B_TYPED_ATTRIBUTION.json`
- `VARIANT_A_CANARY.json`
- `VARIANT_B_CANARY.json`
- `VARIANT_A_FORMAL_SUMMARY.json`
- `VARIANT_B_FORMAL_SUMMARY.json`
- `VARIANT_A_SHARDS.tsv`
- `VARIANT_B_SHARDS.tsv`
- `VARIANT_A_ADMISSION_ACK.json`
- `VARIANT_B_ADMISSION_ACK.json`
- `VARIANT_ROBUSTNESS_COMPARISON.json`
- `THIRD_LINEAGE_HANDOFF.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preferred full PASS:
`C16_OLMOE_VARIANT_AWARE_FORMAL_109_V37_PASS_DUAL_VARIANT`

Fail closed only on genuine evidence blockers:
- variant cannot be dynamically tied to expert58
- static source-address semantics unresolved
- bounded natural retry cannot obtain a required variant
- formal drop/overflow/terminal/full-scope cannot close
- serial admission/ACK fails
- variant set is too unstable for bounded typed coverage

Routine NVBit lifecycle, selector plumbing, retry orchestration, and trace-capacity issues are engineering problems: solve and continue.

## Git/cleanup

Use existing node109 Git transport. Do not install/configure `gh`.

At end:
- review pack -> SHA256SUMS -> commit -> push -> canonical ls-remote verify
- release GPU lock
- no stale NVBit/profiler/CUDA process
- GPU baseline restored
- retain valid OLMoE replica
- retain useful NVBit JIT introspection tooling
- clean worktree
