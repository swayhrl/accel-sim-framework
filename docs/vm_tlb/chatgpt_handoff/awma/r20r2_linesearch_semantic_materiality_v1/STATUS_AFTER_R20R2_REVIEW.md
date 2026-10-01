# R20R2 review after threshold-only classification

Date: 2026-10-01

Execution authority:
- branch: `hrl/awma-r20r2-linesearch-semantic-materiality-109-v1`
- commit: `e645b5e011c18f1e44b7a1509fb55c49486adff5`
- tree: `a84dfb574feed44d8b64c4e5ea41858351be721e`
- formal label: `R20R2_LINESEARCH_DIAGNOSTIC_THRESHOLD_ONLY`

## Accepted evidence

The exact frozen t152 solver entry and world413 reproduced both LS outcomes under observer-ON:
- 31 qualified same-graph replays
- 30 LS clear
- 1 LS set
- observer-OFF regression: 5/5 qualified

The decisive paired divergence is outer solver iteration 2, inner line-search iteration 1:
- clear: hi_next derivative = +0.00244140625, gtol_accept ~= 0.011216454, conv_hi=true
- set: hi_next derivative = -0.01318359375, gtol_accept ~= 0.011216399, conv_hi=false
- set case subsequently reaches the unchanged 20-iteration line-search bound

Yet:
- nefc remains 46
- outer solver_niter remains 8
- constraint coverage remains exact
- selected outer-2 alpha in the set case lies inside the observed clear-run alpha range
- selected improvement lies inside the observed clear-run improvement range
- qacc/qfrc_constraint/efc.force/efc.Ma differences remain far below the pre-frozen local numerical screen
- fixed source writes LS_ITERATIONS after applying the selected step
- no fixed-source numerical-control path was found to consume the LS bit
- bounded scratch audit found no specific read-before-write dependency required to explain the flip

Therefore the exact LS bit alone is not a defensible future numerical-equivalence gate for this local solver-entry study.

## Important limitation

This does NOT mean:
- LS_ITERATIONS is globally harmless
- line-search mathematical convergence occurred in the set-bit replay
- every future LS flip may be ignored
- the observer proved the complete solver deterministic
- active-world scheduling is correct or fast

The paired clear/set traces already differ slightly in earlier floating state. The observer may perturb execution probability even when it preserves accepted outputs; frequency 1/31 is not treated as a property of the uninstrumented solver.

The scientific result is about **semantic materiality under the frozen local contract**, not flip probability.

## Future active-world numerical contract — accepted for a new experiment

A future active-world B0/S1 experiment may use a new contract that keeps the following as hard gates:

1. exact solver-entry identity and options
2. exact world / constraint identity and coverage
3. exact nefc
4. exact outer solver_niter
5. no new true capacity overflow
6. finite outputs
7. ctx.done / completion semantics
8. the already-frozen qacc/qfrc_constraint/efc.Ma/valid-efc.force local floating screens
9. qfrc source relation / source-justified residual checks
10. no hidden-state dependency or stale-output evidence

`LS_ITERATIONS` must be recorded per world, with count/location and selected alpha/improvement impact, but **the bit by itself is not a hard B0/S1 equality gate**.

Any LS difference that is accompanied by:
- changed outer niter
- changed coverage
- output outside the frozen local contract
- materially different alpha/path that propagates beyond the accepted envelope
- new hidden-state dependency
remains a correctness failure.

Capacity overflow and outer `ITERATIONS` remain separate hard outcomes.

This is a new contract for a future experiment. R20R1's historical exact-stop contract and STOP remain unchanged.

## Readiness for next step

The active-world performance question is now eligible for one bounded Native software diagnostic.

Recommended next stage:
`R20R3_ACTIVE_WORLD_SOLVER_NATIVE_DIAGNOSTIC`

It should:
- reuse the frozen real solver-entry corpus
- use the revised contract above
- implement exactly one online active-world/worklist diagnostic
- measure complete `solver.solve`, including list/queue/reset/index/synchronization costs
- use the predeclared discovery entries first
- open holdout entries only after candidate/contract freeze and only if discovery shows stable material response
- keep full physics-step and RL-training claims out of scope

No hardware / node174 / Accel-Sim admission follows automatically from a positive Native response.

Current state:
- R20R2: STOP, accepted
- active-world performance: READY_FOR_BOUNDED_NATIVE_DIAGNOSTIC
- architecture review: NOT READY
- Lane F: STOP pending explicit R20R3 authorization
- Lane E/G: STOP
- node174 / Accel-Sim: STOP
