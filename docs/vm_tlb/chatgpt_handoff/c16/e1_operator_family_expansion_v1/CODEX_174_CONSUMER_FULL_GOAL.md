# CODEX 174-new — Coverage Closure + Operator-Family Consumer Prep Full Goal V1

## Mode

GOAL MODE / CPU-only independent closure + next-stage prep

Suggested branch:

`hrl/c16-e1-operator-family-expansion-consumer-174new-v1`

No GPU.
No simulator execution.
No trace capture.
No simulator mutation.

## Read first

Fetch and verify:

`hrl/c16-e1-operator-family-expansion-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_operator_family_expansion_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_operator_family_expansion_v1/COVERAGE_PRODUCER_PRE_RESUME_AUDIT.md`
3. `docs/vm_tlb/chatgpt_handoff/c16/e1_operator_family_expansion_v1/DESIGN.md`
4. `docs/vm_tlb/chatgpt_handoff/c16/e1_operator_family_expansion_v1/CONDITION_MATRIX_PRECONTRACT.json`
5. `docs/vm_tlb/chatgpt_handoff/c16/e1_operator_family_expansion_v1/STAGE_DECISION_PRECONTRACT.json`
6. this file

Accepted coverage producer:

`hrl/c16-e1-coverage-scaling-109-v1@18acd7dcc10118c68b450d226a8e7ca80c51ad72`

Current coverage consumer prep:

`hrl/c16-e1-coverage-scaling-consumer-174new-v1@5481d85951180dae90776442c3e0620af96a4712`

## Goal

Execute one large CPU-only Goal:

1. independently close the completed coverage producer from raw evidence;
2. freeze the coverage-stage interpretation;
3. independently audit the N28 realization residual;
4. build/freeze the operator-family consumer before producer data;
5. fetch operator-family producer once after prep and consume if ready;
6. otherwise STOP READY.

No simulator run.

---

# Part A — coverage producer raw closure

## A1. Do not trust producer summaries as authority

Directly consume:

- RAW_CENSUS_run*.json
- RAW_COVERAGE_CONTROL/FAIR_*_run*.json
- RAW_FULLHINT_*_run*.json
- raw NCU BASE/SESSION/PROFILE
- raw metric-query evidence
- raw policy histories.

Producer summaries are final cross-check only.

## A2. Normalize producer native schema

Coverage raw files expose:

- selected_layers
- module_census
- all 28 up_proj occurrences
- decode_step_ms
- policy_receipt
- policy_transitions
- policy_transition_count
- requested/actual set-aside.

Build deterministic adapters into the already frozen consumer schema.

Preserve source SHA provenance for every normalized file.

N28 must independently close:

- 112 up_proj decode occurrences per run
- 140 policy transitions per run
- 7 CONTROL + 7 FAIR fresh runs
- exact tokens/SHA
- requested 33947648 B
- actual 37748736 B.

## A3. Coverage real-artifact canaries

At minimum:

- RAW_CENSUS_run0
- RAW_COVERAGE_CONTROL_N28_run0
- RAW_COVERAGE_FAIR_N28_run0
- RAW_FULLHINT_FULLHINT_N28_run0
- one primary N28 NCU profile.

All must PASS before full consume.

## A4. Independent FFN opportunity census

From raw 7 census runs independently recompute:

- gate share
- up share
- down share
- all-FFN projection share
- per-layer distributions
- all 84 qweight-backed identity.

Producer approximate cross-check only:

gate ~14.76%
up ~16.84%
down ~15.78%
all FFN ~47.39%.

## A5. Independent coverage curve

Recompute N1/N2/N4/N8/N14A/N14B/N28 from raw run-aligned rows.

Do not use ratio-of-independent-medians as authority.

Independently recompute:

- selected target share
- summed local saving
- observed decode saving
- realization ratio
- local material-layer fraction
- non-selected up_proj effect
- whole-decode effect.

Apply the frozen pre-data stage decision exactly.

Producer label is cross-check only:

`COVERAGE_SCALING_POSITIVE_BUT_SUBTHRESHOLD`

