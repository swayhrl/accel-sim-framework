# R19 Lane E final review — IBP direct-consumer design

Date: 2026-10-01

Execution authority:
- branch: `hrl/awma-r19e1-ibp-direct-consumer-design-174new-v1`
- commit: `a758be1017f35caa55dda6ad529d1b6c5f141553`
- tree: `dd75c5e1326b2ff9cb491f5b7ecdbb7be30bc187`
- formal label: `R19E1_IBP_DIRECT_CONSUMER_DIAGNOSTIC_NOT_QUALIFIED`

## Accepted facts

The parent R19 scout correctly identified a real Legion/Reddit boundary:
- sampler reconstructs full sampled `N2 x 602` FP32 features into a GPU dense buffer;
- trainer then allocates a second full tensor and performs a device-to-device copy;
- only after that does the first GraphSAGE SAGEConv consume features.

The first GraphSAGE layer:
- performs `fc_neigh` once per unique sampled source row;
- reuses transformed source rows across multiple edges;
- separately applies `fc_self` to the destination prefix;
- performs DGL g-SpMM mean aggregation;
- participates in trainer-owned autograd/backward/Adam.

Therefore a naive decode-per-edge or decode-and-immediately-consume transformation changes work/reuse/rounding semantics.

## Why P1/P2/P3 do not qualify

P1:
moves trainable first-layer execution/autograd across process ownership and replaces one IPC contract with another. Not a boundary-only intervention.

P2:
can preserve unique-row decode/reuse, but requires tiled linears plus per-tile IPC/synchronization. A B0-vs-D1 comparison would confound dense-buffer removal with GEMM shape/algorithm and synchronization changes.

A future causal P2 study would need at least an additional matched control using the same tiled consumer/synchronization while retaining the full dense source boundary. That materially expands the experiment and is not justified before the dense boundary has independent evidence of cost.

P3:
requires a custom decode-aware first-layer forward/backward and explicit reuse handling; too invasive to isolate the original boundary.

Thus no current same-semantics two-arm diagnostic is qualified.

## Numerical boundary

Feature reconstruction remains bitwise lossless.

First-layer output bitwise determinism is unknown without a runtime replay because pinned DGL CUDA COO reduction contains floating-point atomics and runtime sparse dispatch is not yet bound.

The pre-registered future rule in the E1 pack is accepted:
- first establish B0 repeated-output behavior before any D1 performance run;
- if deterministic, require exact output identity;
- if not, freeze a B0-derived numerical interval before D1;
- never widen tolerance after D1.

## Separate software fact: trainer-side second D2D copy

Pinned Legion code contains a commented `torch::from_blob(float_features,...)` zero-copy view, followed by the active path:
- allocate a second `[N2,602]` CUDA tensor;
- `cudaMemcpyDeviceToDevice` the full feature buffer.

The source comment says:
`Creating a new tensor and copying works better than from_blob. I dont know why.`

This is a real but separate software/runtime question. It does not remove the sampler's first full dense materialization and is not the R19 direct-consumer hypothesis.

Project decision:
- do not build a new Legion/Reddit environment solely to retest this copy;
- if a qualified Legion runtime is created for another reason, this may be measured as a cheap software canary;
- do not interpret it as an architecture opportunity without independent critical-path evidence.

## Final project interpretation

Accept:
`R19E1_IBP_DIRECT_CONSUMER_DIAGNOSTIC_NOT_QUALIFIED`

Meaning:

> The source-level opportunity remains conceptually plausible, but with the current training/process/dataflow organization we cannot construct a bounded matched intervention that removes only the sampled-feature dense boundary while preserving GraphSAGE work, reuse, autograd ownership, synchronization and numerical semantics.

This is not evidence that the dense buffer costs zero time. It is evidence that the current proposed experiment cannot causally measure that cost.

## Lane state

Lane E / IBP direct-consumer: STOP.
No 109 Native run.
No Accel-Sim.
No hardware mechanism.

Lane F R19F1 remains active/authorized.
Lane G fast-weight is STOP.
