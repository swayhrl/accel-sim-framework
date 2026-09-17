# AWMA Current State

Date: 2026-09-17

## Coordination status

Current stage is now split into three logical tracks:

```text
Track A — 174-new
Q05 translation timeline closure
ACTIVE

Track B — 109
kernel target selection
COMPLETE / ACCEPTED

Track C — 109
storage governance + bounded GPU capture side lane
ACTIVE by new ChatGPT authorization
```

Track C supersedes the previous temporary instruction that node109 must remain idle while Track A runs. The reason is that Track B has now closed deterministic candidate identities and the RTX4080 is idle; storage governance is first made safe, then only those already-accepted candidates may be captured.

## Accepted Track B result

```text
branch = hrl/awma-kernel-target-selection-109-v1
HEAD   = e90fd76d3704df4a367bb04de09aee42d0cab803
status = AWMA_KERNEL_TARGET_SELECTION_V1_COMPLETE_WITH_SCOPE
review = PASS_WITHIN_SCOPE
```

Accepted candidates remain `CANDIDATE_ONLY_NOT_CAPTURED` until Track C requalifies them in a fresh exact run:

```text
PREFILL_GEMM_PRIMARY_1
  CUBLAS_GEMM / CUTLASS Kernel2
  grid/block = 128,3,1 / 256,1,1
  phase/function/shape occurrence = 12
  reference launch = 285 (navigation only)
  57.31% Prefill GEMM-family time
  38.10% total Prefill GPU time

DECODE_GEMV_PRIMARY_1
  CUBLAS_GEMV / internal::gemvx int6
  grid/block = 1216,1,1 / 16,4,1
  decode step = 1
  phase/function/shape occurrence = 10
  reference launch = 1244 (navigation only)
  1,536 recurrences across 32 decode steps
  40.64% Decode GEMV-family time
  20.22% total Decode GPU time

DECODE_FLASH_PRIMARY_1
  flash_fwd_splitkv_kernel
  grid/block = 1,9,14 / 128,1,1
  decode step = 1
  occurrence = 17
  reference launch = 1748 (navigation only)
  82.10% Decode Flash time

DECODE_FLASH_PRIMARY_2
  flash_fwd_splitkv_combine_kernel
  grid/block = 2,1,1 / 128,1,1
  decode step = 1
  occurrence = 0
  reference launch = 1018 (navigation only)
  17.90% Decode Flash time
```

The old Native `PREFILL_HEAVY_GEMM` exact identity remains:

```text
NATIVE_TARGET_MATCH_NOT_PROVEN
```

A secondary Decode GEMV shape `grid=18992,1,1 / block=8,8,1` remains backlog-only; it is not authorized for capture in Track C.

## Track A remains active and unchanged

174-new continues:

```text
AWMA_Q05_TRANSLATION_TIMELINE_CLOSURE_V1
```

using the existing node-specific specification.

It must still close:

- first-touch / pre-fill / post-fill attribution;
- cycle-keyed translation-key events;
- warm-after-fill behavior;
- same-unit 10k/50k/full coverage where source semantics allow.

Track C must not modify or depend on Track A's simulator worktree.

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

Current accepted Q05 simulation target remains:

```text
Q05_PREFILL_ATTN_FLASH
function occurrence = 0
pytorch_flash::flash_fwd_kernel<...>
```

## Frozen simulation identities

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
Characterization anchor     = bb92e5a1559dd7e2b2520e9a7a4937262664512c
```

## Accepted Q05 bounded/full facts

```text
R0 10k gpu_sim_insn = 1,084,480 completed active thread-instructions
I0 10k              = 1,697,696 (+56.55%)
R0 50k              = 11,587,872
I0 50k              = 20,458,400 (+76.55%)

125 miss requesters = 19 translation allocations + 106 merges
max waiter depth = 35
```

P2 and M8 did not yield measurable 10k progress gain.

Complete Q05 structure:

```text
224 CTA
896 warps
13,361,600 warp-instruction records
971,824 memory-instruction records
29,564,416 lane-address events
228 unique offline 64 KiB VPN
R0 natural completion = 885,681 cycles
```

The trace-file order remains `STRUCTURAL_TRACE_ORDER_ONLY`.

## Storage authority decision

The durable large-data owner is node164.

```text
node164 root:
/root/share/mnt164/huangrulin/c16_ai_workload/
```

Roles are frozen as:

```text
109 = GPU producer + short-lived local staging
174-new = analysis/simulator, not durable large-data storage
164 = durable large-data authority
```

Large artifacts including simulator-native traces, NSYS/NCU reports, NVBit raw, simulation raw, cycle timelines and large derived datasets belong on node164.

Existing accepted durable paths are provenance and must not be mass-moved for cleanliness.

Before new large side-lane captures are published, Track C must close:

```text
AWMA_164_DATA_PLANE_QUALIFIED_V1
```

using a 1-2 GiB partial/resume/size/SHA/rename/read-back canary.

No accepted scientific artifact may be deleted during this governance stage.

## Node roles now

### 174-new

Continue Track A only.

### 109 / RTX4080

Execute Track C in strict sequence:

```text
Phase A: storage governance / data-plane qualification
then, only after PASS,
Phase B: bounded simulator-native producer captures of the four accepted candidates
```

Track C may produce producer-qualified durable bundles only. It may not create new SIM_INPUT IDs or run simulation.

### node164

Own all new large Track C raw artifacts after durable publication and independent destination verification.

## Immediate execution order

Parallel:

```text
174-new:
CODEX_NEXT_STAGE_174NEW_Q05_TRANSLATION_TIMELINE_CLOSURE_V1.md

109:
CODEX_NEXT_STAGE_109_STORAGE_GOVERNANCE_AND_GPU_SIDELANE_V1.md
```

Read storage policy:

```text
STORAGE_GOVERNANCE_POLICY_V1.md
```

## Global STOP boundaries

Neither active track may automatically start:

- new TLB/PTW mechanisms;
- L2-TLB latency/PTW/walker/capacity/page-size sweeps;
- Segment;
- NCU campaigns;
- C16WARP1 campaigns;
- Qwen3/DeepSeek campaigns;
- admission or simulation of new Track C captures.

Track C is authorized only for the four selected Qwen2.5 candidate producer captures after storage qualification.
