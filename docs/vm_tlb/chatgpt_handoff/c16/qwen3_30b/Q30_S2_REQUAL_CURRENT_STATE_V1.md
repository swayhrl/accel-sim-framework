# Q30 S2/T2048 Target Requalification — Current State V1

Status: `S2_STATE_REPLAY_ACCEPTED / FORMAL_CAPTURE_NOT_STARTED`

## Accepted scientific authorities

Model:

```text
Qwen/Qwen3-30B-A3B
revision: ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Accepted upstream sequence:

```text
asset archive:
d048d1a5348ff3ace248d1e62cdd8e071a82d5d1

control/input/layout prep:
674d7acda0aaf072b7cd12cac84da9264b559cb2

CPU streaming integration hardening:
6034071c76279952c1476626552a9eaaaab6ef0b

S0 semantic streaming + exact replay:
ba4358b8059be4fb5756f49852e50ecfe7dea9a3

S0 layer-local target qualification:
acbda39f5714cedb0e8b88ec32b07b4db2845885

S2/T2048 semantic state + exact replay:
ee67225edc8fc5868de585d38e0391cbeb755d9f
```

The accepted S2 decision is:

```text
Q30_S2_T2048_STATE_REPLAY_PASS
FORMAL_CAPTURE_NOT_YET_AUTHORIZED
```

## Preserved deployment on node109

Model working copy:

```text
/data/c16/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Runtime:

```text
/data/c16/env/c16-qwen3-30b-hf451-gpu
```

Frozen deployment identity remains the accepted HF 4.51.0 BF16 SDPA Qwen3-MoE baseline. Do not upgrade, quantize, fuse, prune, change expert count/top-k, or change attention implementation during qualification.

## S0 qualification authority

The accepted S0 matrix at `acbda39f...` froze four layer-24 candidates:

```text
Q30_PF_ATTENTION_FLASH
  phase: PREFILL
  family: ATTENTION
  S0 occurrence: layer24 ordinal 48
  S0 static GLOBAL MREFs: 23

Q30_PF_EXPERT_GEMM
  phase: PREFILL
  family: EXPERT_PROJECTION_OR_GEMM
  S0 occurrence: layer24 ordinal 96
  S0 static GLOBAL MREFs: 47

Q30_DEC3_ATTENTION_SPLITKV
  phase: DECODE
  family: ATTENTION
  S0 occurrence: layer24 ordinal 47
  S0 static GLOBAL MREFs: 57

Q30_DEC3_EXPERT_GEMV
  phase: DECODE
  family: EXPERT_PROJECTION_OR_GEMM
  S0 occurrence: layer24 ordinal 202
  S0 static GLOBAL MREFs: 243
```

These values are S0 authority only. They are **not** transferable to S2 by assumption.

## S2 authority

Scenario:

```text
Q30_S2_TEXT
B1 / T2048 / parent decode binding D32
bounded semantic execution used for state generation: Prefill + Decode steps 0..3
classification: Q30_S2_TEXT_PREFIX_D4
```

Accepted local/state run ID:

```text
Q30_S2_STREAM_V1_20260917T001000Z
```

Accepted node164 provenance root:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/
qwen3_30b_replay_states/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
Q30_S2_STREAM_V1_20260917T001000Z/
```

Use the local S2 target-state bundles under the corresponding node109 bringup run if still present; otherwise restore only from the accepted node164 replay-state provenance after exact SHA verification. Do not regenerate the whole S2 semantic run merely for qualification when accepted states are intact.

Fixed S2 qualification states are:

```text
PREFILL / Layer 24 / T2048
DECODE / step 3 / Layer 24 / long-KV state
```

Both states already passed two fresh-process complete-layer replays with source/router bitwise equality and replay determinism.

## Scientifically important S0 -> S2 scaling already established

At Layer 24 Prefill:

```text
context:                 128 -> 2048
MoE assignments:        1,024 -> 16,384
unique experts:             75 -> 92
KV bytes:              6,291,456 -> 100,663,296
target-state bytes:    ~7.47 MB -> ~119.19 MB
replay peak allocated: 1,268,723,200 -> 1,478,141,440 bytes
```

At Decode step 3:

```text
input hidden shape remains [1,1,2048]
assignments remain 8
unique selected experts remain 8
KV bytes grow from 12,926,976 to 201,670,656
replay peak allocated grows from 1,271,945,728 to 1,492,218,368 bytes
```

These are semantic/state quantities only. They do **not** establish S2 kernel identity, launch ordinal, static MREF identity, DRAM traffic, L2 traffic, or trace footprint.

## Why requalification is required

The next stage must determine from actual S2 replay evidence whether S0 target families preserve or change:

```text
kernel implementation/function
launch count and ordinal
grid/block shape
attention algorithm variant
expert kernel variant
code-object/function identity
static GLOBAL MREF set
executed static MREF subset
bounded NCU DRAM/L2/SM behavior
```

In particular, the following are prohibited assumptions:

```text
S0 ordinal == S2 ordinal
S0 static MREF count == S2 static MREF count
S0 attention kernel == S2 attention kernel
S0 expert GEMM/GEMV identity == S2 identity
S0 NCU traffic is representative of S2
```

## Stage boundary

This requalification stage may run diagnostic/qualification tooling:

```text
NSYS kernel census
bounded NCU characterization
NVBit static/no-payload MREF mapping
one-MREF reachability canaries
```

It must **not** run the formal large capture campaign:

```text
no complete dynamic MREF-sharded trace set
no large NVBit payload capture
no broad formal NCU matrix
no S2_CODE / S2_STRUCTURED
no new semantic state generation unless accepted S2 state is invalidated
```

The deliverable is a final evidence-backed capture portfolio and exact identities for the next formal-capture Goal.