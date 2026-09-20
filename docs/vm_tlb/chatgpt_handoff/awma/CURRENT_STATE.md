# AWMA Current State

Date: 2026-09-20

Status:

`ASYMMETRIC_MAINLINE_RELEASE`

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

### 174 — BLOCKED ON STORAGE

Independent GitHub verification shows:

`hrl/awma-174-hitpath-v4-provenance-closeout-exec`

still points to:

`c8657cf637c5b54a0f40135248ff1eabcfd66696`

and the remote commit tree does not contain the reconstructed V4 final report/matrix/envelope/receipts.

The publication reconstruction is now blocked because:

```text
/root/share/mnt164/huangrulin
-> Transport endpoint is not connected

10.208.130.164
-> network reachable

direct SSH
-> no usable credential / authentication rejected
```

No local reachable Git commit contains the complete reconstructed closure tree.

Therefore:

`174_MAINLINE_BLOCKED_ON_NODE164_STORAGE_RECOVERY`

No new 174 simulation may start.

The active 174 task is now infrastructure-only:

`AWMA_174_NODE164_MOUNT_RECOVERY_V1`

followed by:

`AWMA_174_V4_REMOTE_PUBLICATION_REPAIR_V2`

## 6. Asymmetric mainline release

The 109 Native track does NOT scientifically depend on the missing 174 publication files.

Therefore node109 must not remain idle merely because 174 storage is blocked.

Current parallel schedule:

```text
109:
  start AWMA_109_EXACT_TARGET_NATIVE_CROSSVIEW_V1 now

174:
  recover /root/share/mnt164
  -> recover immutable V4 closure evidence
  -> publish V4 closeout correctly
  -> only then start Simulation cross-target stage
```

Cross-view synthesis still waits for both scientific tracks.

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

## 8. 109 Native mainline

Stage:

`AWMA_109_EXACT_TARGET_NATIVE_CROSSVIEW_V1`

Goal:

for T0/T1/T2, reuse existing evidence first and close only missing:

- exact target identity;
- native timing;
- Route-B footprint;
- bounded exact-selector NCU traffic/resource evidence;
- implementation fingerprint.

No MoE/AWQ continuation.

## 9. 174 Simulation mainline — pending storage recovery

Stage:

`AWMA_174_CROSS_TARGET_REPAIRED_HITPATH_VALIDITY_V1`

May start ONLY after:

1. node164 immutable V4 closure is readable;
2. V4 publication V2 is remotely closed;
3. remote commit tree contains the required report/matrix/envelope/receipts.

Then T1/T2 receive minimal repaired hit-path screens.

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
  CODEX_NEXT_STAGE_109_EXACT_TARGET_NATIVE_CROSSVIEW_V1.md

174 NOW:
  CODEX_RECOVER_174_NODE164_MOUNT_V1.md

174 AFTER MOUNT PASS:
  CODEX_REPAIR_174_V4_REMOTE_PUBLICATION_V2.md

174 AFTER PUBLICATION PASS:
  CODEX_NEXT_STAGE_174_CROSS_TARGET_HITPATH_VALIDITY_V1.md

AFTER BOTH SCIENTIFIC TRACKS:
  STOP -> ChatGPT Cross-view review
```

No architecture mechanism is authorized.
