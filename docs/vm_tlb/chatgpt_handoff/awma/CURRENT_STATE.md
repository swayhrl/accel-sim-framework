# AWMA Current State

Date: 2026-09-20

Status:

`109_NATIVE_TRACK_COMPLETE_174_MAP_ADMISSION_AUDIT_READY`

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

> Is the large repaired translation hit-path sensitivity a robust property across representative AI kernel families, or is it specific to Q05 / current simulator timing semantics?

This must be answered before any TLB/PTW mechanism design.

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

The new active 174 stage is:

`AWMA_174_VM_MAP_SEMANTICS_AND_CROSS_TARGET_ADMISSION_V3`

## 6. Mainline schedule

109 Native Cross-view is complete and accepted with scope.

Current schedule:

```text
109:
  COMPLETE_WITH_SCOPE
  remain GPU-idle; do not resume MoE/AWQ side lanes

174:
  audit exact VM map functional semantics
  -> decide whether a neutral compatibility view is source-safe
  -> T0 neutral-map 10/80 equivalence gate
  -> if PASS: T1/T2 10/80 + 0/80 only
  -> if map metadata is functionally required: STOP and request exact metadata
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

## 9. 174 Simulation mainline — MAP ADMISSION AUDIT READY

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

Next stage:

`AWMA_174_VM_MAP_SEMANTICS_AND_CROSS_TARGET_ADMISSION_V3`

Primary metric after admission:

`10/80 -> 0/80`

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

## 11. Decision gate

After both tracks close, classify:

```text
HITPATH_SENSITIVITY_SYSTEMATIC_ACROSS_KERNEL_CLASSES
HITPATH_SENSITIVITY_ATTENTION_DOMINANT
HITPATH_SENSITIVITY_TARGET_DEPENDENT
SIMULATOR_HITPATH_MODEL_REQUIRES_SEMANTIC_RECALIBRATION
INSUFFICIENT_CROSS_TARGET_EVIDENCE
```

Only after this may a TLB/PTW mechanism stage be considered.

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
  CODEX_NEXT_STAGE_174_VM_MAP_SEMANTICS_CROSS_TARGET_V3.md

AFTER 174 SCIENTIFIC TRACK:
  STOP -> ChatGPT Cross-view review
```

No architecture mechanism is authorized.
