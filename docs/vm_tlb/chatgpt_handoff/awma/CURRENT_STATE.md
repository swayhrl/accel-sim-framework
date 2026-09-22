# AWMA Current State

Date: 2026-09-20

Status:

`HITPATH_ATTRIBUTION_CLOSED_FRONTEND_RECALIBRATION_BUILD_RECOVERY`

## 1. Project mission

AWMA remains **AI Workload Memory Analysis**.

The mainline scientific sequence is:

```text
broad Native workload evidence
        ->
question-driven representative target selection
        ->
qualified Simulation on a small subset
        ->
Native/Simulation Cross-view
        ->
model-validity decision
        ->
only then architecture mechanism
```

Native coverage is intentionally broader than Simulation coverage.

A strong side-lane result does not automatically become the AWMA mainline.

## 2. Frozen mainline workload

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT
batch      = 1
prefill    = 2048
decode     = 32
dtype      = FP16
backend    = SDPA
```

## 3. Current mainline question

Cross-target validity is now closed.

Accepted classification:

`HITPATH_SENSITIVITY_SYSTEMATIC_ACROSS_KERNEL_CLASSES`

Mainline consequence:

`SIMULATOR_HITPATH_MODEL_REQUIRES_SEMANTIC_RECALIBRATION_BEFORE_MECHANISM`

The active question is now:

> Which exact simulator hit-path semantics convert a 10-cycle L1 translation lookup into a 53-60% total-cycle effect, and what must be recalibrated before mechanism evaluation?

## 4. Q05 repaired-model anchor

Repair authority:

`3f7bc0cd3cb3667b38fa0dd803ac034e19b493d6`

Repaired requalification authority:

`a7110f789a2bc6761d8885a2ca5628b4acf50f69`

Accepted repaired Q05/P34 anchor:

```text
P34 repaired natural 10/80 = 1,619,068 cycles
target admissions           = 3,090,304
translated                  = 3,090,304
untranslated                = 0
unobserved                  = 0
```

These are simulator-model results, not RTX4080 hardware-latency claims.

## 5. P0 gate status

### 109 — CLOSED

Verified pause branch:

`hrl/awma-109-moe-causal-closure-scale-20h-v1`

Remote HEAD:

`0e32ac01b0237d94b39e45b288263e87e1960ccf`

The remote pause commit contains:

- `PAUSED_STATE.json`;
- frozen 10-block x 22-condition C2 schedule;
- degree-realization authority;
- admitted-condition index;
- SHA256SUMS.

107 completed C2 conditions are retained as candidate evidence.

The MoE campaign status is:

`PAUSED_FOR_AWMA_MAINLINE`

109 GPU/lock is released.

Therefore:

`109_MAINLINE_RELEASED`

### 174 — STORAGE RECOVERED; SCIENTIFIC REQUALIFICATION REQUIRED

node164 access is restored and the immutable V4 durable root is readable.

Independent review commit:

`46de0c35e2c26fdabd9fc691370bedf0cc5974f5`

establishes that the V4 repaired 10/80 qualification is complete, but all six historical lookup-matrix launches lack terminal and per-access coverage markers.

Therefore the six historical lookup points are:

`V4_LOOKUP_MATRIX_PARTIAL_NOT_ADMITTED`

and the old full-matrix publication path is:

`V4_FULL_MATRIX_PUBLICATION_SUPERSEDED`

The accepted repaired runtime, isolated R0/I0 authority, contextual repaired R0/I0 anchors, and V4 runtime-load forensic qualification remain valid.

The V2 minimal requalification has now completed and is accepted with scope:

`hrl/awma-174-minimal-requalified-cross-target-hitpath-v2 @ f34b53597ab7d9175f8286dde67f4313462aabb5`

T0 isolated repaired 10/80 exactly reproduced the accepted authority; 0/80 and 0/0 both completed with full per-access coverage.

T1/T2 were not admitted because their producer bundles do not contain target-specific VM map bindings.

The V3 source/config audit has completed and is remote-published:

`hrl/awma-174-vm-map-semantics-cross-target-v3 @ b3310731956d0f731da47bb324cc22d661002dfc`

V3 correctly proved Segment descriptors are functionally capable, but its final `TARGET_SPECIFIC_VM_METADATA_REQUIRED` conclusion is not yet admitted because it did not close the post-parse F0 runtime state.

Existing accepted repaired F0 telemetry shows `vm_weight_segmentation_enabled=0` and zero Segment lookup/hit/suppression activity despite a loaded descriptor path.

V3R1 is complete and accepted:

`hrl/awma-174-exact-f0-segment-state-v3r1 @ 7a4f2a419fe77c017cb9a9a5555b1551a2fc884c`

It proves:

`F0_SEGMENT_FUNCTIONALLY_DORMANT_CONFIRMED`

and closes T1/T2 10/80 + 0/80 with terminal/full-coverage/zero-Segment activity.

The hit-path attribution stage is complete and accepted:

`hrl/awma-174-hitpath-semantic-attribution-v1 @ f79aaa1d22d2a22912e8b71dc832bdbf31a899f7`

Accepted attribution:

`MIXED_MODEL_EFFECT`

with source-supported dominant components:

- `SERIALIZED_PRE_ADMISSION_LOOKUP_WAIT_DOMINANT`
- `ACCESSQ_HEAD_OF_LINE_TRANSLATION_BLOCKING_DOMINANT`
- `ZERO_LATENCY_RETRY_ORDERING_NONLINEARITY`

The new active 174 stage is:

`AWMA_TRANSLATION_FRONTEND_PIPELINING_RECALIBRATION_V1`

## 6. Mainline schedule

109 Native Cross-view is complete and accepted with scope.

Current schedule:

```text
109:
  COMPLETE_WITH_SCOPE
  remain GPU-idle; do not resume MoE/AWQ side lanes

