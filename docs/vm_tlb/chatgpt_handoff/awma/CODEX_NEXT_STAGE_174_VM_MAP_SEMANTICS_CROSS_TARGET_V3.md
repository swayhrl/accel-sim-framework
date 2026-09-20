# CODEX NEXT STAGE — 174 VM Map Semantics Audit + Cross-Target Admission V3

Date: 2026-09-20

Mode:

`GOAL MODE / solve-and-continue / MAINLINE`

Node:

`174-new`

Stage:

`AWMA_174_VM_MAP_SEMANTICS_AND_CROSS_TARGET_ADMISSION_V3`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

Read first:

1. `CURRENT_STATE.md`
2. `REVIEW_174_V2_MAP_ADMISSION_DECISION_2026-09-20.md`
3. `CROSSVIEW_JOIN_CONTRACT_V1.md`
4. `174_MANDATORY_REMOTE_PUBLICATION_CONTRACT.md`
5. this Goal

Suggested execution branch:

`hrl/awma-174-vm-map-semantics-cross-target-v3`

## 0. Frozen accepted anchors

T0 V2:

`f34b53597ab7d9175f8286dde67f4313462aabb5`

Accepted T0:

```text
10/80 = 1,654,548
0/80  =   711,464
0/0   =   745,880
I0    =   674,179 external accepted reference
```

T1/T2 Native/producer authority:

`2122eccc7aed61d05b114075e1c3126c4308e64b`

`8f49ba3b9228b5f8a9163e961225ffd415107734`

No target substitution.

## 1. Phase A — exact effective-config audit

From the exact V2 repaired runtime, materialize and hash the effective configuration actually used for T0.

Record at minimum:

- `gpgpu_vm_mode`
- page size
- L1/L2 TLB geometry/latency
- `gpgpu_vm_weight_segmentation_enable`
- Segment entries/latency
- object-map path/SHA
- weight-segment-map path/SHA
- fair-arm setting
- all VM-related overrides

Create:

`EFFECTIVE_VM_CONFIG_AUDIT.tsv`

Do not infer effective values from historical base config text alone.

## 2. Phase B — source consumer audit

Using the exact loaded repaired core/source authority, trace all consumers of:

- `gpgpu_vm_object_map`
- `gpgpu_vm_weight_segment_map`
- object_class
- Segment registration/lookup
- object-labelled telemetry

Produce a compact call-path/semantic table:

`VM_MAP_SOURCE_SEMANTICS.tsv`

For each map field/classify whether it can affect:

```text
VA->PA functional mapping
TLB key
TLB hit/miss/fill/replacement
PTW/PWC/PTE
translation MSHR
memory request address
cache/memory scheduling
Segment eligibility/result
telemetry label only
```

Every classification needs source-location evidence.

## 3. Phase C — admission decision

Classify exactly one:

### C1
`NEUTRAL_COMPATIBILITY_VIEW_SOURCE_SAFE`

Requires proof that under accepted repaired F0:

- Segment functional path is disabled;
- map contents do not affect normal functional translation/cache/memory behavior;
- object map differences affect only labels/disabled Segment path.

### C2
`TARGET_SPECIFIC_VM_METADATA_REQUIRED`

If any required map information changes functional simulation semantics.

### C3
`SOURCE_SEMANTICS_AMBIGUOUS_STOP`

If source/runtime evidence is insufficient.

C2/C3 -> STOP science and publish audit. Do not recapture automatically.

## 4. Phase D — construct neutral target-local compatibility maps

Only for C1.

Construct T0/T1/T2 target-local assets using a schema accepted by the current runtime.

Requirements:

- bind map receipt to exact target producer/input hash;
- do not claim real WEIGHT/KV ranges;
- label `FUNCTIONALLY_NEUTRAL_COMPATIBILITY_VIEW`;
- no fabricated runtime-allocation sidecar SHA;
- if schema requires an unavailable sidecar field that cannot truthfully be replaced, classify C2 and STOP.

Record:

`NEUTRAL_MAP_AUTHORITY.json`

