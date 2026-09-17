# AWMA Current State

Date: 2026-09-17

## Coordination status

The first Q05 representativeness/full-kernel clarification round is complete on both nodes.

Accepted execution results:

```text
109 census branch:
hrl/awma-qwen25-s2-census-109-v1
HEAD = 678d7b491d4788369ca0c22717453b20846ab195
status = AWMA_QWEN25_S2_KERNEL_CENSUS_V1_COMPLETE_WITH_SCOPE

174-new full-Q05 branch:
hrl/awma-q05-full-translation-174new-v1
HEAD = 6415d3f1
status = AWMA_Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_V1_COMPLETE_WITH_SCOPE
```

Review disposition:

```text
109 = ACCEPTED
174-new = ACCEPTED_WITH_REQUIRED_FOLLOWUP
```

The 174-new stage correctly preserved evidence boundaries, but the central first-touch/fill/post-fill question remains unresolved because the frozen simulator telemetry does not carry cycle-keyed translation-key associations. This is now the highest-priority scientific gap.

The next stage is therefore:

```text
AWMA_Q05_TRANSLATION_TIMELINE_CLOSURE_AND_KERNEL_TARGET_SELECTION_V1
```

It remains pre-mechanism.

## Frozen workload identity

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT  # AWMA internal scenario label
batch      = 1
input      = TEXT
prefill    = 2048 tokens
decode     = 32 tokens
dtype      = FP16
backend    = SDPA
```

Current Simulation target:

```text
Q05_PREFILL_ATTN_FLASH
function occurrence = 0
kernel = pytorch_flash::flash_fwd_kernel<...>
```

## Frozen Simulation identities

```text
SIM_INPUT_0ab4e2fe2195d3b7d7da4ee9df6017cbec5c063fcc8110374e1a753f87177634
SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
SIM_RUN_92a553b0d69a9f41c5e20a8650366c53f7fed31c29c7462947d3af03c6f136f1
SIM_EVIDENCE_c8b4175d33f8bed7def2984489eadbdbcdfaffbfcb6a7daef33c8beb18e80959
```

Accepted source anchors:

```text
Framework execution source = d64408a97d76a320a6d49468653d416e33677af8
Core                       = 57bb71ecd015b6ec0ab32e45b0815e5beaf69172
Simulator binary SHA256    = 34deedd99e85e52fb309852de2ecc5fecd9471436a33a5e77d40bc038a2c31c4
Producer                    = 5143b4e10aaf2fc47bb60492155d2464b0b726fd
Validator hotfix            = fb5d0bebee421a0153661239e1f7c2bc088d5c9e
```

Accepted bounded characterization anchor:

```text
bb92e5a1559dd7e2b2520e9a7a4937262664512c
```

## Accepted bounded characterization facts

R0 10k:

```text
gpu_sim_insn                  = 1,084,480 completed active thread-instructions
translation lookups           = 930
L1 TLB                         = 930 access / 805 hit / 125 miss
L2 TLB                         = 125 access / 0 hit / 125 miss
translation MSHR              = 19 alloc / 106 merge / 0 full
translation MSHR HWM          = 16 / 32
walks                          = 19 start / 19 complete
max waiter depth              = 35
requester latency total       = 164,955
requester MSHR-wait component = 144,303
```

Accounting identity:

```text
125 miss requesters = 19 new outstanding translations + 106 merges
```

Counterfactual progress:

```text
10k: R0 1,084,480 ; I0 1,697,696 (+56.55%)
50k: R0 11,587,872 ; I0 20,458,400 (+76.55%)
```

P2 and M8 showed essentially no 10k progress gain, so L2-TLB port throughput and shared-L2 per-entry merge capacity are downgraded as dominant single causes. I0 remains only aggregate translation-path sensitivity, not a realizable speedup.

## New accepted result: complete Q05 structure

The accepted simulator-native trace covers the complete selected Q05 kernel, not the full model.

```text
CTA                               = 224
warps                             = 896
warp-instruction records          = 13,361,600
memory-instruction records        = 971,824
lane-address events               = 29,564,416
unique offline 64 KiB VPN         = 228
```

Trace-file order is:

```text
STRUCTURAL_TRACE_ORDER_ONLY
```

It must not be used as a cross-CTA simulator-cycle timeline.

Natural R0 completion:

```text
cycles                            = 885,681
issued CTA                        = 224 / 224
completed active thread-insns     = 368,696,302
```

10k and 50k each have:

```text
issued CTA = 70 / 224 = 31.25%
```

This does not mean the kernel is 31.25% complete. The frozen telemetry did not provide valid cycle-keyed warp-instruction, memory-reference, or unique-page coverage for those windows.

Current Q05 classification:

```text
MIXED
per-translation first-touch/fill/post-fill attribution = INCONCLUSIVE
```

Supported statement:

> There is strong outstanding-translation fanout in the early bounded window, while the full structural page footprint is highly skewed. The current evidence does not justify calling the behavior pure streaming or capacity thrashing.

Unsupported until next stage:

- exact first-touch fraction by cycle window;
- requests-before-fill fraction per translation key;
- post-fill L1/L2 hit rate by key;
- post-fill revisit interval;
- cycle-keyed unique-page growth;
- stable warm-after-fill classification.

## New accepted result: full S2 kernel-call inventory

One exact frozen lightweight NSYS CUDA/NVTX run produced the complete kernel-call inventory.

```text
total CUDA kernel activities     = 34,677
inside explicit inference ranges = 34,072
Prefill launches                  = 408
Decode launches                   = 33,664
Decode launches per step          = 1,052 x 32
```

Q05 representativeness:

```text
Prefill PYTORCH_FLASH_FWD launches = 10
all 10 launch shape                = grid 16,1,14 / block 128,1,1
Q05 duration                       = 159,969 ns
same-family median                 = 154,112.5 ns
same-family range                  = 146,976 .. 159,969 ns
```

Accepted classification:

```text
same Prefill FlashAttention family = REPRESENTATIVE_WITHIN_SAME_FLASH_FAMILY
broader Attention                  = PARTIALLY_REPRESENTATIVE
whole frozen run                   = SPECIAL_CASE
Decode                             = NOT ASSUMED REPRESENTATIVE
layer mapping                      = NOT PROVEN
```

Important GPU-time structure:

### Prefill

```text
CUBLAS_GEMM      70 launches   66.48% Prefill GPU time
PYTORCH_FLASH_FWD 10 launches  14.31% Prefill GPU time
```

The remaining time is split among elementwise/copy/reduction/other families. Thus Q05 is important but does not represent the dominant Prefill compute family.

### Decode total

```text
CUBLAS_GEMV       5,408 launches  49.76% Decode GPU time
PYTORCH_FLASH_FWD 1,536 launches   9.87% Decode GPU time
```

Decode FlashAttention uses different launch shapes from Prefill Q05, so Q05 must not be extrapolated to Decode.

The previous semantic category `UNKNOWN` mainly reflected lack of high-level operator-role mapping; implementation-family classification already identifies CUBLAS_GEMM/GEMV. Do not describe these as scientifically unknown kernels.

## Current scientific decision

Two things are now clear.

First, Q05 is a valid representative target for one repeated Prefill FlashAttention implementation class, so finishing its translation-behavior diagnosis remains scientifically useful.

Second, a general AI-workload/TLB claim cannot rest on Q05 alone. Before broad mechanism claims, the target set must eventually include at least representative non-Flash families, especially:

- dominant Prefill CUBLAS_GEMM;
- dominant Decode CUBLAS_GEMV;
- likely one Decode FlashAttention target because Prefill Q05 does not represent Decode Flash shapes.

The next stage selects these candidates but does not yet capture them.

## Node roles for the next stage

### 174-new / port 2239

Execute diagnostic-only translation timeline closure.

Goals:

- add timing-neutral, disabled-by-default cycle/key telemetry;
- pass a strict R0 10k neutrality/equivalence gate;
- obtain first-touch, pre-fill fanout, fill, post-fill hit/revisit behavior;
- obtain valid 10k/50k/full coverage for warp-instruction, memory-instruction, and unique translated pages when same-unit closure can be proven;
- rerun R0 10k, 50k and natural completion only as required by the spec;
- do not test mechanisms.

### 109 / RTX4080

GPU remains idle for this stage.

Perform offline target selection from the accepted census:

- group Prefill CUBLAS_GEMM by exact implementation + launch shape;
- group Decode CUBLAS_GEMV by exact implementation + launch shape;
- summarize Decode FlashAttention shape/family variants;
- select deterministic representative occurrences for possible later simulator-native capture;
- check whether existing Native heavy-GEMM targets align with one selected census target;
- do not capture new traces yet.

### node164

Durable storage remains the owner for large raw telemetry and full launch inventories.

## Immediate execution order

Run the next two tracks in parallel:

```text
174-new:
CODEX_NEXT_STAGE_174NEW_Q05_TRANSLATION_TIMELINE_CLOSURE_V1.md

109:
CODEX_NEXT_STAGE_109_KERNEL_TARGET_SELECTION_V1.md
```

Canonical dispatcher:

```text
CODEX_NEXT_STAGE.md
```

## Global STOP boundary

Do not automatically start:

- L2-TLB lookup-latency sweep;
- PTW fixed-latency experiment;
- walker-count sweep;
- TLB-capacity sweep;
- page-size sweep;
- Segment;
- early outstanding-translation detection;
- any new simulator-native kernel capture.

After both tracks finish, return reports/review packs to ChatGPT for the next scientific decision.
