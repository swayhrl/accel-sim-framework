# AWMA Current State

Date: 2026-09-20

Status:

`MAINLINE_RESET_TO_CROSS_TARGET_VALIDATION_AND_CROSSVIEW`

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

Primary workload identity:

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

## 3. Current mainline scientific question

The next mainline question is no longer:

> can Q05 show translation sensitivity?

That has been established inside the accepted simulator model.

The current question is:

> Is the large repaired translation hit-path sensitivity a robust property across representative AI kernel families, or is it specific to Q05 / the current simulator timing semantics?

This must be answered before any TLB/PTW mechanism design.

## 4. Q05 repaired-model status

The accepted repaired per-access contract requires every VM-eligible downstream admission to have completed translation.

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

The repaired Q05 model exhibits:

- very high L1-TLB hit rate;
- very few actual walks under contextual P34;
- large R0 -> I0 sensitivity;
- strong sensitivity to modeled L1 lookup service latency.

These are **simulator-model results**, not RTX4080 hardware latency claims.

## 5. 174 V4 status

Execution branch:

`hrl/awma-174-runtime-load-forensics-hitpath-v4`

Remote execution HEAD:

`c8657cf637c5b54a0f40135248ff1eabcfd66696`

The runtime-load issue was solved and the repaired core was qualified.

The user reports that all six repaired lookup points and zero-science provenance reconstruction have completed.

However, as of this coordination update, the remote publication ref:

`hrl/awma-174-hitpath-v4-provenance-closeout-exec`

still resolves to the old execution HEAD `c8657cf...` rather than a new commit containing the reconstructed matrix/envelope closure.

Therefore current status is:

`SCIENCE_EXECUTED / REMOTE_PUBLICATION_BLOCKING_CLOSEOUT`

No simulation rerun is authorized for this publication gap.

The permanent 174 publication rule is:

`docs/vm_tlb/chatgpt_handoff/awma/174_MANDATORY_REMOTE_PUBLICATION_CONTRACT.md`

## 6. Next representative target set

The next Simulation subset is intentionally small and question-driven.

### T0 — Attention anchor

`Q05_PREFILL_ATTN_FLASH`

Existing repaired/contextual anchor.

### T1 — Prefill GEMM

`PREFILL_GEMM_PRIMARY_OCC0`

Accepted producer bundle under producer authority:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

Reported producer properties include:

- raw records: 12,043,648
- memory instruction records: 2,298,240
- effective lane addresses: 70,352,896
- 64 KiB VM-entry pages: 495

No recapture is authorized by default.

### T2 — Decode GEMV

`DECODE_GEMV_PRIMARY_STEP16`

Same accepted producer authority:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

Reported producer properties include:

- raw records: 1,515,136
- memory instruction records: 318,592
- effective lane addresses: 9,022,720
- 64 KiB VM-entry pages: 135

Step16 is selected before new simulation as a middle decode step from the already accepted stable primary GEMV family.

No result-driven target substitution is allowed.

## 7. New mainline stage

Stage:

`AWMA_CROSS_TARGET_HITPATH_VALIDITY_AND_NATIVE_CROSSVIEW_V1`

Two tracks execute in parallel only after prerequisites close.

### Track A — 174-new

Role:

`Simulation Evidence Plane`

Goal:

- reuse repaired runtime;
- admit T1/T2 exact simulator inputs;
- run a minimal hit-path validity matrix;
- compare target classes without designing a mechanism.

Minimum per new target:

```text
repaired natural 10/80
target-only 0/80
target-only 0/0 when admitted safely
target-I0 only if the exact existing diagnostic contract transfers cleanly
```

Classification:

`REPAIRED_ISOLATED_SCREEN`

unless same-run predecessor context is separately available and qualified.

### Track B — 109 / RTX4080

Role:

`Native Evidence Plane`

Goal:

For exact T0/T1/T2 targets, reuse existing evidence first and add only bounded missing native evidence:

- exact kernel identity / occurrence / decode step;
- native CUDA timing;
- lightweight NCU resource/traffic evidence where exact selector is proven;
- accepted Route-B page/line/memory-record footprint;
- CTA/warp/kernel shape;
- implementation fingerprint.

No new broad NVBit or SASS trace campaign.

## 8. Cross-view objective

Create one aligned table with relation:

`EXACT_WORKLOAD_TARGET`

for T0/T1/T2.

Valid comparisons include:

- target identity;
- phase/operator family;
- CTA/warp shape;
- memory-reference density;
- native page footprint;
- native traffic/resource regime;
- simulated translation request density;
- simulated TLB hit/miss/walk behavior;
- simulated sensitivity to L1 lookup timing.

Do NOT directly equate:

- NCU cache controls with TLB flush;
- native wall/CUDA timing with simulator cycles;
- native L2 counter definitions with simulator L2 counters unless definitions are explicitly aligned.

## 9. Decision gate after dual-track stage

The mainline must classify the repaired simulator behavior into one of:

```text
HITPATH_SENSITIVITY_SYSTEMATIC_ACROSS_KERNEL_CLASSES
HITPATH_SENSITIVITY_ATTENTION_DOMINANT
HITPATH_SENSITIVITY_TARGET_DEPENDENT
SIMULATOR_HITPATH_MODEL_REQUIRES_SEMANTIC_RECALIBRATION
INSUFFICIENT_CROSS_TARGET_EVIDENCE
```

Only after this decision may a TLB/PTW mechanism stage be proposed.

## 10. Candidate side lanes

### MoE routing-skew candidate

Accepted anchor:

`hrl/awma-109-moe-routing-skew-20h-v1 @ ed645f3aec0fe4623e1895dee2754ece0ab063f1`

Status:

`HIGH_VALUE_RESEARCH_CANDIDATE / SIDE_LANE_FROZEN`

The subsequently launched MoE causal-closure campaign is now:

`PAUSE_REQUESTED_FOR_MAINLINE_PREEMPTION`

Any already-completed C2 condition/block is retained as partial evidence.

It must not continue consuming the RTX4080 after the smallest safe checkpoint.

### Raw/AWQ implementation candidate

Accepted evidence includes:

- shape-specific replay/oracle correction;
- M1023/M1024 implementation transition;
- A/B/C same-weight decomposition;
- isolated NCU evidence.

Status:

`HIGH_VALUE_RESEARCH_CANDIDATE / SIDE_LANE_FROZEN`

No additional AWQ work is currently mainline.

## 11. Node priority

### 174-new

1. close remote publication of V4;
2. Track A cross-target repaired hit-path validation;
3. Cross-view analysis support;
4. no new mechanism until review.

### 109 / RTX4080

1. pause MoE causal-closure at a clean checkpoint;
2. release GPU lock;
3. Track B exact-target native Cross-view;
4. side lanes remain frozen unless explicitly reactivated.

### node164

Durable raw/receipt authority.

## 12. Immediate order

```text
P0
  109: safely pause MoE causal-closure campaign
  174: finish V4 remote publication

P1
  174: T1 Prefill GEMM repaired hit-path screen
  109: T0/T1/T2 exact-target native evidence closure

P2
  174: T2 Decode GEMV repaired hit-path screen

P3
  Cross-view synthesis + ChatGPT scientific review

STOP before mechanism design
```

## 13. Global boundaries

Do not automatically start:

- TLB capacity sweep;
- walker/PTW mechanism;
- PWC mechanism;
- Segment/page-size mechanism;
- cache mechanism;
- MoE scheduling mechanism;
- AWQ kernel optimization;
- new model download.

Routine engineering problems remain solve-and-continue.

Scientific identity/semantics changes require review.
