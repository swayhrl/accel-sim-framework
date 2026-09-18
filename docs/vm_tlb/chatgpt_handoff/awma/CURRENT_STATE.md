# AWMA Current State

Date: 2026-09-18

## Coordination stage

`AWMA_Q05_CONTIGUOUS_PREFIX_WARM_REPLAY_V1`

Mainline priority remains frozen: node109 RTX4080 and node174-new serve the active mainline first. Side work may run only when the mainline does not need the resource and must never delay the mainline.

Execution-efficiency policy is also frozen: small, correctness-neutral issues with an obvious safe fix are folded into the next real mainline handoff or corrected directly in ChatGPT-owned coordination material. They do **not** get a standalone Codex round merely for bookkeeping. A separate Codex stage is reserved for work that needs execution/evidence, changes scientific semantics/provenance, or carries nontrivial engineering risk.

## Previous context-warmup stage review

### 174-new feasibility — ACCEPTED WITH SCOPE

Execution:

```text
hrl/awma-q05-warm-replay-feasibility-174new-v1
e2fa35f045e0b4f977a964d9c92974c9f6d3e240
```

Key result:

`WARM_REPLAY_READY_WITH_DIAGNOSTIC_COUNTER_BOUNDARY_ONLY`

Self-warm diagnostic in one simulator instance:

```text
Q05 #1 = 885,681 cycles
Q05 #2 = 821,426 cycles
Q05 #2 L2 TLB = 2,922 access / 2,922 hit / 0 miss
Q05 #2 new walks = 0
Q05 #2 new translation-MSHR merges = 0
```

This proves modeled translation state survives sequential kernel dispatch and Q05-only deltas are feasible without resetting at target entry.

Claim boundary: the cycle reduction is a combined modeled warm-state effect. It is NOT yet attributable solely to TLB/translation because data-cache state may also persist. The next stage must close L1/L2 TLB and L1/L2 data-cache semantics separately.

### 109 native context — VALID REVIEW STOP

Execution:

```text
hrl/awma-q05-native-context-109-v1
64a2e51943a6737b84132bc7daa5f4d7c74f8099
```

Accepted output:

- frozen workload/Q05 identity closed;
- exact contiguous Q05 predecessor sequence closed;
- Q05 is Prefill launch 34;
- there are exactly 34 contiguous Prefill predecessors, launches 0..33.

The attempted lightweight page observer is REJECTED:

- stock sync: channel backpressure;
- stock async: real dependency stall;
- callback prefix teardown: process abort/no natural terminal;
- R6: sidecar emitted but process aborted; predecessor sets not proven.

No page-overlap or hardware-TLB claim is accepted from those attempts.

## Mainline pivot

Do not spend another mainline stage repairing the lightweight observer.

Because the full real Q05 prefix is only 34 predecessor launches and the eventual warm replay requires full predecessor traces anyway, node109 now captures one bounded **same-run contiguous simulator-native context bundle** for launches 0..34.

Offline page-overlap is derived from that formal bundle.

Node174-new then replays real predecessor suffixes before Q05 under unchanged F0 semantics.

## Active tracks

```text
M3R — 109 / RTX4080
Q05 P34 LDC.U8 semantic recovery + existing-raw promotion
ACTIVE MAINLINE

M4 — 174-new
Q05 warm-prefix replay
WAITING_FOR_CONTEXT_BUNDLE
```

### M3R — 109

The first contiguous-prefix run closed R1 and R2 and captured all 35/35 same-context raw members, but formal admission stopped at member 2 because the frozen strict validator rejected `LDC.U8` with width 0.

This is now a mainline blocker, not deferred side work.

Execute:

`CODEX_RESUME_109_Q05_PREFIX_LDC_U8_RECOVERY_V1.md`

Existing P34 evidence already contains all 35 terminally closed raw members in one CUDA context. The recovery path must first reuse that raw execution offline.

Source-backed diagnosis to verify: the producer intentionally omits dynamic payload for constant operands; frozen Accel-Sim accepts `LDC` through an implicit constant-load path. Therefore do not fabricate width/address. Repair only the strict validator classification for exact `LDC`, regression-test it, validate all 35 members, then perform page-overlap analysis and node164 publication.

GPU recapture is fallback-only if existing raw integrity/provenance cannot be closed.

### M4 — 174-new

Preparation has already closed as:

`AWMA_Q05_WARM_PREFIX_REPLAY_174NEW_V1_WAITING_FOR_CONTEXT_BUNDLE`

Do not dispatch a standalone round for minor documentation-only semantic cleanup. The known F0 wording cleanup will be folded into the next M4 resume after the 109 context bundle arrives.

Resume under:

`CODEX_NEXT_STAGE_174NEW_Q05_WARM_PREFIX_REPLAY_V1.md`

First close actual F0 boundary semantics separately for:

- L1 data cache;
- L2 data cache;
- L1 TLB;
- L2 TLB;
- PWC;
- drained translation in-flight state.

Then, after M3 bundle is durable+ACK, replay:

```text
ISOLATED_Q05
P1  + Q05
P2  + Q05
P4  + Q05
P8  + Q05
P16 + Q05
P34 + Q05
```

Each warm row starts fresh and preserves state only within that row.

## Frozen workload

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT
batch      = 1
prefill    = 2048
decode     = 32
dtype      = FP16
backend    = SDPA
target     = Q05_PREFILL_ATTN_FLASH
occurrence = 0
```

Existing isolated-Q05 identities remain read-only:

```text
SIM_INPUT_0ab4e2fe2195d3b7d7da4ee9df6017cbec5c063fcc8110374e1a753f87177634
SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
SIM_RUN_92a553b0d69a9f41c5e20a8650366c53f7fed31c29c7462947d3af03c6f136f1
SIM_EVIDENCE_c8b4175d33f8bed7def2984489eadbdbcdfaffbfcb6a7daef33c8beb18e80959
```

Accepted core/producer anchors remain:

```text
framework execution source = d64408a97d76a320a6d49468653d416e33677af8
core                       = 57bb71ecd015b6ec0ab32e45b0815e5beaf69172
qualified binary SHA256    = 34deedd99e85e52fb309852de2ecc5fecd9471436a33a5e77d40bc038a2c31c4
producer                    = 5143b4e10aaf2fc47bb60492155d2464b0b726fd
validator hotfix            = fb5d0bebee421a0153661239e1f7c2bc088d5c9e
```

## Storage

node164 remains the durable authority.

Model-asset placement is asymmetric by design:

- node164 remains the authoritative copy for all model assets and receipts;
- node109 may retain local **replica copies of currently active capture models** for repeated GPU capture convenience. These replicas are non-authoritative, hash-verifiable, and may be cleaned later if space is needed;
- node174-new should not retain model-weight replicas. It should consume authoritative assets from node164 as needed and keep only simulator/source/small working state locally.

109 may also keep capture staging/working data until durable publication is closed. 174 local data remains working/simulation state only.

The new context bundle is formal only after per-member closure, bundle hash closure, destination verify/admit and ACK.

## Deferred side work

Still deferred while mainline uses the resource:

- Decode Flash follow-on capture after the shared LDC semantic issue is closed;
- Qwen3/DeepSeek campaigns;
- complementary GEMM/GEMV replay;
- NCU side campaigns;
- cleanup work;
- new mechanisms.

## STOP boundary

No TLB/PTW/cache mechanism, latency/capacity/page-size/Segment experiment may start automatically after warm-prefix results. Return the results to ChatGPT for scientific review.
