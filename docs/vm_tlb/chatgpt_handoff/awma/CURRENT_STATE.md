# AWMA Current State

Date: 2026-09-17

## Coordination status

AWMA is now entering the next MAINLINE stage:

`AWMA_Q05_CONTEXT_WARMUP_SENSITIVITY_V1`

The project priority rule is frozen:

> Mainline always has first claim on node109 RTX4080 and node174-new. Side work may run only when the active mainline does not need the resource and must never make the mainline wait.

Current mainline tracks:

```text
Track M1 — node109 / RTX4080
Q05 native predecessor-context characterization
ACTIVE

Track M2 — node174-new
Q05 warm-replay feasibility / kernel-boundary state audit
ACTIVE
```

The two tracks are complementary:

- M1 determines what real predecessor execution exists before Q05 and which Q05 pages were previously touched in the same frozen native execution context;
- M2 determines whether/how the simulator can preserve TLB/PWC/cache state across sequential kernels and measure Q05 without resetting the warm state.

No new TLB/PTW mechanism experiment is authorized yet.

---

## Why this is now the mainline question

The accepted Q05 trace is a complete whole-kernel simulator-native trace, but current simulation replays Q05 as an isolated selected kernel.

Therefore previous results establish isolated-state sensitivity, not yet full-application-context sensitivity.

The next question is:

> How much of the observed Q05 translation/cache behavior is intrinsic to Q05, and how much is caused by losing predecessor-created state when Q05 is replayed alone?

This distinction is required before using Q05 to motivate a real TLB/PTW mechanism.

Shared experiment contract:

`Q05_CONTEXT_WARMUP_EXPERIMENT_CONTRACT_V1.md`

---

## Frozen workload identity

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT
batch      = 1
input      = frozen TEXT binding
prefill    = 2048 tokens
decode     = 32 tokens
dtype      = FP16
backend    = SDPA
```

Current accepted Q05 target:

```text
Q05_PREFILL_ATTN_FLASH
function occurrence = 0
kernel = pytorch_flash::flash_fwd_kernel<...>
```

Frozen Simulation IDs remain read-only:

```text
SIM_INPUT_0ab4e2fe2195d3b7d7da4ee9df6017cbec5c063fcc8110374e1a753f87177634
SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
SIM_RUN_92a553b0d69a9f41c5e20a8650366c53f7fed31c29c7462947d3af03c6f136f1
SIM_EVIDENCE_c8b4175d33f8bed7def2984489eadbdbcdfaffbfcb6a7daef33c8beb18e80959
```

Accepted simulator/source anchors remain:

```text
Framework execution source = d64408a97d76a320a6d49468653d416e33677af8
Core                       = 57bb71ecd015b6ec0ab32e45b0815e5beaf69172
qualified binary SHA256    = 34deedd99e85e52fb309852de2ecc5fecd9471436a33a5e77d40bc038a2c31c4
producer                    = 5143b4e10aaf2fc47bb60492155d2464b0b726fd
validator hotfix            = fb5d0bebee421a0153661239e1f7c2bc088d5c9e
characterization anchor     = bb92e5a1559dd7e2b2520e9a7a4937262664512c
```

---

## Accepted isolated-Q05 characterization

R0 10k:

```text
gpu_sim_insn = 1,084,480 completed active thread-instructions
L1 TLB       = 930 access / 805 hit / 125 miss
L2 TLB       = 125 access / 0 hit / 125 miss
MSHR         = 19 alloc / 106 merge / 0 full / HWM 16
walks        = 19 start / 19 complete
max waiter   = 35
```

Counterfactual ideal-identity sensitivity:

```text
10k: R0 1,084,480 ; I0 1,697,696 (+56.55%)
50k: R0 11,587,872 ; I0 20,458,400 (+76.55%)
```

P2 and M8 did not produce measurable 10k progress gain, so L2-TLB port throughput and shared-L2 per-entry merge capacity are downgraded as dominant single causes.

These are fixed-window isolated selected-kernel sensitivity results, not full-model speedup claims.

---

## Complete Q05 structure and timeline

Whole selected Q05 trace:

```text
224 CTA
896 warps
13,361,600 warp-instruction records
971,824 memory-instruction records
29,564,416 lane-address events
228 unique offline 64KiB VPN
```

Trace file order remains:

`STRUCTURAL_TRACE_ORDER_ONLY`

Natural isolated R0 completion:

```text
885,681 cycles
224 issued CTA
368,696,302 completed active thread-instructions
```

Diagnostic timeline result:

```text
translation key = {asid, vpn, page_size}

10k:
19 keys / 19 fills / 106 merges / 8,730 post-fill REQUEST invocations

50k:
104 keys / 104 fills / 374 merges / 474,414 post-fill REQUEST invocations