## A6. N28 residual audit

Create:

`COVERAGE_N28_RESIDUAL_AUDIT.json`

From raw run-aligned N28 rows compute:

`residual_outside_selected_up = observed_decode_saving - selected_up_local_saving`

Summarize:
- median/min/max;
- residual / local saving;
- whole-decode realization.

Do not name the residual cache collateral slowdown.

State explicitly:
- N28 has no non-selected up_proj bucket;
- source of residual is unresolved because gate/down/other work was not timed in N28 coverage conditions.

This artifact is a key input to the next stage.

## A7. N14 holdout

Independently close N14A/N14B:
- share
- local distribution
- whole decode
- realization.

No winner selection.

## A8. FULLHINT

Verify frozen trigger fires from independent N28 result.

Consume exact four conditions:
- CONTROL_FULL_N8
- FULLHINT_N8
- CONTROL_FULL_N28
- FULLHINT_N28.

Confirm additional FULLHINT NCU trigger is false if independent FAIR-vs-FULLHINT N28 difference <0.5 percentage points.

Do not require absent evidence.

## A9. Coverage NCU

Consume exact primary 16-profile matrix.

Multi-pass rules:
- all PASS receipts identical in semantic/token/policy identity;
- BASE profiler__replayer_passes equals PASS receipt count.

Preserve:
- additive sums where valid;
- non-additive per-kernel values.

Independently close the N28 duration/stall vs traffic-dilution observation.

---

# Part B — finalize coverage consumer pack

Complete:

`docs/vm_tlb/review_packs/C16_E1_COVERAGE_SCALING_CONSUMER_174NEW_V1/`

Fill:

- INDEPENDENT_FFN_OPPORTUNITY_ANALYSIS.json
- INDEPENDENT_COVERAGE_SCALING_ANALYSIS.json
- INDEPENDENT_N14_HOLDOUT.json
- INDEPENDENT_COVERAGE_CRITICAL_PATH.json
- INDEPENDENT_FULLHINT_ANALYSIS.json
- PRODUCER_MATCH_CHECK.json
- FINAL_DECISION.json
- NEXT_STEP_AUTHORIZATION.json

Add:

- COVERAGE_N28_RESIDUAL_AUDIT.json
- PRODUCER_RAW_PROVENANCE_AUDIT.json
- REAL_ARTIFACT_CANARIES.json

Preserve:
- no simulator auto-authorization.

---

# Part C — freeze operator-family consumer before producer data

## C1. Natural FFN call-order consumer

Implement consumer for a raw natural call-order authority.

Require:
- exact 84 FFN projection call sequence in PREFILL/D0-D3;
- same sequence across fresh processes;
- no duplicate/missing module occurrence.

The consumer must not assume gate/up/down order without raw evidence.

## C2. Module authority

Freeze exact:
- 28 layers
- gate/up/down
- AWQ WQLinear_GEMM
- qweight-backed exact intervals.

Fail closed on:
- role missing
- module class/backend drift
- qweight bytes/span/contiguity drift.

## C3. Condition matrix

Use exactly:

`CONDITION_MATRIX_PRECONTRACT.json`

Require all 14 primary conditions.

No post-data condition selection.

## C4. Policy consumer

For each condition:

- fixed requested 33947648 B
- actual query-back 37748736 B
- exact selected module set
- update immediately before selected module natural call
- exact qweight window
- hitRatio=1/K
- CONTROL NORMAL/NORMAL
- FAIR PERSISTING/STREAMING
- no in-run reset
- reset before/after condition.

Unselected modules must have no policy update in this stage.

## C5. Native timing consumer

Every condition:
- 7 fresh processes
- exact tokens
- all 84 FFN D0-D3 input/output SHA
- all 84 FFN timings
- D0-D3 decode timing
- policy overhead.

Fail closed on missing/duplicate event or rep.

## C6. Residual decomposition consumer

Run-aligned compute exactly:

