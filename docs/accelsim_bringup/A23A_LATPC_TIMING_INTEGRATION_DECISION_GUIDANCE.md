# A23A LATPC timing integration decision guidance

## Goal

Decide how to proceed after the shadow VM substrate.

A23A must not implement timing integration. It only produces a decision and future plan.

## Required script

Create:

scripts/accelsim/a23a_latpc_timing_integration_decision.py

## Inputs

A22C foundation report and readiness matrix.
A22A behavior comparison.
A22B sanity and sensitivity results.
A20B architecture.

## Decision options

Choose one primary path.

Option 1: SHADOW_FIRST_MECHANISM_PATH

Use when:

- shadow VM stats are working
- timing integration is still high risk
- next goal is Regularity Detector, LATC, LATP over shadow model
- this path cannot reproduce IPC speedup faithfully

Recommended if A22C is only address/partial or shadow stats are new.

Option 2: TIMING_INTEGRATION_PREP_PATH

Use when:

- shadow VM is robust
- TLB/MSHR/PTW counters are non-trivial
- behavior equivalence passed
- code hook quality is good
- future timing model can be designed next

This still does not implement timing in A23.

Option 3: FOUNDATION_REWORK_REQUIRED

Use when:

- stats inconsistent
- no useful shadow VM stats
- behavior changed
- address hook is too approximate

## Timing integration future plan

If timing integration is recommended later, the plan must mention:

1. Add a real translation request state machine or timing wrapper.
2. Model L1 TLB hit latency.
3. Model L2 TLB hit latency.
4. Model PTW latency and limited walkers.
5. Model TLB MSHR occupancy.
6. Stall or delay memory issue only when translation is unavailable.
7. Ensure disabled baseline remains identical.
8. Validate on synthetic targeted cases before NW.
9. Keep shadow and timing stats comparable.
10. Do not mix LATC/LATP mechanisms before baseline VM timing is validated.

## Shadow-first future plan

If shadow-first is recommended, the plan must mention:

1. A24 Regularity Detector over shadow VM.
2. A25 LATC over shadow MSHR.
3. A26 LATP over shadow PTW.
4. A27 combined LATPC shadow analysis.
5. The result can show mechanism potential but not IPC speedup reproduction.
6. Timing integration remains necessary for faithful paper speedup.

## Required outputs

.local_reports/A23A_latpc_timing_integration_decision_<timestamp>.md
.local_reports/A23A_latpc_timing_integration_plan_<timestamp>.csv

## Timing plan CSV columns

- future_round
- path
- task
- prerequisite
- expected_output
- risk
- notes

## Status rules

PASS:
Decision and future plan are clear.

PASS_WITH_WARNINGS:
Decision depends on partial or approximate substrate.

FAIL_NO_A22C:
A22C report missing.
