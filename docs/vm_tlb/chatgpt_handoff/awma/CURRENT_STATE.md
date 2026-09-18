# AWMA Current State

Date: 2026-09-18

## Coordination stage

`AWMA_Q05_CONTEXTUAL_LOOKUP_PATH_DECOMPOSITION_174NEW_V1`

Node174-new remains the active scientific mainline.

Node109 unattended side lane is closed and GPU is released for user work.

## Accepted context-effect decomposition

Execution:

```text
hrl/awma-q05-context-effect-decomposition-174new-v1
b24edffd7a90fc6417b95c6d4198f5c40dcf0b35
```

Status:

`AWMA_Q05_CONTEXT_EFFECT_DECOMPOSITION_174NEW_V1_COMPLETE_WITH_SCOPE`

Target-only Q05 I0 results:

```text
context            R0 cycles   Q05-I0 cycles   sensitivity
FORMAL_ISOLATED       864552          670682      -22.42%
P2                    848511          701244      -17.36%
P8                    835145          664241      -20.46%
P34                   871835          674121      -22.68%
```

The target-only diagnostic is accepted:

- every predecessor remains natural F0/R0;
- only exact Q05 bypasses TLB/MSHR/PTW/PWC/PTE;
- natural identity-compatible SimVA->SimPA is preserved;
- P8/P34 disabled controls reproduce accepted natural metrics exactly;
- no TLB/PTW/cache mechanism was run.

## Critical same-trace baseline correction

Direct contextual cycle comparisons must use:

`FORMAL_ISOLATED_R0 = 864552 cycles`

because it uses the same admitted context-bundle member34 trace identity as P2/P8/P34.

The older:

`885681 cycles`

isolated result remains a valid historical standalone-Q05 result but comes from the earlier standalone capture/input identity. It must not be used as the primary same-trace cycle denominator.

Correct same-trace natural comparisons:

```text
P2  vs formal isolated: -1.86%
P8  vs formal isolated: -3.40%
P34 vs formal isolated: +0.84%
```

Formal isolated -> P34:

```text
walks:       240 -> 15
L2-TLB miss: 731 -> 249
cycles:      864552 -> 871835
```

Therefore full real predecessor history removes almost all modeled walks and most L2-TLB misses, but its total inherited context slightly worsens Q05 cycles relative to the same-trace isolated control.

This supersedes the earlier cross-capture cycle-delta interpretation; historical evidence itself is not rewritten.

## Why the next stage targets lookup service

P34 natural Q05:

```text
L1 accesses = 776915
L1 hits     = 773501
L1 misses   = 3414
L1 hit rate = ~99.56%

L2 accesses = 3414
L2 hits     = 3165
L2 misses   = 249
walk starts = 15
```

Accepted modeled lookup latencies:

```text
L1 TLB = 10 cycles
L2 TLB = 80 cycles
PWC    = 1 cycle
```

Requester-latency composition:

```text
L1 service  = 7,769,150 requester-cycles
L2 service  =   273,120
MSHR wait   =   434,431
L2 queue    =       681
total       = 8,477,382
```

The L1-service term is ~91.65% of the summed requester-latency composition.

These are not exposed GPU cycles, so they cannot predict speedup directly. They motivate a target-only latency decomposition.

## Active mainline

Execute:

`CODEX_NEXT_STAGE_174NEW_Q05_CONTEXTUAL_LOOKUP_PATH_DECOMPOSITION_V1.md`

Core idea:

```text
prefix = natural R0
Q05 only:
  vary L1 lookup latency
  vary L2 lookup latency
  preserve capacity/ports/state/mapping
```

P34 is the realism reference and receives the full matrix.

P8 is the screening candidate and receives a reduced matrix.

## Baseline policy

Until this stage returns:

- P34 = realism reference;
- P8 = screening-prefix candidate;
- formal isolated member34 = same-trace isolated control;
- historical standalone isolated Q05 = historical cross-capture reference;
- no architecture mechanism is yet authorized.

## 109 side-lane status

Accepted closeout:

```text
hrl/awma-109-unattended-capture-campaign-v1
8f49ba3b9228b5f8a9163e961225ffd415107734
```

Decision:

`AWMA_109_UNATTENDED_CAPTURE_CAMPAIGN_V1_COMPLETE_WITH_SCOPE`

16 immutable node164-ACKed bundles were produced. Node109 GPU is released.

## STOP boundary

Return lookup-path decomposition results to ChatGPT before any TLB/PTW/cache mechanism design or sweep.