full:
240 simulator keys / 240 fills / 393 merges
8,747,322 post-fill REQUEST invocations
max waiter depth = 35
```

Current interpretation:

`MIXED`

Supported:

- strong pre-fill burst fanout exists;
- about 95% of observed merge events occur by 50k while more than half of final translation keys still appear after 50k;
- new translation demand therefore continues after fanout has largely diminished;
- current evidence does not support a simple TLB-capacity/thrashing story.

Boundary:

`REQUEST` is a simulator invocation/retry unit, not an independent memory instruction or TLB lookup count.

Carry-forward caveats:

- post-fill per-key L1/L2 outcome remains unavailable from the previous timeline logging;
- 240 simulator translation keys vs 228 offline 64KiB VPN must be reconciled before native page sets are joined to simulator keys.

The 174-new V1 warm-replay feasibility track explicitly carries the 240-vs-228 reconciliation task.

---

## Accepted full S2 kernel census / Q05 representativeness

Exact frozen run:

```text
34,677 total CUDA kernel activities
34,072 inside explicit inference ranges
408 Prefill launches
33,664 Decode launches
```

Q05 belongs to 10 same-shape Prefill FlashAttention launches and is:

`REPRESENTATIVE_WITHIN_SAME_FLASH_FAMILY`

but only partially representative of broader Attention and not representative of the whole model.

Important execution families:

```text
Prefill CUBLAS_GEMM      = 66.48% Prefill GPU time
Prefill FlashAttention   = 14.31%
Decode CUBLAS_GEMV       = 49.76% Decode GPU time
Decode FlashAttention    = 9.87%
```

---

## Complementary producer assets already captured

Node109 side-lane result has closed two additional producer-qualified whole-target bundles on node164:

```text
PREFILL_GEMM_PRIMARY_1
  PRODUCER_CAPTURE_COMPLETE_DURABLE
  12,043,648 raw records
  terminal COMPLETE / drop=0 / overflow=0 / mode2=0

DECODE_GEMV_PRIMARY_1
  PRODUCER_CAPTURE_COMPLETE_DURABLE
  1,515,136 raw records
  terminal COMPLETE / drop=0 / overflow=0 / mode2=0
```

They are durable producer assets only. They are not yet SIM_INPUTs and are not part of the current warmup experiment.

Decode Flash status:

```text
DECODE_FLASH_PRIMARY_1
  CAPTURE_CONTRACT_BLOCKED
  real LDC.U8 record rejected by frozen grammar because width is missing/zero

DECODE_FLASH_PRIMARY_2
  NOT_STARTED_DUE_TO_FAIL_CLOSED_STOP
```

The LDC.U8 grammar issue is deferred. Do not repair it during the current mainline unless ChatGPT explicitly creates a separate task while the mainline does not need the GPU.

---

## Storage / node roles

Durable large-data owner:

`/root/share/mnt164/huangrulin/c16_ai_workload/`

Roles:

```text
109 = GPU producer / native characterization
174-new = simulator / analysis
164 = durable large-data authority
```

Producer-side data-plane qualification reached:

`AWMA_164_DATA_PLANE_QUALIFIED_V1`

The previous 174 consumer audit independently confirmed that accepted AWMA raw is not uniquely dependent on 174 local disk; its final producer-canary delta verification may be completed later when mainline resources are idle.

174 local-storage audit also completed read-only: no large local-only accepted AWMA authority was found; no cleanup action is currently worth interrupting mainline work.

---

## Mainline Track M1 — node109 / RTX4080 — ACTIVE

Execute:

`CODEX_NEXT_STAGE_109_Q05_NATIVE_CONTEXT_CHARACTERIZATION_V1.md`

Goals:

- establish exact Q05 predecessor launch sequence;
- capture a bounded SAME-RUN lightweight memory/page context through Q05;
- compute predecessor page-overlap opportunity and last-touch distance;
- establish normal-context Q05 timing stability;
- optionally test data-cache-sensitive NCU conditions without claiming TLB flush/preservation;
- recommend a bounded set of continuous predecessor prefix windows for later simulator-native capture.

No simulator-native predecessor capture campaign in this V1 stage.

Expected completion:

`AWMA_Q05_NATIVE_CONTEXT_CHARACTERIZATION_109_V1_COMPLETE_WITH_SCOPE`

---

## Mainline Track M2 — 174-new — ACTIVE

Execute:

`CODEX_NEXT_STAGE_174NEW_Q05_WARM_REPLAY_FEASIBILITY_V1.md`

Goals:

- source-audit what state persists/resets across kernels;
- reconcile 240 simulator keys vs 228 offline pages;
- define a Q05-only measurement boundary that does not clear warm state;
- qualify state observability;
- run self-warm diagnostics only as plumbing evidence when source semantics allow;
- define the exact future predecessor context-bundle contract.

No real predecessor warm-prefix science in this V1 stage.

Expected completion:

`AWMA_Q05_WARM_REPLAY_FEASIBILITY_174NEW_V1_COMPLETE_WITH_SCOPE`

---

## Mainline priority rule

While M1 is ACTIVE, node109 RTX4080 is reserved for the mainline.

Do not start:

- LDC.U8 repair side lane;
- Qwen3 / DeepSeek work;
- NCU campaigns unrelated to Q05 context sensitivity;
- additional selected-kernel capture;
- cleanup work;
- other opportunistic GPU tasks.

A side task can resume only after the active mainline explicitly releases the GPU.

---

## Global STOP boundary

This stage may not automatically begin:

- real predecessor simulator-native capture campaign;
- SIM_INPUT admission of a predecessor context bundle;
- scientific prefix+Q05 warm replay;
- L2-TLB latency/PTW/walker/capacity/page-size sweeps;
- Segment;
- early outstanding-translation mechanism;
- new cache/TLB mechanism.

After M1 and M2 complete, return both reports/review packs to ChatGPT. ChatGPT will select the actual continuous prefix matrix and issue the next mainline capture/replay stage.
