# CODEX 174-new — C16 E1 Shared Closure + Coverage-Scaling Consumer Prep Full Goal V1

## Mode

GOAL MODE / CPU-only independent closure + parallel next-stage prep

Suggested branch:

`hrl/c16-e1-coverage-scaling-consumer-174new-v1`

No GPU.
No simulator execution.
No trace capture.
No simulator source mutation.

## Read first

Fetch and verify:

`hrl/c16-e1-coverage-scaling-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_coverage_scaling_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_coverage_scaling_v1/DESIGN.md`
3. `docs/vm_tlb/chatgpt_handoff/c16/e1_coverage_scaling_v1/LAYER_SELECTION_PRECONTRACT.json`
4. `docs/vm_tlb/chatgpt_handoff/c16/e1_coverage_scaling_v1/STAGE_DECISION_PRECONTRACT.json`
5. this file

Also read the latest shared-residency handoff audit:

`docs/vm_tlb/chatgpt_handoff/c16/e1_shared_residency_mechanism_feasibility_v1/CONSUMER_RESUME_AUDIT_V3.md`

Accepted shared producer:

`hrl/c16-e1-shared-residency-feasibility-109-v1@1e701f013fc174b5b4df9febb5c33500f9ea586e`

Current design/consumer prep:

`hrl/c16-e1-shared-residency-design-review-174new-v1@547e9263a8d0c12bb34d96e27134a120b83fb6d0`

Latest consumer hardening:

`hrl/c16-e1-shared-residency-consumer-hardening-v2@87998e7fcdcc1422ca87e8814bf054cb65161657`

## Goal

Complete one large CPU-only Goal:

1. independently close the already completed shared-residency producer;
2. preserve the shared-stage conclusion;
3. independently quantify the three-module Amdahl/realization result;
4. audit the prior simulator/project evidence relevant to coverage;
5. freeze and implement the next coverage-scaling consumer before new producer data appears;
6. fetch the coverage producer once after prep and consume if already available;
7. otherwise STOP READY.

Do not run a simulator.

---

# Part A — close the shared-residency producer first

## A1. Apply consumer hardening

Base the working branch on the current reviewed consumer/design state and apply:

`hrl/c16-e1-shared-residency-consumer-hardening-v2@87998e7fcdcc1422ca87e8814bf054cb65161657`

Do not redo the static design review.

Run all shared/critical-path tests plus upstream regressions.

## A2. Normalize real producer raw schema

Producer raw native authority exposes:

- policy_receipt
- policy_transitions
- policy_transition_count
- qweight_regions
- semantic/timing evidence

Rotating authority exposes:

- policy_receipt
- window_transitions
- A/B qweight regions.

Build deterministic adapters only from raw evidence.
Preserve source SHA provenance.

Do not use producer summaries as calculation authority.

## A3. Real-artifact canaries

At minimum close:

- RAW_SHARED_NATIVE_ROTATE_CONTROL_3_run0
- RAW_SHARED_NATIVE_SHARE3_run0
- RAW_SHARED_NATIVE_SHARE2_UP_run0
- one ROTATE_PERSIST_A_B_A repetition
- one shared D3 NCU profile

Verify:

- fixed requested 33,947,648 B;
- runtime query-back 37,748,736 B;
- exact 15-update full-model schedule;
- selected PERSISTING vs non-selected NORMAL/NORMAL;
- no in-run reset;
- token/SHA identity;
- BASE/SESSION/PROFILE/policy identity.

## A4. Independent shared analysis

Recompute from raw:

- rotating qualification;
- local target timing benefits;
- stable D1-D3 whole-decode benefit;
- policy API overhead;
- 14-profile NCU additive effects;
- critical-path metrics;
- stage label.

Do not read producer SHARED_POLICY_ANALYSIS.json as calculation authority.

Expected producer label is cross-check only:

`SHARED_RESIDENCY_LOCAL_ONLY`

## A5. Multi-pass NCU handling

For critical-path profiles with multiple application replay passes:

- every PASS receipt must have identical semantic/token/policy identity;
- BASE `profiler__replayer_passes` must match PASS receipt count.

