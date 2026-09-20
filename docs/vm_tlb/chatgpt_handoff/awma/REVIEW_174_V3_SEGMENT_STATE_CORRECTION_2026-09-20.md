# ChatGPT Review — V3 Segment-State Correction

Date: 2026-09-20

Reviewed V3:

`hrl/awma-174-vm-map-semantics-cross-target-v3 @ b3310731956d0f731da47bb324cc22d661002dfc`

V3 publication/audit integrity is accepted, but its final admission conclusion is **not yet accepted as the mainline decision**.

Status:

`V3_SOURCE_AUDIT_ACCEPTED / TARGET_SPECIFIC_VM_METADATA_REQUIRED_NOT_YET_ADMITTED`

## 1. What V3 proved correctly

V3 correctly proves:

- the parsed effective config contains `gpgpu_vm_weight_segmentation_enable=1`;
- a Segment descriptor, when active, can return a functional PPN/source;
- object_class itself is telemetry-only and is not a translation key/timing input;
- fabricating an active Segment descriptor would be scientifically invalid.

These findings remain accepted.

## 2. Missing runtime-state step

V3 inspected the parsed/effective config and source capability, but did not close the post-parse fair-arm runtime state actually used by accepted F0.

This matters because historical C11 tooling explicitly states:

> F0/F1/F2/F5/F9 Segment-disabled after parsing while retaining a legal V2 map path.

Therefore:

`parsed enable=1`

does not by itself prove:

`runtime Segment active=1`.

## 3. Existing repaired F0 evidence

Accepted repaired requalification:

`a7110f789a2bc6761d8885a2ca5628b4acf50f69`

contains target-boundary telemetry for repaired P34 F0 showing:

```text
vm_weight_segmentation_enabled              0
vm_weight_segment_lookup_attempts           0
vm_weight_segment_lookup_launches           0
vm_weight_segment_lookup_completions        0
vm_weight_segment_hits                      0
vm_weight_segment_misses                    0
vm_weight_segment_l1_fills_suppressed       0
vm_weight_segment_l2_suppressed             0
vm_weight_segment_mshr_suppressed           0
vm_weight_segment_pwq_suppressed            0
vm_weight_segment_walker_suppressed         0
vm_weight_segment_pwc_suppressed            0
vm_weight_segment_pte_suppressed            0
```

The same table shows a descriptor may be loaded while functional Segment remains disabled.

This is evidence that map presence is not equivalent to active Segment translation in F0.

## 4. Q05 compatibility-map identity

The exact V2 map SHA values from V3 are:

```text
object-map SHA256  = 689af1cfe35897fb17e741cd9699a20dafaf3e529d7d7603447d6381066bfc99
segment-map SHA256 = 765d9793d0922e12f6c02d4a042c14eca3b35197ed48f246af3fb2187e66047c
```

They correspond exactly to the historical Q05 compatibility views:

```text
object map:
  range KV_CACHE 0x0 .. 0x1ffffffffffff

segment map:
  segment WEIGHT 0x0 .. 0x1ffffffffffff
```

These are whole-VA compatibility views, not precise target runtime-allocation maps.

Therefore V2 T0 itself is not using a target-precise WEIGHT/KV map.

## 5. Correct next question

Before any node109 recapture:

> In the exact accepted V2 isolated T0 F0 runtime, after all fair-arm post-parse selection, was Segment functionally disabled and were Segment lookup/hit/suppression counters exactly zero?

This can be answered from existing immutable T0 logs/source. No simulation is required.

## 6. Decision branches

### A — exact V2 T0 confirms Segment disabled / zero participation

Classify:

`F0_SEGMENT_FUNCTIONALLY_DORMANT_CONFIRMED`

Then T1/T2 do **not** require real target Segment metadata for the current F0 hit-path-validity question.

The existing Q05 object/segment assets may be reclassified as:

`MODEL_GENERIC_DORMANT_F0_COMPATIBILITY_ASSETS`

provided:

- exact same asset SHA is used across T0/T1/T2;
- no claim is made that they describe real T1/T2 WEIGHT/KV allocation;
- object-labelled telemetry is excluded from cross-target claims;
- Segment counters remain zero for T1/T2;
- any nonzero Segment attempt/hit is a hard admission failure.

This preserves the exact T0 modeled runtime semantics rather than introducing a new allocation model.

### B — exact V2 T0 shows any Segment participation

Then V3 conclusion stands:

`TARGET_SPECIFIC_VM_METADATA_REQUIRED`

Only in branch B should node109 be asked for new same-run metadata/trace capture.

## 7. PA boundary correction

Even in branch B, the future producer is **not required to measure hardware GPU PPN**.

Historical accepted C11 authority explicitly states capture did not contain hardware PPN/page-map and used:

`C5_MODELED_PA_HIGH_UNUSED_BIT_V1`

to derive SimPA/SimPPN from runtime SimVA.

Therefore the required producer-side evidence is runtime allocation metadata:

- exact run-bound SimVA extent(s);
- object identity/classification provenance;
- lifetime;
- target/workload identity;
- permissions when semantically known;
- ASID/epoch contract as defined by the simulator input pipeline.

SimPA/SimPPN remains a documented simulator modeling decision unless a future stage explicitly changes that contract.

Do not request or claim measured hardware PA without a new scientific contract.

## 8. V3 node164 audit-copy closeout

The only outstanding V3 publication item is a hash-only engineering closeout.

When 174 connectivity returns, run:

`sha256sum -c SHA256SUMS`

inside the already-copied node164 V3 audit directory.

No science rerun is authorized for this closeout.
