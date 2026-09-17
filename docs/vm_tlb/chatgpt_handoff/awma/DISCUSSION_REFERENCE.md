# AWMA Discussion Reference — storage governance and GPU side lane

Date: 2026-09-17

## 1. Why storage governance is now the first infrastructure task

AWMA already produces large artifacts:

- model weights;
- full NSYS inventories;
- Native/NVBit traces;
- simulator-native trace bundles;
- full natural-completion simulator output;
- future cycle-keyed translation timelines.

The project role model has always been:

```text
109 = GPU producer
174-new = simulator / analysis
164 = durable large-data storage
```

The current accepted Q05 simulator-native trace is already durable on node164, and the complete natural-completion Q05 simulator evidence is also stored on node164. Therefore the correct long-term direction is not to expand 174-new local storage usage, but to formalize a reliable producer-to-164 data plane and a catalog/retention policy.

The new storage-governance stage does not move accepted historical data simply to make the directory tree prettier. Historical durable paths are provenance.

The first required closure is a 1-2 GiB synthetic canary proving:

```text
109 local source
 -> hrl174new transport path
 -> node164 .partial
 -> resume
 -> size closure
 -> SHA256 closure
 -> promotion/rename
 -> read-back hash
 -> cleanup only after verification
```

This closes the difference between “small scratch writes work” and “large formal captures can be safely published”.

## 2. Why node174 should not become the data disk

174-new is the long-term analysis/simulation node, but large-data authority on its local filesystem is undesirable because:

- simulator-native traces can grow rapidly;
- multiple full simulator runs can accumulate large logs/timelines;
- future multi-model Native campaigns will produce much more raw data;
- 164 is already the project’s large durable namespace.

Therefore:

```text
174 local disk = code / worktree / small scratch / small summaries
164 = large durable raw + derived authority
```

A large temporary 174 copy is always a working copy, never the only authoritative copy.

## 3. Why 109 no longer needs to remain idle

The previous coordination stage intentionally kept node109 idle while candidate selection was incomplete.

That condition has changed.

Accepted target-selection result:

```text
branch = hrl/awma-kernel-target-selection-109-v1
HEAD   = e90fd76d3704df4a367bb04de09aee42d0cab803
status = PASS_WITHIN_SCOPE
```

The selected targets are not arbitrary launches. They were selected from the exact frozen S2 census by implementation family, launch shape, recurrence and GPU-time contribution.

The important selected coverage is:

```text
Prefill primary GEMM:
  57.31% Prefill GEMM-family time
  38.10% total Prefill GPU time

Decode primary GEMV:
  40.64% Decode GEMV-family time
  20.22% total Decode GPU time

Decode Flash splitkv:
  82.10% Decode Flash time

Decode Flash splitkv-combine:
  17.90% Decode Flash time
```

Q05 remains representative only for one Prefill FlashAttention family. The selected targets therefore add exactly the missing execution families that future cross-kernel TLB/cache analysis will need.

## 4. Why capture can proceed before the 174-new Q05 timeline finishes

The 174-new active task asks a different question:

> For the already accepted Q05 trace, is the observed translation pressure mainly cold first-touch, pre-fill fanout, or persistent post-fill behavior?

The new 109 side lane does not need that answer in order to create producer-qualified input bundles for already selected complementary kernel families.

Capturing these targets now does not commit the project to a particular TLB mechanism. It only prepares future simulation/native evidence so the next scientific round does not wait for GPU production.

The side lane is therefore useful pipeline overlap:

```text
174-new: Q05 translation timeline analysis
||
109: storage qualification -> complementary target capture
```

The scientific decision about how to use the new captures remains deferred until ChatGPT reviews Track A and Track C together.

## 5. Why storage qualification must precede new formal capture

The project should not deliberately create new large traces before proving where and how they will be durably stored.

Thus the new 109 goal is sequential:

```text
Phase A
storage governance / data-plane canary / catalog

PASS gate:
AWMA_164_DATA_PLANE_QUALIFIED_V1

Phase B
bounded selected-kernel simulator-native capture
```

If storage qualification fails, the GPU capture phase does not start.

## 6. Identity discipline for the new target captures

The target-selection review pack records `reference_launch_index`, but that value is not a stable scientific identity across reruns.

Each new capture must re-close identity using:

```text
frozen workload
+ phase
+ decode step where applicable
+ exact kernel function
+ grid/block
+ deterministic occurrence within phase/function/shape
```

Accepted candidate identities from the target-selection pack are:

```text
PREFILL_GEMM_PRIMARY_1
  occurrence 12
  grid/block 128,3,1 / 256,1,1

DECODE_GEMV_PRIMARY_1
  decode step 1
  occurrence 10
  grid/block 1216,1,1 / 16,4,1

DECODE_FLASH_PRIMARY_1
  decode step 1
  occurrence 17
  grid/block 1,9,14 / 128,1,1

DECODE_FLASH_PRIMARY_2
  decode step 1
  occurrence 0
  grid/block 2,1,1 / 128,1,1
```

A candidate whose identity does not re-close is skipped rather than guessed.

## 7. Why the capture side lane is bounded

A full instruction trace can be much larger than an NSYS inventory. GPU idle time is not a reason to create unbounded raw data.

Each candidate therefore receives:

```text
identity requalification
 -> bounded capture canary
 -> size/time guard
 -> whole-kernel capture only if feasible
```

Current guard:

```text
8 GiB durable bundle per target
30 minutes per capture attempt
32 GiB aggregate new durable raw
```

A guard-triggered partial capture is diagnostic only and is never admitted as a complete trace.

## 8. Why the side lane uses the accepted simulator-native producer

The current objective is future Accel-Sim-ready selected-kernel input, not another Native-only memory sample.

Therefore the side lane uses the accepted simulator-native producer authority and must preserve:

```text
terminal COMPLETE
drop = 0
overflow = 0
mode-2/base_delta = 0
strict formatter/grammar closure
```

It must not substitute C16WARP1 for whole-kernel simulation input.

If a new kernel reveals a genuinely new SASS semantic/trace-contract issue, the correct outcome is a scientific review stop, not fake address/width/immediate fields or relaxed validation.

## 9. Why no new NCU/Qwen3/DeepSeek campaign starts yet

There are several valuable future GPU tasks, including:

- secondary long-duration Decode GEMV shape;
- Qwen3-30B S2 target requalification;
- DeepSeek-V2-Lite MLA/MoE target work;
- selected-kernel NCU.

However, the current four Qwen2.5 targets are the most direct continuation of the accepted current-model simulation line and are likely to be consumed soonest.

This stage therefore stops after their bounded producer capture attempts. Other GPU work remains backlog and requires a new handoff.

## 10. Scientific boundary

Track C produces data assets; it does not produce new TLB mechanism conclusions.

After Track A and Track C complete, ChatGPT should jointly review:

```text
Q05 dynamic cold/warm/fanout behavior
+
which complementary target bundles were successfully captured
```

Then decide the next analysis matrix and whether new SIM_INPUT admission should begin.
