# CODEX NEXT STAGE — 174 Exact F0 Segment-State Closure V3R1

Date: 2026-09-20

Mode:

`GOAL MODE / ZERO-SCIENCE AUDIT FIRST / solve-and-continue`

Node:

`174-new`

Stage:

`AWMA_174_EXACT_F0_SEGMENT_STATE_CLOSURE_V3R1`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

Read first:

1. `CURRENT_STATE.md`
2. `REVIEW_174_V3_SEGMENT_STATE_CORRECTION_2026-09-20.md`
3. V3 review pack at `b3310731956d0f731da47bb324cc22d661002dfc`
4. V2 review pack at `f34b53597ab7d9175f8286dde67f4313462aabb5`
5. this Goal

Suggested execution branch:

`hrl/awma-174-exact-f0-segment-state-v3r1`

## 0. Finish V3 hash-only engineering closeout

If the node164 audit-copy already exists, run only:

```bash
cd <existing-V3-node164-audit-directory>
sha256sum -c SHA256SUMS
```

Record PASS/FAIL.

Do not recopies/recompute scientific files unless the directory is actually missing.

This is not a science gate for the new audit.

## 1. No new simulation in Phase A

Do not run simulator yet.

Do not ask node109 to recapture.

Do not generate target metadata.

## 2. Exact V2 T0 runtime-state audit

Use immutable V2 T0 `10/80` run:

`T0_ISOLATED_10_80_CONTROL`

authority:

`f34b53597ab7d9175f8286dde67f4313462aabb5`

raw log authority:

`1e94740ff0edbc60d9faf4416f8f50a354b7f29596d125242309c306e7c8d4d6`

From the exact existing log/runtime state extract all available Segment fields, including at minimum:

```text
vm_weight_segmentation_enabled
vm_weight_segment_descriptors_loaded
vm_weight_segment_entries_configured
vm_weight_segment_local_table_entries
vm_weight_segment_lookup_attempts
vm_weight_segment_lookup_launches
vm_weight_segment_lookup_accepts
vm_weight_segment_lookup_completions
vm_weight_segment_hits
vm_weight_segment_misses
vm_weight_segment_effective_l1_hits
vm_weight_segment_effective_l1_misses
vm_weight_segment_l1_fills_suppressed
vm_weight_segment_l2_suppressed
vm_weight_segment_mshr_suppressed
vm_weight_segment_pwq_suppressed
vm_weight_segment_walker_suppressed
vm_weight_segment_pwc_suppressed
vm_weight_segment_pte_suppressed
vm_weight_segment_fallback_*
```

If fields are cumulative, bind them to exact target boundaries or prove isolated-run scope.

Create:

`T0_EXACT_SEGMENT_RUNTIME_STATE.tsv`

## 3. Fair-arm source/config closure

Trace the exact post-parse path from:

- parsed `gpgpu_vm_weight_segmentation_enable=1`;
- `gpgpu_vm_fair_arm=1`;
- F0 selection;
- final runtime `segment.enabled` state.

Use exact loaded source authority.

Create:

`F0_POST_PARSE_SEGMENT_STATE.md`

It must identify:

- where/when fair-arm mutates or selects Segment state;
- whether map path remains loaded while Segment functional lookup is disabled;
- source locations.

## 4. Existing repaired-F0 cross-check

Cross-check against accepted:

`a7110f789a2bc6761d8885a2ca5628b4acf50f69`

specifically:

`M0_P34_TARGET_BOUNDARY_DELTA.tsv`

which reports Segment disabled/zero participation.

Create:

`F0_SEGMENT_STATE_CONSISTENCY.tsv`

Rows:

- repaired P34 F0;
- V2 isolated T0 F0.

## 5. Decision

### PASS path

Only if exact V2 isolated T0 proves:

```text
runtime Segment disabled
lookup attempts = 0
lookup launches = 0
lookup completions = 0
hits = 0
misses = 0
all suppression counters = 0
```