Do not require exactly one PASS receipt when multiple passes are legitimately collected.

## A6. Shared closure output

Update/finalize:

`docs/vm_tlb/review_packs/C16_E1_SHARED_RESIDENCY_DESIGN_REVIEW_174NEW_V1/`

Add at minimum:

- `INDEPENDENT_SHARED_POLICY_ANALYSIS.json`
- `INDEPENDENT_CRITICAL_PATH_ANALYSIS.json`
- `PRODUCER_RAW_PROVENANCE_AUDIT.json`
- `PRODUCER_MATCH_CHECK.json`
- `REAL_ARTIFACT_CANARIES.json`

Preserve:
- prior producer/strict-consumer divergence;
- traffic caveat;
- no simulator implementation authorization.

---

# Part B — independent Amdahl/coverage audit of the accepted shared stage

Using raw shared native timing, independently compute for stable D1-D3:

For the three SHARE3 targets:
- L0 up
- L14 up
- L0 down

Per run compute:

`target_share = sum(three control target times) / ROTATE_CONTROL_3 decode-step time`

`summed_local_saving = sum(control target time - SHARE3 target time)`

`observed_decode_saving = ROTATE_CONTROL_3 decode-step time - SHARE3 decode-step time`

`realization_ratio = observed_decode_saving / summed_local_saving`

Do not clamp.

Expected approximate cross-check only:

- three-target share ~1.74% of stable decode;
- local savings ~0.42-0.47% of decode;
- realization ratio roughly 0.79-0.89.

Create:

`SHARED_STAGE_AMDAHL_AUDIT.json`

This artifact should explicitly state:

- the <0.5% whole-decode result is consistent with limited protected coverage;
- it is not evidence that local savings fail to realize systemically.

---

# Part C — audit prior simulator/project evidence relevant to coverage

Create:

`COVERAGE_PRIOR_AUDIT.md`

Read accepted historical C12 operator-aware evidence, especially:

- C12 operator-aware final report
- layer robustness findings
- kernel criticality findings

Record only what those sources support:

- FFN and Attention Projection responses were broadly repeated across directly attributable layers in those experiments;
- some Decode comparisons were distributed across many kernels;
- this motivates broad layer-coverage testing.

Explicitly state:

- C12 is not direct evidence for AWQ qweight residency;
- C12 does not quantify the expected benefit of this new persistence policy;
- do not transfer its cycle percentages into the new experiment.

---

# Part D — freeze simulator platform authority without running it

Create:

`SIMULATOR_PLATFORM_AUTHORITY_AUDIT.json`

Verify remote accepted authority:

