# New R20R3P2 source-semantic stop contract — frozen before fresh B0 qualification

This is a separate prospective contract. R20R1/R20R3P1 historical residual-envelope failures remain unchanged. No previous S1 residual amplitude, offending-world count, or distribution enters this rule. The configured solver `tolerance` is used exactly; there is no new multiplier or fitted error cutoff.

Retain hard gates for: exact accepted solver-entry/Model/options/source and all world/constraint identity/coverage; exact `nefc`; exact per-world outer `solver_niter` and non-LS status relative to the accepted B0 reference; no new true capacity overflow; finite effective qacc/qfrc_constraint/efc.Ma/valid efc.force; all `ctx.done` true at complete-solver exit; unchanged R20R1 perworld `0.0005301662193351918` and normalized global-RMS `1.1920928955078125e-5` screens on those four effective outputs; qfrc source relation at the unchanged `100*eps32`; no stale or hidden-state evidence. `LS_ITERATIONS` is recorded under R20R2 semantics but the bit alone is not an equality gate. Outer `ITERATIONS` remains distinct and exact under the source stop interpretation below.

Replace only the historical B0-max final-gradient/model-improvement *value envelope* with exact source-stop consistency. After each complete solver replay, a diagnostic-only Warp kernel reads the graph-end context and recomputes the source's four predicates in float32: `alpha==0`, `0<rescaled improvement<tolerance`, `rescaled sqrt(grad_dot)<tolerance`, `rescaled 0.5*newton_decrement<tolerance`. It also records the rescaled values, final `solver_niter`, done flag and entry/exit `ITERATIONS` bits. This diagnostic is outside solver graph and outside any formal timing; it cannot change solver math.

For every world:

1. `ctx.done` must be true and `1<=solver_niter<=iterations` on the fixed nonempty solve.
2. If `solver_niter<iterations`, at least one source predicate must be true. A newly set `ITERATIONS` bit here is forbidden. A bit inherited from the frozen entry is reported separately, not mistaken for a new limit stop.
3. If `solver_niter==iterations` and the source predicate is false, classify `LIMIT_STOP_NOT_MATHEMATICAL_CONVERGENCE`; require `ITERATIONS` present in the exit bitmask. A newly set bit is valid only in this exact case.
4. If `solver_niter==iterations` and the predicate is true, classify `PREDICATE_DONE_ON_FINAL_ALLOWED_ITERATION`; the source does not newly set `ITERATIONS`. An inherited entry bit is only historical status.
5. Any newly set `ITERATIONS` bit requires `solver_niter==iterations` and a false predicate. Nonfinite predicate inputs, negative `grad_dot`, or ambiguous provenance that prevents the above classification fail closed.

The first 32 B0-only replays are preregistered: eight independent full-entry restores per t128/t136/t144/t152, same graph/capture policy, no extension based on outcome. All must pass every retained gate and this stop rule before the offline negative validator or S1. Directed negatives must reject false-done/nonlimit, early niter, missed constraint, stale qacc/qfrc, and inconsistent newly set `ITERATIONS`. Only then may this new contract be labeled qualified and used prospectively; it never changes earlier accepted conclusions.