emit:

`F0_SEGMENT_FUNCTIONALLY_DORMANT_CONFIRMED`

Then classify the exact existing Q05 maps as:

`MODEL_GENERIC_DORMANT_F0_COMPATIBILITY_ASSETS`

with explicit boundary:

- parser/config closure only;
- object labels not scientific target truth;
- Segment map not active functional translation in F0.

Proceed to Phase B.

### STOP path

If any exact V2 T0 Segment functional participation is nonzero:

`TARGET_SPECIFIC_VM_METADATA_REQUIRED_CONFIRMED`

STOP.

Do not start node109 automatically.

## 6. Phase B — T1/T2 compatibility admission

Only after PASS.

Use the exact same compatibility-asset bytes/SHA as accepted T0 V2:

```text
object-map SHA256  689af1cfe35897fb17e741cd9699a20dafaf3e529d7d7603447d6381066bfc99
segment-map SHA256 765d9793d0922e12f6c02d4a042c14eca3b35197ed48f246af3fb2187e66047c
```

Do not rewrite them as target-specific runtime metadata.

Treat them as part of the frozen F0 model configuration.

Build exact T1/T2 SIM_INPUT admission records binding:

- target producer identity;
- trace hash;
- model/revision/scenario;
- target occurrence/step;
- compatibility-asset SHA;
- evidence label `MODEL_GENERIC_DORMANT_F0_COMPATIBILITY_ASSETS`.

Object-labelled telemetry must be excluded from scientific comparison.

## 7. T1/T2 runtime Segment hard gate

For every T1/T2 simulation run, require:

```text
vm_weight_segmentation_enabled = 0
lookup attempts = 0
lookup launches = 0
lookup completions = 0
hits = 0
misses = 0
all Segment suppression counters = 0
```

Any nonzero value:

`STOP_SCIENTIFIC_SEGMENT_DORMANCY_VIOLATED_<TARGET>`

The run is NOT admitted.

## 8. Minimal science after admission

For each admitted target run only:

```text
10/80
0/80
```

No `0/0`.

Require terminal + full per-access coverage.

Primary metric:

`L1_ZERO_DELTA_FRAC_R0`

Compare against accepted T0:

`0.569994947261`

Also report:

- L1 hit rate;
- L2 behavior;
- walk density;
- requester latency/MSHR wait;
- lookup density vs accepted Native descriptors.

## 9. Scientific classification

If T1/T2 both complete:

choose among:

- `HITPATH_SENSITIVITY_SYSTEMATIC_ACROSS_KERNEL_CLASSES`
- `HITPATH_SENSITIVITY_ATTENTION_DOMINANT`
- `HITPATH_SENSITIVITY_TARGET_DEPENDENT`
- `SIMULATOR_HITPATH_MODEL_REQUIRES_SEMANTIC_RECALIBRATION`

If admission still fails:

`INSUFFICIENT_CROSS_TARGET_EVIDENCE`

No mechanism.

## 10. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/EXACT_F0_SEGMENT_STATE_CROSS_TARGET_174NEW_V3R1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_174_EXACT_F0_SEGMENT_STATE_CROSS_TARGET_V3R1/`

Required:

```text
README.md
SOURCE_ANCHORS.md
V3_NODE164_HASH_CLOSEOUT.md
T0_EXACT_SEGMENT_RUNTIME_STATE.tsv
F0_POST_PARSE_SEGMENT_STATE.md
F0_SEGMENT_STATE_CONSISTENCY.tsv
COMPATIBILITY_ASSET_AUTHORITY.json
T1_T2_SIM_INPUT_ADMISSION.tsv
SEGMENT_DORMANCY_INVARIANTS.tsv
CROSS_TARGET_L1_HITPATH_V3R1.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

STOP-path files may explicitly say NOT_RUN.

## 11. Remote publication

Apply mandatory 174 publication contract.

No local-only completion.

Then STOP.