174:
  recover clean candidate-private top-level build using accepted CUDA 12.4.131 toolchain
  -> repair coverage telemetry semantics without timing changes
  -> implement/compile opt-in diagnostic pipelined accessq translation launch
  -> directed latency/throughput separation tests
  -> run T0/T1/T2 candidate 10/80 + 0/80 with maximal safe parallelism
  -> compare residual hit-path sensitivity
  -> STOP before promoting candidate to baseline
```

Cross-view synthesis waits only for this 174 scientific track.

## 7. Frozen target set

### T0 — Attention anchor

`Q05_PREFILL_ATTN_FLASH`

### T1 — Prefill GEMM

`PREFILL_GEMM_PRIMARY_OCC0`

Producer authority:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

Frozen producer descriptors:

- raw records: 12,043,648
- memory instruction records: 2,298,240
- effective lane addresses: 70,352,896
- 4 KiB pages: 7,906
- 64 KiB pages: 495

### T2 — Decode GEMV

`DECODE_GEMV_PRIMARY_STEP16`

Same producer authority.

Frozen descriptors:

- raw records: 1,515,136
- memory instruction records: 318,592
- effective lane addresses: 9,022,720
- 4 KiB pages: 2,132
- 64 KiB pages: 135

No result-driven target substitution.

## 8. 109 Native mainline — COMPLETE_WITH_SCOPE

Execution branch:

`hrl/awma-109-exact-target-native-crossview-v1`

Remote HEAD:

`2122eccc7aed61d05b114075e1c3126c4308e64b`

Accepted status:

`AWMA_109_EXACT_TARGET_NATIVE_CROSSVIEW_V1_ACCEPTED_WITH_SCOPE`

Accepted T0/T1/T2 exact-target identity export is remote-bound.

T1/T2 Route-B footprint descriptors are complete for the current join.

Compact exact-target native timing is explicitly unavailable for T0/T1/T2, and exact NCU selector/resource evidence is unavailable for T1/T2. These missing fields are not backfilled from another evidence class.

T0 comparable Native footprint fields also remain unavailable in this export; existing Q05 simulator-native trace structure must not be silently imported into the Native evidence plane.

No further 109 GPU work is required for the current mainline decision.

MoE/AWQ side lanes remain frozen.

## 9. 174 Simulation mainline — CROSS-TARGET VALIDITY CLOSED

Accepted V2:

`f34b53597ab7d9175f8286dde67f4313462aabb5`

Accepted T0:

```text
10/80 = 1,654,548
0/80  =   711,464
0/0   =   745,880
I0    =   674,179 external accepted reference
```

T0 has ~99.8907% L1-TLB hit rate, yet 10/80 -> 0/80 removes 56.9995% of R0 cycles and explains 96.1968% of the R0->I0 gap.

0/0 is 34,416 cycles slower than 0/80, so L2-zero behavior is non-additive and will not be used as the primary cross-target metric.

T1/T2 remain `TARGET_NOT_ADMITTED` only because the consumer contract lacks target-specific VM object/segment map bindings.

V3 review:

`b3310731956d0f731da47bb324cc22d661002dfc`

Important correction: V3 read parsed/effective `weight_segmentation_enable=1`, but historical fair-arm F0 semantics disable Segment after parsing. Accepted repaired F0 telemetry already reports Segment disabled and zero Segment lookup/hit/suppression counters.

Exact V2 compatibility assets are whole-VA views rather than target-precise allocation maps. Therefore no node109 recapture is authorized until exact V2 T0 runtime Segment participation is checked from immutable logs.

Accepted V3R1:

`7a4f2a419fe77c017cb9a9a5555b1551a2fc884c`

Cross-target result:

```text
T0 FlashAttention: 56.9995% reduction
T1 Prefill GEMM:   59.7989% reduction
T2 Decode GEMV:    53.0990% reduction
```

All three have L1-TLB hit rates above 99.7% and sparse walk activity.

T2 has a nonlinear downstream-admission effect and is retained with that caveat; T0/T1 are the clean anchors.

Accepted attribution:

`f79aaa1d22d2a22912e8b71dc832bdbf31a899f7`

Source confirms `accessq_back()`-only translation/admission, non-READY `COAL_STALL`, and positive-latency pre-admission head-of-line blocking.

T2's extra 65,899 historical `admissions` are repeated admission attempts with unchanged unique logical UIDs, not new accesses.

Next stage:

`AWMA_TRANSLATION_FRONTEND_PIPELINING_RECALIBRATION_V1`

## 10. Cross-view objective

Join T0/T1/T2 using:

`EXACT_WORKLOAD_TARGET`

and compare only aligned descriptors:

- operator family;
- CTA/warp shape;
- memory-reference density;
- native page footprint;
- native traffic/resource regime;
- simulated translation request density;
- simulated TLB hit/miss/walk behavior;
- simulated L1 lookup sensitivity.

Do not equate native CUDA time with simulator cycles, or NCU cache controls with TLB state.

## 11. Decision gate — CLOSED

Accepted:

`HITPATH_SENSITIVITY_SYSTEMATIC_ACROSS_KERNEL_CLASSES`

Before any TLB/PTW mechanism stage:

`SIMULATOR_HITPATH_MODEL_REQUIRES_SEMANTIC_RECALIBRATION_BEFORE_MECHANISM`

## 12. Candidate side lanes

### Q30 MoE routing-skew

Accepted anchor:

`ed645f3aec0fe4623e1895dee2754ece0ab063f1`

Paused continuation:

`0e32ac01b0237d94b39e45b288263e87e1960ccf`

Status:

`HIGH_VALUE_RESEARCH_CANDIDATE / SIDE_LANE_FROZEN`

### Raw/AWQ implementation policy

Accepted evidence includes shape transition, same-weight A/B/C decomposition, and isolated NCU evidence.

Status:

`HIGH_VALUE_RESEARCH_CANDIDATE / SIDE_LANE_FROZEN`

No side lane may consume mainline resources without explicit reactivation.

## 13. Immediate execution

```text
109 NOW:
  no new GPU task; hold accepted Native result at 2122eccc...

174 NOW:
  CODEX_CONTINUE_174_TRANSLATION_FRONTEND_CLEAN_BUILD_RECOVERY_V1.md

AFTER 174 SCIENTIFIC TRACK:
  STOP -> ChatGPT Cross-view review
```

No architecture mechanism is authorized.
