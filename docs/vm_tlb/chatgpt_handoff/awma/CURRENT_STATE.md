# AWMA Current State

Date: 2026-09-17

## Coordination status

Current tracks:

```text
Track A — 174-new Q05 translation timeline closure
COMPLETE / report received

Track B — 109 kernel target selection
COMPLETE / ACCEPTED

Track C — 109 producer storage governance + bounded GPU capture side lane
ACTIVE

Track D — 174-new independent node164 storage consumer audit
WAITING_FOR_PRODUCER_CANARY

Track E — 174-new local-storage read-only inventory / cleanup-candidate audit
ACTIVE
```

Track E is intentionally read-only and independent of Track C progress. It exists to quantify 174-new local/host-backed storage usage and produce a safe cleanup candidate list. It does **not** authorize deletion.

## Track A completion facts

Reported completion marker:

`AWMA_Q05_TRANSLATION_TIMELINE_CLOSURE_V1_COMPLETE_WITH_SCOPE`

Reported branch:

`hrl/awma-q05-translation-timeline-174new-v1`

Diagnostic R0 10k preserved accepted science:

```text
cycle = 10,000
gpu_sim_insn = 1,084,480
issued CTA = 70
L1 = 930 / 805 / 125
L2 = 125 / 0 / 125
MSHR = 19 alloc / 106 merge / 0 full / HWM 16
walk = 19 / 19
max waiter depth = 35
requester latency total = 164,955
```

Actual diagnostic translation key:

`{asid, vpn, page_size}`

Timeline summary:

```text
10k:
19 keys / 19 fills / 106 merges / 8,730 post-fill REQUEST invocations

50k:
104 keys / 104 fills / 374 merges / 474,414 post-fill REQUEST invocations

full natural R0:
885,681 cycles
224 CTA
240 simulator keys / 240 fills / 393 merges
8,747,322 post-fill REQUEST invocations
max waiter depth = 35
```

Scientific classification remains `MIXED`.

Supported:

- strong pre-fill burst fanout exists;
- new translation keys continue beyond the early window;
- substantial post-fill activity exists;
- current evidence does not support simple TLB-capacity/thrashing.

Important boundary:

`REQUEST` is a simulator invocation/retry unit, not memory-instruction coverage. Post-fill L1/L2 outcome was not directly logged and remains unavailable. No mechanism experiment is authorized by the timeline result alone.

## Track B accepted target-selection result

Accepted branch/commit:

```text
hrl/awma-kernel-target-selection-109-v1
e90fd76d3704df4a367bb04de09aee42d0cab803
```

Authorized Track C candidates only:

```text
PREFILL_GEMM_PRIMARY_1
  CUTLASS Kernel2
  grid/block = 128,3,1 / 256,1,1
  occurrence = 12

DECODE_GEMV_PRIMARY_1
  internal::gemvx int6
  grid/block = 1216,1,1 / 16,4,1
  decode step = 1
  occurrence = 10

DECODE_FLASH_PRIMARY_1
  flash_fwd_splitkv_kernel
  grid/block = 1,9,14 / 128,1,1
  decode step = 1
  occurrence = 17

DECODE_FLASH_PRIMARY_2
  flash_fwd_splitkv_combine_kernel
  grid/block = 2,1,1 / 128,1,1
  decode step = 1
  occurrence = 0
```

Reference global launch numbers are navigation aids only. The old Native `PREFILL_HEAVY_GEMM` alignment remains `NATIVE_TARGET_MATCH_NOT_PROVEN`.

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

Accepted Q05 target:

```text
Q05_PREFILL_ATTN_FLASH
function occurrence = 0
pytorch_flash::flash_fwd_kernel<...>
```

Frozen Simulation IDs remain read-only:

```text
SIM_INPUT_0ab4e2fe2195d3b7d7da4ee9df6017cbec5c063fcc8110374e1a753f87177634
SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
SIM_RUN_92a553b0d69a9f41c5e20a8650366c53f7fed31c29c7462947d3af03c6f136f1
SIM_EVIDENCE_c8b4175d33f8bed7def2984489eadbdbcdfaffbfcb6a7daef33c8beb18e80959
```

## Storage authority

Durable large-data owner:

`/root/share/mnt164/huangrulin/c16_ai_workload/`

Frozen roles:

```text
109 = GPU producer + short-lived local staging
174-new = simulator / analysis / worktree host, not durable large-data authority
164 = durable large-data authority
```

Large accepted artifacts must not depend on 174-new local disk for long-term retention.

## Track C — node109

Continue existing producer-side storage governance and bounded selected-kernel capture goal.

Strict gate:

```text
storage data-plane qualification
-> AWMA_164_DATA_PLANE_QUALIFIED_V1
-> only then bounded captures
```

No SIM_INPUT admission or simulation is authorized.

## Track D — 174-new durable-consumer audit

Reported status:

`AWMA_174NEW_STORAGE_CONSUMER_AUDIT_V1_WAITING_FOR_PRODUCER_CANARY`

The independent existing-data audit is complete. It verified mount/capacity/permissions, indexed accepted Q05 simulator-native trace/natural simulation raw/translation timeline raw, rehashed key Q05 provenance artifacts, and found no need to move/delete accepted evidence.

Track D must remain stopped until Track C producer canary receipt/ACK becomes visible. Then only a small delta consumer verification is needed; do not rerun the full audit.

## Track E — 174-new local storage audit

Execute:

`CODEX_NEXT_STAGE_174NEW_LOCAL_STORAGE_AUDIT_V1.md`

Purpose:

- establish mount/filesystem topology;
- measure local/host-backed storage without counting node164;
- identify largest directories/files and worktree/build/cache footprint;
- determine whether accepted AWMA data has local duplicate working copies;
- classify cleanup candidates by evidence and risk;
- estimate conservative and upper-bound reclaimable bytes;
- perform **no deletion, move, prune, compression, or worktree cleanup**.

Expected completion:

`AWMA_174NEW_LOCAL_STORAGE_AUDIT_V1_COMPLETE_WITH_SCOPE`

## Immediate execution

Parallel:

```text
109:
continue CODEX_NEXT_STAGE_109_STORAGE_GOVERNANCE_AND_GPU_SIDELANE_V1.md

174-new:
execute CODEX_NEXT_STAGE_174NEW_LOCAL_STORAGE_AUDIT_V1.md
```

Track D remains waiting for producer canary.

## Global STOP boundaries

Current tracks may not automatically start:

- new TLB/PTW/cache mechanisms;
- latency/PTW/walker/capacity/page-size/Segment sweeps;
- NCU/C16WARP1 or Qwen3/DeepSeek campaigns beyond current Track C authorization;
- SIM_INPUT admission or simulation of Track C captures;
- deletion, pruning, cleanup, mass move, compression, or physical reorganization of accepted/local scientific data.
