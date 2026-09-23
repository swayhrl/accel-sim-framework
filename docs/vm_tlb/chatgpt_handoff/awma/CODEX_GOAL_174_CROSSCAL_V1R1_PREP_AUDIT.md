# CODEX 174 GOAL — Cross-Calibration V1R1 Prep / Mechanism-Opportunity Audit

Date: 2026-09-23

Mode:

`GOAL MODE / bounded audit + opt-in telemetry / solve-and-continue`

Node:

`174-new`

Stage:

`AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1R1_PREP`

Read first:

`docs/vm_tlb/chatgpt_handoff/awma/REVIEW_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1_2026-09-23.md`

Frozen V1 execution authority:

`hrl/awma-174-native-simulator-cross-calibration-v1 @ 6f9c1df1a03bd9d26130b80be1c31f5957074630`

This Goal does NOT rerun the 24-point matrix and does NOT modify V1/V2R1 semantics.

## 1. Confirm current trace-phase identity from surviving durable evidence

For M0/M1/M2/M3:

- inspect the exact selected trace header/instruction stream;
- inspect durable producer receipts/logs if available on node164;
- bind selector `chase_occurrence_0`;
- prove the selected kernel has 2 brackets/warp;
- bind accepted probe source launch order:
  warmup `chase(... warmup=2 ...)` first,
  measured `chase(... samples=50 ...)` second.

Publish an explicit conclusion:

`CURRENT_M0_M3_TRACE_PHASE = WARMUP_CHASE_OCCURRENCE0`

if the evidence closes.

Also search the durable bundle for any surviving `chase_occurrence_1` or full-process trace payload.

If a measured-kernel payload already exists and has accepted identity/provenance, record it; do not recapture on 174.

If absent, record:

`MEASURED_OCCURRENCE1_TRACE_NOT_PRESENT_IN_ACCEPTED_BUNDLE`

## 2. Recover command/seed authority if possible

Search existing producer receipts/logs/node164 metadata for the exact microtrace capture CLI.

Attempt to recover:

- stride;
- locations;
- warps;
- steps;
- samples;
- warmup;
- policy;
- seed.

Do not infer seed.

If no accepted evidence closes seed, retain:

`TRACE_PERMUTATION_SEED_UNRESOLVED`

## 3. Add opt-in accessq-cardinality telemetry

Use a new independent observational switch, e.g.:

`GPGPUSIM_AWMA_ACCESSQ_CARDINALITY_DIAGNOSTICS=1`

Requirements:

- default OFF;
- parsed centrally;
- observational only;
- must not alter scheduling, coalescing, accessq contents, translation, cache, retry, timing, random state, or ordering;
- output prefix `awma_accessq_cardinality_`.

At the point where a memory instruction's coalesced accessq is available, record at minimum:

- kernel UID;
- sid;
- warp/dynamic warp;
- instruction PC;
- active lane count if available;
- accessq entry count;
- memory instruction ordinal or unique event ID.

Aggregate:

- number of relevant dependent-load instructions;
- min/mean/max accessq entries;
- histogram of cardinality;
- fraction with cardinality >1.

## 4. Telemetry neutrality

For at least M1 and M2 at 10/80 Legacy:

compare telemetry OFF versus ON.

Require exact equality in:

- gpu_sim_cycle;
- gpu_sim_insn;
- CTA;
- translation/cache counters;
- terminal quiescence.

Only new accessq telemetry may differ.

## 5. Mechanism-opportunity classification

Run only the minimum small existing points needed to classify M0–M3.

If every dependent load has:

`accessq_entries == 1`

classify:

`M0_M3_MECHANISM_INACTIVE_CONTROL_SUITE`

for V1/V2R1.

If any point has cardinality >1, publish exact distribution and identify which trace can exercise V1/V2R1.

Do not infer mechanism opportunity solely from warp count.

## 6. SM89 compatibility audit

The current cross-cal path opt-in maps binary version 89 to the existing Ampere opcode map.

Publish:

`SM89_OPCODE_COMPATIBILITY.tsv`

containing every distinct opcode in M0–M3 and:

- trace opcode spelling;
- whether it exists in the selected opcode map;
- decoded instruction class;
- whether the cross-calibration relies on any opcode with known/unresolved Ada-vs-Ampere semantic difference.

This is an admission/parser compatibility audit, not an Ada fidelity claim.

If an essential opcode is unsupported or semantically unresolved, STOP with:

`SM89_OPCODE_COMPATIBILITY_NOT_CLOSED`

## 7. Full simulator config authority

Recover and publish the exact simulator configuration used by Cross-Cal V1:

- base config file(s);
- SHA256;
- VM/TLB latency overrides;
- relevant architecture parameters;
- binary SHA.

The V1 review pack did not bind the base hardware config strongly enough.

Do not change config.

## 8. Reclassify Cross-Cal V1 evidence

Create:

`CROSSCAL_V1_SCOPE_RECLASSIFICATION.md`

Preserve all 24-point data, but distinguish:

- valid simulator results;
- warmup-trace supporting-only comparisons;
- mechanism-active versus mechanism-inactive evidence;
- claims that remain unadmitted pending exact measured-kernel traces.

Do not edit/delete the original V1 publication.

## 9. Deliverables

Suggested branch:

`hrl/awma-174-crosscal-v1r1-prep`

Report:

`docs/vm_tlb/codex_handoff/awma/NATIVE_SIMULATOR_CROSS_CALIBRATION_174NEW_V1R1_PREP_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1R1_PREP/`

Required:

```text
README.md
SOURCE_ANCHORS.md
TRACE_PHASE_IDENTITY.tsv
TRACE_COMMAND_AUTHORITY.tsv
ACCESSQ_DIAGNOSTIC_CONTRACT.md
ACCESSQ_DIAGNOSTIC.patch
ACCESSQ_TELEMETRY_NEUTRALITY.tsv
ACCESSQ_CARDINALITY.tsv
MECHANISM_OPPORTUNITY_DECISION.md
SM89_OPCODE_COMPATIBILITY.tsv
SIMULATOR_CONFIG_AUTHORITY.json
CROSSCAL_V1_SCOPE_RECLASSIFICATION.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

## 10. Stop boundary

No 24-point rerun.
No T0/T1/T2 rerun.
No new TLB/PTW/cache mechanism.
No parameter tuning.

Ordinary engineering problems solve-and-continue.

STOP only for a real scientific identity/compatibility contradiction.

Publish/fetch-back/hash/remote-tree verify/clean worktree, then STOP.
