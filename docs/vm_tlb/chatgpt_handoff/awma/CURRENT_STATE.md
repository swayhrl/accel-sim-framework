# AWMA Current State

Date: 2026-09-17

## Coordination status

AWMA has moved past the simulator-compatible capture bring-up and the first bounded TLB/PTW characterization round. The current scientific stage is:

```text
Q05 representativeness + full-kernel translation-behavior clarification
```

This stage is deliberately **pre-mechanism**. Its job is to determine whether the currently observed translation sensitivity is mainly a cold-start/first-touch effect, a streaming/low-reuse effect, a same-page outstanding-translation fanout effect, or a mixture; and to determine how representative Q05 is within the full Qwen2.5 workload.

The accepted characterization anchor is:

```text
bb92e5a1559dd7e2b2520e9a7a4937262664512c
```

Result:

```text
AWMA_TLB_PTW_CHARACTERIZATION_V1_COMPLETE_WITH_SCOPE
OPPORTUNITY_PRESENT
scope = FIXED_WINDOW_PROGRESS_SENSITIVITY
```

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

`S2_TEXT` is only an AWMA internal name for the above test configuration. It is not a standard LLM term.

Current Simulation target:

```text
Q05_PREFILL_ATTN_FLASH
function occurrence = 0
kernel = pytorch_flash::flash_fwd_kernel<...>
```

The simulator-native producer captured the complete selected Q05 CUDA kernel, not only a 10k/50k prefix:

```text
raw records = 13,490,624
capture completion = COMPLETE
drop = 0
overflow = 0
```

The 10k and 50k values used in the characterization round are simulator-cycle stop windows applied while replaying this complete kernel trace.

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

## Accepted F0 translation configuration

Effective runtime baseline:

- functional VM mode 2;
- 64 KiB base page;
- 49-bit VA;
- L1 TLB: 32 entries, 32-way, 1 port, 10-cycle lookup;
- exact L2 TLB: 768 entries, 16-way, 48 sets, 1 port, 80-cycle lookup;
- translation MSHR: 32 entries;
- PWQ: 32;
- walkers: 16;
- real PTE L2/DRAM page-walk mode;
- four page-table levels;
- PWC: 128 entries, 1 cycle;
- Segment disabled.

Use the effective runtime configuration after fair-arm selection. Do not infer effective settings only from historical raw config text.

## Completed characterization results

### R0 baseline, 10k cycles

```text
gpu_sim_cycle                    = 10,000
gpu_sim_insn                     = 1,084,480 completed active thread-instructions
gpu_tot_issued_cta               = 70
translation lookup requests      = 930
L1 TLB accesses/hits/misses      = 930 / 805 / 125
L2 TLB accesses/hits/misses      = 125 / 0 / 125
L2 TLB port-denial events        = 5,828
translation MSHR alloc/merge     = 19 / 106
translation MSHR full            = 0
translation MSHR HWM             = 16 / 32
walk starts/completions          = 19 / 19
PTE requests/responses           = 70 / 70
PTE L2-only / DRAM               = 48 / 22
requester latency total          = 164,955
requester MSHR-wait component    = 144,303
max waiter depth                 = 35
```

Important accounting identity:

```text
125 L1/L2 miss requesters = 19 new translation allocations + 106 merges
```

Thus the 125 misses are not evidence for 125 independent page walks.

### Counterfactual variants

At 10k cycles:

```text
R0 = 1,084,480
I0 = 1,697,696  (+56.55%)
P2 = 1,084,448  (~0%)
M8 = 1,084,448  (~0%)
```

At 50k cycles:

```text
R0 = 11,587,872
I0 = 20,458,400 (+76.55%)
```

Interpretation boundaries:

- I0 is ideal identity translation: it removes the functional translation path; it is not merely 100% L1-TLB hit and is not a realizable hardware speedup claim.
- The +56.55% and +76.55% values are fixed-cycle progress/IPC sensitivity values, not complete-kernel speedups.
- P2 shows that reducing L2-TLB port-denial events alone does not improve same-window progress; this downgrades L2-TLB port throughput as the dominant single bottleneck but does not test L2-TLB lookup latency.
- M8 changes shared-L2 per-entry merge capacity from 4 to 8; its near-zero progress effect does not test translation-MSHR capacity.
- translation-MSHR capacity itself is not currently indicated as saturated: 32 entries, HWM 16, full 0.
- L2-TLB 0 hits in the 10k window must not yet be interpreted as steady-state streaming or capacity thrashing.