## 5. Phase E — T0 functional-equivalence gate

Run only:

`T0_NEUTRAL_MAP_10_80`

Same repaired runtime and exact T0 input.

Expected accepted authority:

`1,654,548 cycles`

Require exact equality against V2 T0 10/80 for:

- cycles;
- instructions = 368,696,302;
- CTA = 224;
- admissions = 3,090,304;
- translated = 3,090,304;
- untranslated/unobserved = 0;
- total L1 accesses/hits/misses;
- total L2 accesses/hits/misses;
- walk starts;
- PWC totals;
- PTE totals;
- requester total latency and MSHR wait if object-label-independent.

Object-class-labelled counters may differ only if the source audit explicitly classifies them telemetry-only.

If any functional metric differs:

`NEUTRAL_MAP_FUNCTIONAL_EQUIVALENCE_FAIL`

STOP before T1/T2.

If exact gate passes:

`NEUTRAL_MAP_FUNCTIONAL_EQUIVALENCE_PASS`

## 6. Phase F — T1/T2 simulator input admission

Only after Phase E PASS.

For T1 and T2:

- validate exact producer bundle;
- validate trace grammar/terminal receipt;
- build target-specific SIM_INPUT identity;
- bind target-local neutral compatibility maps;
- record explicit evidence-class label.

No recapture.

Create:

`T1_T2_SIM_INPUT_ADMISSION.tsv`

## 7. Phase G — minimal cross-target hit-path test

For each admitted T1/T2 run only:

### R0
`10/80`

### L1-zero
`0/80`

Do NOT run 0/0 unless explicitly required by a new scientific failure.

Every point must have:

- natural terminal completion;
- exact target identity;
- complete CTA/instruction completion;
- full per-access coverage;
- translated == downstream admissions;
- untranslated = 0;
- unobserved = 0.

## 8. Metrics

For T1/T2 report:

- cycles;
- admissions;
- L1 hits/misses/rate;
- L2 hits/misses;
- walks;
- PWC/PTE;
- requester latency/MSHR wait;
- `L1_ZERO_DELTA_CYCLES`;
- `L1_ZERO_DELTA_FRAC_R0`;
- lookup density relative to accepted Native memory-instruction/lane-address descriptors.

Join with T0:

```text
T0 L1_ZERO_DELTA_FRAC_R0 = 0.569994947261
```

## 9. Scientific decision

If T1/T2 complete, classify:

- `HITPATH_SENSITIVITY_SYSTEMATIC_ACROSS_KERNEL_CLASSES`
- `HITPATH_SENSITIVITY_ATTENTION_DOMINANT`
- `HITPATH_SENSITIVITY_TARGET_DEPENDENT`
- `SIMULATOR_HITPATH_MODEL_REQUIRES_SEMANTIC_RECALIBRATION`

If one/both cannot be admitted:

`INSUFFICIENT_CROSS_TARGET_EVIDENCE`

Do not start a mechanism.

## 10. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/VM_MAP_SEMANTICS_CROSS_TARGET_174NEW_V3_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_174_VM_MAP_SEMANTICS_CROSS_TARGET_V3/`

Required:

```text
README.md
SOURCE_ANCHORS.md
EFFECTIVE_VM_CONFIG_AUDIT.tsv
VM_MAP_SOURCE_SEMANTICS.tsv
MAP_ADMISSION_DECISION.md
NEUTRAL_MAP_AUTHORITY.json
T0_NEUTRAL_MAP_EQUIVALENCE.tsv
T1_T2_SIM_INPUT_ADMISSION.tsv
CROSS_TARGET_L1_HITPATH.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

For C2/C3 stop paths, files that depend on later phases may contain explicit NOT_RUN status rather than fabricated values.

## 11. Remote publication

Apply mandatory 174 publication contract.

Before final status:

- node164 closure;
- commit/push;
- git ls-remote/fetch verify;
- remote HEAD == local HEAD;
- remote tree verification;
- SHA256SUMS PASS;
- worktree clean.

Then STOP.
