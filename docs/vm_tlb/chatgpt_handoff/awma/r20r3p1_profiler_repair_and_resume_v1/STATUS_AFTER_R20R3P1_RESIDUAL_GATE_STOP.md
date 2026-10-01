# R20R3P1 review after final-gradient residual-gate stop

Date: 2026-10-01

Execution authority:
- branch: `hrl/awma-r20r3p1-profiler-repair-resume-109-v1`
- commit: `53837e8366f0d96a636c89365b782aa411e7bc63`
- tree: `1c46eb3135093e89d6c7ae1f6c99a1ce97da9c87`
- formal label: `R20R3_CANDIDATE_NUMERICS_NOT_QUALIFIED`

## Accepted facts

Profiler repair and stage selection succeeded:
- cumulative eligible-stage GPU time:
  - update-gradient incremental = 1024.802 us
  - line-search = 663.618 us
  - constraint update = 384.925 us
- selected stage: `_update_gradient_incremental`
- one fixed candidate: online ascending active-world IDs + 304 workers
- OFF and list canaries passed

At first real candidate entry t128:
- B0 and S1 each pass parent-reference effective-output gates
- paired nefc exact
- paired outer solver_niter exact
- paired non-LS status exact
- qacc/qfrc_constraint/efc.Ma/valid-efc.force per-world and global-RMS screens pass
- qfrc source relation passes
- model-improvement residual gate passes

The only failed gate is the historical final-gradient residual envelope.

Important:
- S1 exceeds the pre-frozen historical B0 gradient envelope in 10 worlds
- the paired fresh B0 itself exceeds the same envelope in 11 worlds
- thus the failure cannot be attributed specifically to S1
- no performance timing was run

## Source semantics review

Pinned solver source uses `ctx.grad_dot` and `ctx.newton_decrement` inside `_solve_done` to decide the current outer-iteration completion predicate.

For Newton, the source completion rule is:
- alpha == 0
- OR positive improvement < tolerance
- OR gradient < tolerance
- OR model_improvement < tolerance
- OR, separately, outer solver iteration limit is reached

The old R20R1 contract itself already states that graph-end gradient/model-improvement values are residual diagnostics and are not guaranteed to encode the exact stop-time predicate in all cases.

After a world is done, later update-gradient paths skip it through `ctx.done`; the final graph-end residual arrays are SolverContext diagnostics and are not public physical outputs consumed by the integrator.

Therefore:
- exact outer solver_niter and done semantics are more direct stop-behavior evidence than matching a historical maximum final-gradient value;
- the old historical-max + tolerance envelope requires separate B0-only stability/semantic review before being used to reject S1;
- this does not retroactively change R20R3P1, whose frozen gate correctly forced STOP.

## Recommended next round

`R20R3P2_RESIDUAL_CONTRACT_REQUALIFICATION_AND_RESUME`

This must be a new experiment.

Contract derivation must not use prior S1 residual values to choose thresholds.

Allowed evidence for the new residual contract:
1. pinned source completion predicates;
2. fresh B0-only repeats on the four frozen discovery entries;
3. directed offline negative controls;
4. exact outer niter/done/status/coverage plus existing effective-output numerical screens.

Preferred replacement:
- verify source-semantic completion consistency per world rather than historical-gradient-value equality;
- keep final gradient/model-improvement as reported diagnostics unless source-semantic inconsistency appears;
- keep outer ITERATIONS as explicit hard status;
- do not call limit-stopped worlds converged.

If no B0-only source-grounded, discriminative replacement can be frozen:
`R20R3P2_RESIDUAL_CONTRACT_NOT_QUALIFIED`
STOP and close current R20 performance attempt.

If it qualifies:
- reuse exactly the already-selected incremental-gradient stage;
- reuse exactly the same candidate patch and 304-worker rule;
- no stage/profile/worker reselection;
- rerun candidate correctness on all four discovery entries;
- if correct, automatically resume the original formal complete-solver timing and conditional holdout.

No 174/hardware admission follows automatically.
