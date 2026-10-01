# R20 final closure after R20R5

Date: 2026-10-02

Execution authority:
- branch: `hrl/awma-r20r5-hybrid-native-109-v1`
- commit: `57ffbd4a8c8fedb1f050913bd2801c76eb1a4e7c`
- tree: `45c273a8bab7c51ba77d7417bf6ef64fcda3fe05`
- formal label: `R20_ACTIVE_WORLD_LINE_CLOSED_HYBRID_NUMERICS_NOT_QUALIFIED`

## Accepted R20R5 facts

The final source-derived hybrid was implemented cleanly.

Hybrid semantics:
- current device `nsolving > 304`:
  - execute original baseline `_update_gradient_incremental`
  - do not build active-ID list
- current device `nsolving <= 304`:
  - build ascending IDs from current `ctx.done`
  - execute the already-frozen 304-worker H-update / blocked-Cholesky worklist path

No host per-iteration branch decision, future niter, threshold tuning, worker tuning, second stage or second queue was used.

Qualification before formal timing:
- nested device conditional canary PASS
- branch canaries at 1024 / 305 / 304 / 1 / 0 PASS
- four OFF regressions PASS
- four B0/H1 complete-solver correctness checks PASS
- online branch traces match actual active-count transitions

Thus the hybrid implementation itself was technically and numerically qualified before timing.

## Formal timing stop

The formal contract required all 120 formal samples to independently pass the semantic gates.

The first 90 formal samples passed.

The next formal sample:
- group 2
- t136
- arm = B0
- formal repeat 0

failed:
- exact per-world `solver_niter`

while:
- `nefc` remained exact
- source-stop consistency still passed

The failure happened on the baseline arm, not H1.

The failed output arrays were not retained, so the differing world and exact cause remain unknown.

Consequences:
- no complete valid three-group aggregate exists;
- no measured hybrid speedup or slowdown is scientifically admissible;
- holdout stays sealed;
- the failure must not be attributed to H1.

## Why R20 closes here

R20R5 was preregistered as the final active-world runtime candidate.

The project had already bounded the search space through:
1. real active-world shrinkage discovery;
2. local solver-entry numerical qualification;
3. LS_ITERATIONS semantic isolation;
4. deterministic stage selection from one B0 profile;
5. one always-worklist 304-worker candidate;
6. source-semantic residual-contract repair;
7. complete-solver negative for the always-worklist candidate;
8. CPU-only late-phase oracle;
9. one final source-derived 304-threshold hybrid.

Opening another qualification/retry solely because the final formal B0 happened to change outer niter would create another post-result admission cycle for the same candidate and violate the no-rescue boundary.

Therefore R20 is closed even though the final hybrid did not receive a valid performance verdict.

## Final scientific interpretation of R20

Supported:

1. **Natural solver-tail heterogeneity is real** on this public G1 replay.
   Worlds finish at different outer solver iterations and the active set shrinks substantially.

2. **The original full-world launch organization continues to pay repeated stage launch geometry after many worlds are done.**
   This is a real execution-organization phenomenon.

3. The fixed always-worklist 304-worker software organization is a valid measured negative:
   - numerically qualified
   - complete-solver timing qualified
   - ~66.6% slower than baseline

4. A late-only targeted oracle shows nontrivial ideal headroom:
   - O2 = 11.77% complete-solver zero-overhead upper bound
   - this is not measured speedup

5. The only source-derived final hybrid was technically implementable and passed pre-timing correctness.

Not supported:

- a valid measured performance result for the final hybrid
- whole physics-step speedup
- RL training speedup
- hardware headroom
- a claim that every active-world organization is slower
- a claim that active-world scheduling is generally ineffective

## Methodological conclusion

The line is closed because the bounded software exploration did not produce a reproducible material complete-solver win under a clean final performance contract.

This is stronger than a simple negative benchmark result:
- the phenomenon exists;
- an obvious worklist mapping is strongly negative;
- a structurally motivated hybrid remains unmeasured due baseline semantic instability during formal repetition;
- further rescue work would exceed the project's bounded-search rule.

## Project state

R20 active-world line:
`CLOSED`

Do not reopen via:
- worker sweep
- threshold sweep
- second stage
- alternate queue/worklist
- timing restart on the same hybrid
- relaxed outer-niter contract
- holdout
- 174 / Accel-Sim
- hardware mechanism

A future independent project may revisit GPU batched-physics dynamic work scheduling only with:
- a new research question,
- a new contract,
- and independent workload evidence.

It should not be treated as continuation of R20.

Recommended AWMA next action:
return to the broader phenomenon-discovery frontier and select a new candidate/problem, carrying forward the R20 lessons about numerical-contract stability, software-organization baselines and ideal-headroom screening.
