# AWMA Current State

Date: 2026-09-18

## Coordination stage

`AWMA_Q05_LOOKUP_MODEL_VALIDITY_CLOSURE_174NEW_V1`

Node174-new remains the active scientific mainline.

Node109 has no AWMA task and remains released for user work.

## Accepted lookup-path decomposition

Execution:

```text
hrl/awma-q05-contextual-lookup-decomposition-174new-v1
07d8c3cdd414b0a881264df341685e864fed2761
```

Status:

`AWMA_Q05_CONTEXTUAL_LOOKUP_PATH_DECOMPOSITION_174NEW_V1_COMPLETE_WITH_SCOPE`

P34 target-only matrix:

```text
L1/L2    cycles      delta vs 10/80
10/80    871835      0
 5/80    778598     -93237
 2/80    771796    -100039
 0/80    748102    -123733
10/40    904750     +32915
10/0     878836      +7001
 0/0     657110    -214725
I0       674121    -197714
```

P8 shows the same strong direction for L1 shortening.

## What is accepted

- target L1 lookup timing has a strong effect on modeled Q05 cycles;
- P8 and P34 diagnostic-disabled controls reproduce;
- P34 prior target-I0 reproduces;
- L2-only latency perturbation is non-monotonic;
- zero/zero and I0 are not equivalent;
- no architecture mechanism has been evaluated.

## Critical interpretation boundary

The previous matrix is **not a pure additive lookup-latency subtraction**.

The accepted controller performs the actual TLB `probe()` only when the configured lookup service interval completes.

Therefore changing lookup latency also changes **when the evolving TLB state is sampled**.

Observed evidence:

```text
P34 L1 launches
10/80 = 776915
5/80  = 779016
2/80  = 786997
0/80  = 865036

P34 L2 misses
10/80 = 249
5/80  = 306
2/80  = 307
0/80  = 308

P34 L2 misses under L2-only changes
80 cycles = 249
40 cycles = 277
 0 cycles = 304
```

Thus faster service can cause a lookup to probe before a concurrent fill that the slower lookup would have observed.

This timing/fill-order coupling must be characterized before mechanism interpretation.

## Lookup-latency provenance concern

Accepted core history introduces:

```text
L1 lookup latency = 10
L2 lookup latency = 80
```

in:

`swayhrl/gpgpu-sim @ 5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

with source descriptions:

```text
generic M3 L1 TLB lookup service cycles
generic M3 L2 TLB lookup service cycles
```

Until a direct project calibration receipt is found, these values must be treated as model parameters, not RTX4080 hardware facts.

## Same-trace baseline remains frozen

```text
FORMAL_ISOLATED_R0 = 864552
P2_R0              = 848511
P8_R0              = 835145
P34_R0             = 871835
```

Historical standalone isolated 885681 remains cross-capture evidence only.

## Active mainline

Execute:

`CODEX_NEXT_STAGE_174NEW_Q05_LOOKUP_MODEL_VALIDITY_V1.md`

Goals:

1. close 10/80 provenance;
2. mine invocation/retry accounting from existing logs;
3. prove probe-time coupling from source;
4. add read-only launch-vs-completion residency telemetry;
5. rerun only the bounded existing lookup points;
6. classify the lookup-sensitivity result;
7. prepare, but do not execute, a future RTX4080 native TLB calibration plan.

## No mechanism policy

No faster-TLB/PTW/cache mechanism is authorized until lookup-model validity closes.

## Node109

Accepted unattended side-lane closeout remains:

```text
hrl/awma-109-unattended-capture-campaign-v1
8f49ba3b9228b5f8a9163e961225ffd415107734
```

Node109 GPU remains released.

## STOP boundary

Return model-validity evidence to ChatGPT before any architecture mechanism or RTX4080 calibration campaign.