## Current scientific hypothesis boundary

The strongest current structural signal is:

```text
small number of outstanding translations
        x
high same-translation requester fanout
        x
long translation-completion latency
```

However, the current evidence does **not** distinguish cleanly between:

1. cold first-touch at the beginning of an isolated kernel replay;
2. streaming / low translation reuse;
3. many requesters arriving before a translation fill and therefore repeatedly observing a miss;
4. persistent post-fill reuse;
5. a mixture of the above.

This ambiguity must be resolved before mechanism design.

## Trace availability boundary

Do not say that the complete Qwen2.5 run is already available as an Accel-Sim trace.

Current distinction:

- full-run NSYS/kernel metadata: lightweight real-GPU execution catalog, when available;
- Native C16WARP1/MREF traces: selected native targets, suitable for scoped address/page/cache-line analysis, but not losslessly convertible post hoc into simulator traceg;
- simulator-native whole-kernel trace: formally accepted for the selected Q05 target.

The simulator-compatible capture pipeline is now technically established, so new selected kernels can be captured by reusing the mature pipeline, subject to per-kernel validation. This does not mean every kernel in the model has already been captured.

## Node roles for the current stage

### 174-new / port 2239

Owner of Simulation-plane analysis.

Current task:

```text
AWMA_Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_V1
```

Responsibilities:

- analyze the complete Q05 simulator-native trace;
- establish 10k/50k/full-kernel coverage metrics;
- obtain cycle-ordered VPN/translation behavior from the simulator;
- separate first-touch, pre-fill fanout, post-fill reuse and streaming behavior;
- run one R0 natural-completion replay only if required and practical;
- do not start a new translation mechanism experiment.

### 109 / RTX4080

Owner of Native producer/capture.

Current task:

```text
AWMA_QWEN25_S2_KERNEL_CENSUS_V1
```

Responsibilities:

- first reuse existing accepted NSYS/kernel-catalog evidence if sufficient;
- otherwise run only one lightweight full-scenario kernel-call inventory for the frozen workload;
- classify kernel launches by phase, semantic family and exact implementation where evidence supports it;
- quantify launch-count share and GPU-time share;
- determine how common/typical Q05's FlashAttention implementation is.

This stage does **not** authorize NCU, NVBit memory trace, new simulator-native kernel traces, or broad recapture on 109.

### node164

Durable storage owner for large raw/derived artifacts.

Keep large timelines, NSYS reports and full diagnostic logs on node164. Git contains code, compact summaries, manifests, hashes and review evidence only.

## Current open questions

1. Where exactly do 10k and 50k sit within the complete Q05 kernel by CTA, warp-instruction, memory-reference and unique-page coverage?
2. Are most unique 64 KiB pages introduced near the kernel beginning or continuously throughout execution?
3. Of the current L2 misses, how many occur before the corresponding translation has filled?
4. After fill, are those pages repeatedly reused and hit in L1/L2 TLB, or rarely revisited?
5. What is the full-kernel distribution of translation fanout and waiter depth?
6. How many CUDA kernel launches occur in the complete frozen Qwen2.5 scenario, and which semantic/implementation families dominate by launch count and GPU time?
7. How many times does the same `flash_fwd` implementation appear during Prefill, and is Q05 occurrence 0 typical of that family?

## Immediate execution order

Run the following two tracks in parallel from this coordination state:

```text
174-new:
CODEX_NEXT_STAGE_174NEW_Q05_FULL_TRANSLATION_BEHAVIOR_V1.md

109:
CODEX_NEXT_STAGE_109_QWEN25_S2_KERNEL_CENSUS_V1.md
```

The canonical dispatcher is:

```text
CODEX_NEXT_STAGE.md
```

After both tracks finish, stop and return their reports/review packs to ChatGPT for a new scientific decision.

Do not automatically start:

- L2-TLB latency sweep;
- PTW fixed-latency experiment;
- walker-count sweep;
- TLB-capacity sweep;
- page-size sweep;
- Segment;
- early-outstanding-detection mechanism;
- new selected-kernel simulator-native capture.
