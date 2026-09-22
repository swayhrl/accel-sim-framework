# AWMA Cross-view Decision — Translation Hit-Path Validity

Date: 2026-09-22

Accepted Native authority:

`hrl/awma-109-exact-target-native-crossview-v1 @ 2122eccc7aed61d05b114075e1c3126c4308e64b`

Accepted Simulation authority:

`hrl/awma-174-exact-f0-segment-state-v3r1 @ 7a4f2a419fe77c017cb9a9a5555b1551a2fc884c`

## 1. Decision

Primary mainline classification:

`HITPATH_SENSITIVITY_SYSTEMATIC_ACROSS_KERNEL_CLASSES`

Mainline consequence:

`SIMULATOR_HITPATH_MODEL_REQUIRES_SEMANTIC_RECALIBRATION_BEFORE_MECHANISM`

No TLB/PTW/cache mechanism is authorized.

## 2. Exact cross-target result

All three targets use the same repaired F0 model class.

Segment is functionally dormant:

`F0_SEGMENT_FUNCTIONALLY_DORMANT_CONFIRMED`

Cross-target table:

```text
Target  Family          10/80 cycles  0/80 cycles  L1-zero reduction  L1 hit rate   walks / 1K L1
T0      FlashAttention    1,654,548      711,464       56.9995%        99.8907%        0.07765
T1      Prefill GEMM      3,114,834    1,252,198       59.7989%        99.8745%        0.06885
T2      Decode GEMV         152,777       71,654       53.0990%        99.7112%        0.32573
```

Thus the large modeled sensitivity is not specific to the Attention target.

## 3. Why this is a model-validity signal

For all three targets:

- L1-TLB hit rate is above 99.7%;
- PTW/walk activity is sparse relative to lookup volume;
- setting only the modeled L1 lookup service latency from 10 to 0 cycles reduces total simulated cycles by roughly 53-60%.

The direction and magnitude persist across:

- FlashAttention;
- a large Prefill GEMM;
- a much smaller Decode GEMV.

This makes a target-specific explanation insufficient.

The result does NOT imply that RTX4080 hardware TLB hit latency has this performance cost.

The simulator is not hardware-calibrated for that claim.

## 4. Native cross-view context

T1 and T2 differ materially in Native dynamic regime.

T1 accepted Native descriptors:

```text
memory instructions = 2,298,240
lane addresses       = 70,352,896
64 KiB pages         = 495
```

T2:

```text
memory instructions = 318,592
lane addresses       = 9,022,720
64 KiB pages         = 135
```

Yet both show large repaired-model L1 hit-path sensitivity.

Approximate simulator lookup density against accepted Native descriptors:

```text
T1: ~3.12 L1 translation lookups / Native memory-instruction record
T2: ~1.29 L1 translation lookups / Native memory-instruction record
```

These are Cross-view descriptive ratios, not an assertion that Native and Simulation event definitions are identical.

## 5. T2 nonlinear downstream effect

T2 requires a specific caveat.

```text
10/80:
  instructions = 43,357,696
  CTA          = 1,216
  L1 lookups   = 411,386
  admissions   = 411,008

0/80:
  instructions = 43,357,696
  CTA          = 1,216
  L1 lookups   = 411,703
  admissions   = 476,907
```

Thus:

- instruction and CTA completion are identical;
- L1 lookup count changes by only ~0.077%;
- downstream admission count increases by ~16.0%.

Therefore T2's 53.099% cycle reduction is qualitatively aligned with T0/T1 but is not a pure additive latency effect.

It is evidence that changing lookup timing can alter downstream retry/admission/scheduling behavior.

Classify T2 as:

`QUALITATIVELY_ALIGNED_WITH_NONLINEAR_DOWNSTREAM_EFFECT`

Do not hide this difference.

## 6. Stronger clean anchors

T0 and T1 are the clean cross-target anchors because their downstream admission counts remain invariant across 10/80 and 0/80.

Their reductions are:

```text
T0 = 56.9995%
T1 = 59.7989%
```

This alone establishes that the large sensitivity is not Attention-specific.

T2 independently confirms the same direction and similar magnitude, with the nonlinear-admission caveat above.

## 7. Source-level hypothesis to test next

The repaired coverage contract requires:

> before each L1D or bypass-ICNT downstream admission, the exact `accessq_back()`
> must already have `vm_translation_applied`; otherwise the memory pipeline
> returns `COAL_STALL`.

The current lookup model also assigns a positive L1 service interval before a hit becomes ready.

A high-priority hypothesis is therefore:

`SERIALIZED_OR_HEAD_OF_LINE_PRE_ADMISSION_TRANSLATION_WAIT`

i.e. the modeled 10-cycle L1 hit service may be converted into a repeated memory-pipeline stall before data-cache/interconnect admission, potentially amplified by access-queue ordering and repeated coalesced accesses.

This is a hypothesis, not yet an accepted root cause.

## 8. Next stage

Proceed to:

`AWMA_TRANSLATION_HITPATH_SEMANTIC_ATTRIBUTION_V1`

Goals:

1. prove the exact source-level blocking/overlap semantics;
2. measure where the 10-cycle service becomes critical-path stall;
3. explain T2 admission multiplicity change;
4. determine what semantic recalibration is required before mechanism evaluation.

Do not add new workloads unless this attribution stage proves they are necessary.
