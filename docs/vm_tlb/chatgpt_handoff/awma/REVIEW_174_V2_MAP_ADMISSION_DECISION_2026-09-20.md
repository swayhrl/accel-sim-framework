# ChatGPT Review — 174 V2 and T1/T2 Admission Decision

Date: 2026-09-20

Reviewed execution:

`hrl/awma-174-minimal-requalified-cross-target-hitpath-v2`

Remote HEAD:

`f34b53597ab7d9175f8286dde67f4313462aabb5`

Decision:

`AWMA_174_MINIMAL_REQUALIFIED_CROSS_TARGET_HITPATH_V2_ACCEPTED_WITH_SCOPE`

## 1. T0 requalification is accepted

All three T0 points have:

- natural terminal completion;
- 224 CTA;
- 368,696,302 instructions;
- 3,090,304 downstream admissions;
- 3,090,304 translated;
- zero untranslated;
- zero unobserved.

Cycles:

```text
10/80 = 1,654,548
0/80  =   711,464
0/0   =   745,880
I0 accepted external reference = 674,179
```

The fresh 10/80 control exactly reproduces the accepted repaired isolated R0 authority.

## 2. T0 scientific interpretation

Natural 10/80:

```text
L1 accesses = 3,090,824
L1 hits     = 3,087,447
L1 misses   = 3,377
L1 hit rate = 99.890741%

L2 hits / L1 misses = 2,857 / 3,377 = 84.6017%
walk starts = 240
walk density = 0.07765 per 1K L1 lookups
```

Yet:

```text
10/80 -> 0/80 delta = 943,084 cycles
fraction of R0       = 56.9995%

R0 -> I0 gap         = 980,369 cycles
0/80 explains        = 96.1968% of that gap
```

Thus the repaired isolated Q05 model has a very large **modeled L1 lookup hit-path sensitivity** despite an approximately 99.89% L1-TLB hit rate.

This is a simulator-model observation, not a hardware TLB-latency claim.

## 3. 0/0 is non-monotonic and non-additive

`0/0 = 745,880` is 34,416 cycles slower than `0/80 = 711,464`.

At the same time:

- L2 misses increase 769 -> 801;
- requester MSHR-wait cycles increase 742,135 -> 814,160;
- total requester translation latency decreases.

Therefore removing L2 lookup service changes execution/order/state interactions.

The 0/0 point is useful as a non-additivity diagnostic but should not be treated as an additive estimate of L2 lookup latency.

For cross-target validity the primary metric should now be:

`10/80 -> 0/80`

not a larger latency sweep.

## 4. T1/T2 TARGET_NOT_ADMITTED is an input-contract issue

T1/T2 producer identity and raw address traces are accepted.

The missing item is:

`target-specific VM object-map / weight-segment-map binding`

This is not evidence that the traces themselves are invalid.

## 5. Historical map-contract observation

The original consumer wrapper requires both:

- `-gpgpu_vm_object_map`
- `-gpgpu_vm_weight_segment_map`

as hash-bound compatibility-view assets.

Historical Q05 current-model compatibility maps were extremely coarse:

```text
object map:
  entire modeled VA range -> KV_CACHE

segment map:
  entire modeled VA range -> WEIGHT
```

By contrast, older C11/M4C maps were derived from privileged runtime allocation metadata and contained real WEIGHT/KV ranges plus a modeled segment registration.

Therefore "a map file exists" and "exact target object semantics are known" are not equivalent.

## 6. Next decision: audit map functional semantics before recapture

Before asking node109 to recapture T1/T2, determine from the exact repaired F0 runtime/source:

1. Is Weight Segment enabled or disabled in the effective repaired runtime?
2. Does object class affect:
   - virtual-to-physical functional mapping;
   - TLB/PTW lookup/fill/replacement;
   - memory scheduling;
   - or only object-labelled telemetry / Segment eligibility?
3. When Segment is disabled, is the segment-map asset consumed functionally or only required by the wrapper contract?
4. Can a target-local neutral compatibility map be created without fabricating runtime allocation metadata?

Do not infer these from configuration filenames. Prove them from effective config + loaded source.

## 7. Neutral-map path if and only if source audit permits it

If source audit proves that, under the accepted repaired F0 configuration:

- Segment is disabled;
- object class does not alter functional translation/cache/memory behavior;
- segment-map contents do not alter functional behavior;

then a neutral compatibility map may be created for T1/T2.

It must be explicitly labelled:

`FUNCTIONALLY_NEUTRAL_COMPATIBILITY_VIEW`

It must not claim real WEIGHT/KV attribution.

It must bind to the exact T1/T2 producer/input identity.

## 8. Mandatory T0 neutral-map equivalence gate

Before using any neutral map on T1/T2, run one T0 10/80 control with the proposed neutral compatibility map.

Compare to accepted T0 10/80:

`1,654,548 cycles`

Require exact equality for:

- cycles;
- instructions;
- CTA;
- coverage;
- total L1/L2 TLB counts;
- walks/PWC/PTE;
- total non-object-labelled translation counters.

Object-labelled telemetry is excluded from equality if the map intentionally changes only labels.

If this gate fails, neutral-map admission is rejected.

## 9. T1/T2 minimal cross-target science

If neutral-map gate passes, T1/T2 require only:

```text
10/80
0/80
```

Do not run 0/0 by default.

Reason:

- mainline question is L1 hit-path sensitivity;
- T0 already establishes 0/0 non-additivity;
- extra L2-zero points add cost and confounding without answering the primary cross-target question.

## 10. Fallback if maps are functionally required

If source audit proves that exact target allocation/segment metadata affects functional behavior, STOP before simulation.

Return:

`TARGET_SPECIFIC_VM_METADATA_REQUIRED`

with the exact missing metadata contract.

Only then should ChatGPT authorize a new node109 capture.

No automatic recapture is authorized by this review.
