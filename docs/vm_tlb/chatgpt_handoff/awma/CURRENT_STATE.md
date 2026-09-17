# AWMA Current State

Date: 2026-09-17

## Coordination status

Current execution tracks:

```text
Track A — 174-new
Q05 translation timeline closure
COMPLETE / report received

Track B — 109
kernel target selection
COMPLETE / ACCEPTED

Track C — 109
storage governance + bounded GPU capture side lane
ACTIVE

Track D — 174-new
independent node164 storage consumer audit
ACTIVE
```

Track C and Track D are intentionally complementary:

- 109 proves producer-side finalize/publish/ACK and then may use the RTX4080 for bounded selected-kernel captures;
- 174-new independently proves that node164 can be consumed as a durable authority without relying on 109 local paths or 174 local disk.

## Track A completion facts

Reported completion marker:

`AWMA_Q05_TRANSLATION_TIMELINE_CLOSURE_V1_COMPLETE_WITH_SCOPE`

Execution branch reported by Codex:

`hrl/awma-q05-translation-timeline-174new-v1`

Key diagnostic-neutrality facts:

```text
R0 10k matches accepted science:
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

Diagnostic translation key is:

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

Scientific classification remains:

`MIXED`

Supported:

- clear pre-fill burst fanout exists;
- substantial post-fill activity continues across the kernel;
- the evidence does not support a simple TLB-capacity/thrashing explanation.

Important boundary:

`REQUEST` is a simulator invocation/retry unit, not memory-instruction coverage. Post-fill L1/L2 outcome was not directly logged and remains unavailable.

No TLB/PTW mechanism or latency/capacity/page-size/Segment experiment has been authorized by this completion alone.

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
  phase/function/shape occurrence = 12

DECODE_GEMV_PRIMARY_1
  internal::gemvx int6
  grid/block = 1216,1,1 / 16,4,1
  decode step = 1
  phase/function/shape occurrence = 10

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

Reference global launch numbers are navigation aids only and may not be used as scientific identity.

The old Native `PREFILL_HEAVY_GEMM` exact alignment remains `NATIVE_TARGET_MATCH_NOT_PROVEN`.

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

Current accepted Q05 target remains:

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
174-new = simulator / analysis / independent durable-consumer audit
164 = durable large-data authority
```

Large artifacts must not depend on 174-new local disk for long-term retention.

Existing accepted paths must not be mass-moved for cleanliness.

### Track C — 109

Strict order:

1. storage governance + 1-2 GiB producer-side data-plane canary;
2. reach `AWMA_164_DATA_PLANE_QUALIFIED_V1`;
3. only then perform bounded producer captures of the four authorized candidates;
4. publish producer-qualified durable bundles to node164;
5. no SIM_INPUT admission or simulation.

### Track D — 174-new

Execute the independent read-side audit:

`CODEX_NEXT_STAGE_174NEW_STORAGE_CONSUMER_AUDIT_V1.md`

Required goals:

- audit node164 mount/capacity/permissions from 174-new;
- independently inventory accepted Q05 trace, simulation raw, translation timeline raw and S2 census inventory;
- independently verify producer canary receipt/ACK when available;
- verify durable catalog is consumable without producer-local paths;
- identify orphan partials / local-only large artifacts / duplicate authority / cleanup candidates;
- no deletion or mass move.

## Immediate execution

Parallel:

```text
109:
CODEX_NEXT_STAGE_109_STORAGE_GOVERNANCE_AND_GPU_SIDELANE_V1.md

174-new:
CODEX_NEXT_STAGE_174NEW_STORAGE_CONSUMER_AUDIT_V1.md
```

Read policy:

`STORAGE_GOVERNANCE_POLICY_V1.md`

## Global STOP boundaries

Neither track may automatically start:

- new TLB/PTW/cache mechanisms;
- L2-TLB latency/PTW/walker/capacity/page-size sweeps;
- Segment;
- NCU/C16WARP1 campaigns;
- Qwen3/DeepSeek campaigns;
- SIM_INPUT admission or simulation of Track C captures;
- deletion or physical reorganization of accepted durable data.