- Core code mapping:
  `swayhrl/gpgpu-sim@57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- platform:
  `RTX4080_ADA_ACCELSIM_BASE_V1`
- config:
  `configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config`
- config SHA:
  `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`
- qualification:
  `RTX4080_ADA_PLATFORM_QUALIFIED`

Also preserve the known scope:
qualified for memory/translation/cache studies, not universal cycle-accuracy.

Explicitly state:
no SM86/RTX3080 configuration is to be used for the eventual first residency mechanism experiment.

Do not run the simulator.

---

# Part E — build the coverage-scaling consumer before producer data

## E1. FFN census consumer

Freeze exact expected model structure:

- 28 layers
- gate_proj/up_proj/down_proj requested
- runtime authority decides whether each role is supported.

Fail closed on:
- duplicate/missing layer/module;
- wrong module class;
- qweight identity drift;
- nonfinite timing;
- duplicate/missing rep;
- token/SHA drift.

Compute run-aligned role shares:
- up
- gate
- down
- total supported FFN projections.

## E2. Coverage policy consumer

Use exact layer sets from:

`LAYER_SELECTION_PRECONTRACT.json`

Validate every CONTROL/FAIR condition:

- fixed requested set-aside 33,947,648 B;
- fixed actual query-back 37,748,736 B;
- exact selected layer set;
- exact PREFILL + D0-D3 update order;
- exact full up_proj qweight window;
- hitRatio=1/N;
- CONTROL uses NORMAL/NORMAL;
- FAIR uses PERSISTING/STREAMING;
- no in-run reset;
- reset before/after condition.

All 28 up_proj occurrences must be present in all runs, selected and non-selected.

## E3. Coverage timing/Amdahl consumer

Compute from run-aligned raw rows:

- selected target share;
- summed local saving;
- observed decode saving;
- realization ratio;
- non-selected aggregate effect;
- selected layer material fraction;
- stable D1-D3 effect.

Do not compute target share using independent medians only.

## E4. N14 holdout consumer

Independently compare N14A and N14B using the same metrics.

No winner selection.

## E5. Coverage NCU consumer

Reuse category-aware critical-path rules.

Freeze exact 16-point maximum primary NCU matrix from DESIGN.

Fail closed on:
- metric query/version ambiguity;
- unit drift;
- kernel inventory mismatch;
- wrong semantic occurrence;
- missing policy history;
- replay-pass/PASS-receipt mismatch.

## E6. FULLHINT trigger consumer

Implement STAGE_DECISION_PRECONTRACT exactly.

If trigger false:
require producer not to run FULLHINT.

If trigger true:
require exact N8/N28 CONTROL_FULL/FULLHINT matrix.

Interpret hitRatio=1 as over-subscribed intent under fixed total set-aside, not infinite effective capacity.

## E7. Synthetic tests

Add adversarial tests for:

- wrong layer set
- post-data layer selection attempt
- missing layer event
- selected/non-selected confusion
- wrong 1/N hitRatio
- actual set-aside drift
- in-run reset
- token/SHA drift
- target-share median-of-medians bug
- zero/negative local-saving realization denominator
- N14 set mismatch
- FULLHINT run when trigger false
- FULLHINT missing when trigger true
- NCU unit/pass mismatch.

---

# Part F — coverage consumer review pack

Prepare:

`docs/vm_tlb/review_packs/C16_E1_COVERAGE_SCALING_CONSUMER_174NEW_V1/`

At minimum:

- `UPSTREAM_SHARED_CLOSURE_AUDIT.json`
- `SHARED_STAGE_AMDAHL_AUDIT.json`
- `COVERAGE_PRIOR_AUDIT.md`
- `SIMULATOR_PLATFORM_AUTHORITY_AUDIT.json`
- `FFN_CENSUS_CONSUMER_CONTRACT.json`
- `COVERAGE_POLICY_CONSUMER_CONTRACT.json`
- `COVERAGE_ANALYSIS_CONSUMER_CONTRACT.json`
- `COVERAGE_NCU_CONSUMER_CONTRACT.json`
- `FULLHINT_CONSUMER_CONTRACT.json`
- `CONSUMER_TESTS.tsv`
- `INDEPENDENT_FFN_OPPORTUNITY_ANALYSIS.json` when producer ready
- `INDEPENDENT_COVERAGE_SCALING_ANALYSIS.json` when producer ready
- `INDEPENDENT_N14_HOLDOUT.json` when producer ready
- `INDEPENDENT_COVERAGE_CRITICAL_PATH.json` when producer ready
- `INDEPENDENT_FULLHINT_ANALYSIS.json` when applicable
- `PRODUCER_MATCH_CHECK.json`
- `FINAL_DECISION.json`
- `NEXT_STEP_AUTHORIZATION.json`
- `SHA256SUMS`

---

# Part G — one-shot fetch coverage producer

Expected producer branch:

`hrl/c16-e1-coverage-scaling-109-v1`

After all prep and tests:

fetch producer once.

If complete:
- consume raw evidence directly;
- independently close the stage;
- update scientific log;
- commit/push/verify/clean;
- STOP_FOR_CHATGPT_REVIEW.

If absent/incomplete:
- commit/push prep;
- verify/clean;
- STOP:

`READY_FOR_E1_COVERAGE_SCALING_109`

Do not poll.

---

# Boundary

Do not:

- use GPU;
- execute Accel-Sim;
- mutate GPGPU-Sim;
- capture trace;
- run NVBit;
- implement mechanism;
- simulate mechanism.

Routine parser/schema/Git/document issues:
solve-and-continue.

Small correctness-preserving changes:
fix in this Goal.

Only stop early for a real scientific authority/identity contradiction.