- SELECTED_SHARE
- DIRECT_SELECTED_SAVING
- UNSELECTED_FFN_SAVING
- TOTAL_FFN_SAVING
- OBSERVED_DECODE_SAVING
- OUTSIDE_FFN_RESIDUAL
- SELECTED_REALIZATION
- FFN_REALIZATION.

Ratios unclamped.

Do not label negative residual as cache slowdown automatically.

## C7. Host-overhead consumer

Independently compare CONTROL/FAIR:
- per-update API duration
- total API duration per run
- overhead delta.

Do not subtract from GPU timing.

## C8. NCU consumer

Freeze the 12-profile representative matrix from DESIGN.

Re-use category-aware aggregation:
- additive only when semantically additive;
- stall/utilization/occupancy per-kernel.

Require runtime metric query receipt.

## C9. FULLHINT GUD84

Implement frozen trigger and exact two-condition matrix.

If trigger false:
evidence must be absent.

If trigger true:
evidence must be present.

Additional NCU only if >=0.5 percentage-point change versus FAIR_GUD84.

## C10. Stage decision

Implement:

`STAGE_DECISION_PRECONTRACT.json`

exactly.

No auto simulator authorization.

## C11. Synthetic/adversarial tests

Cover at least:

- wrong natural call order
- missing FFN module
- role drift
- selected-module set drift
- update attached to wrong module
- wrong hitRatio
- actual set-aside drift
- in-run reset
- token/SHA drift
- missing all-84 timing event
- direct-saving median-of-medians bug
- residual sign handling
- negative/zero realization denominator
- host-overhead unit mismatch
- NCU multipass mismatch
- FULLHINT false/true matrix mismatch.

---

# Part D — operator-family consumer prep pack

Create:

`docs/vm_tlb/review_packs/C16_E1_OPERATOR_FAMILY_EXPANSION_CONSUMER_174NEW_V1/`

At minimum:

- `UPSTREAM_COVERAGE_CLOSURE_AUDIT.json`
- `COVERAGE_N28_RESIDUAL_AUDIT.json`
- `NATURAL_CALL_ORDER_CONSUMER_CONTRACT.json`
- `OPERATOR_FAMILY_POLICY_CONSUMER_CONTRACT.json`
- `OPERATOR_FAMILY_ANALYSIS_CONSUMER_CONTRACT.json`
- `OPERATOR_FAMILY_NCU_CONSUMER_CONTRACT.json`
- `FULLHINT_GUD84_CONSUMER_CONTRACT.json`
- `CONSUMER_TESTS.tsv`
- `INDEPENDENT_ROLE_ONLY_ANALYSIS.json` when producer ready
- `INDEPENDENT_PAIRWISE_ANALYSIS.json` when producer ready
- `INDEPENDENT_ALL_FFN_ANALYSIS.json` when producer ready
- `INDEPENDENT_RESIDUAL_DECOMPOSITION.json` when producer ready
- `INDEPENDENT_CRITICAL_PATH.json` when producer ready
- `INDEPENDENT_FULLHINT_GUD84.json` when applicable
- `PRODUCER_MATCH_CHECK.json`
- `FINAL_DECISION.json`
- `NEXT_STEP_AUTHORIZATION.json`
- `SHA256SUMS`

---

# Part E — one-shot producer fetch

Expected:

`hrl/c16-e1-operator-family-expansion-109-v1`

After all prep/tests:

fetch once.

If producer complete:
- consume raw evidence;
- independently close;
- update scientific log;
- commit/push/verify/clean;
- STOP_FOR_CHATGPT_REVIEW.

If absent/incomplete:
- commit/push prep;
- verify/clean;
- STOP:

`READY_FOR_E1_OPERATOR_FAMILY_EXPANSION_109`

No polling.

---

# Boundary

No GPU.
No Accel-Sim.
No GPGPU-Sim mutation.
No NVBit.
No trace capture.
No mechanism implementation/simulation.

Routine parser/schema/Git issues:
solve-and-continue.

Small fixes:
repair in this Goal.

Stop early only for a true scientific authority/identity contradiction.
