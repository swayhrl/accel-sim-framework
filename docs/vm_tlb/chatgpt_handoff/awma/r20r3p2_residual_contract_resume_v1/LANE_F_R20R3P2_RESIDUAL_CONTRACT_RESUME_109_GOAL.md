# Codex Goal — Lane F / node109
## AWMA R20R3P2 B0-only residual-contract requalification and automatic resume V1

Date: 2026-10-01

Repository:
`swayhrl/accel-sim-framework`

Execution branch:
`hrl/awma-r20r3p2-residual-contract-resume-109-v1`

Scientific parent:
`53837e8366f0d96a636c89365b782aa411e7bc63`

Stage:
`AWMA_R20R3P2_RESIDUAL_CONTRACT_REQUALIFICATION_AND_RESUME_109_V1`

This is one continuous solve-and-continue Goal.

Order:
1. audit source semantics of final SolverContext residuals and done predicates;
2. derive a replacement B0-only stop-consistency contract from source semantics, not from S1;
3. validate it on fresh B0-only repeats across the four frozen discovery entries plus directed negatives;
4. if the contract qualifies, reuse **exactly** the existing selected stage and 304-worker candidate;
5. rerun candidate correctness on all four discovery entries;
6. if correct, resume the already-authorized formal complete-solver timing and conditional holdout;
7. STOP at the first contract-defined terminal condition.

No new profiler/stage selection/candidate/worker search is authorized.

---

# 0. Frozen authority

Reuse exactly:
- MuJoCo Warp source `3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`
- solver.py blob `090061796792f4d11408eaa69b4ef3c44465c705`
- RTX4080 / SM89
- B=1024
- G1 hfield / shuffle_dance / Menagerie authority
- sparse Newton / pyramidal / conditional graph
- iterations=10
- ls_iterations=20
- tolerance / ls_tolerance unchanged
- exact discovery solver entries:
  - t128 `8f3d7015979e959625f3b1d1cd1efb3fb2dea65b4e07bc9c9f1795b30dccd85d`
  - t136 `07c012c0d17eaba3522bcc35016eff581612c138b7c876dff64455788344e883`
  - t144 `4177e0a8a509608651f85f055877576cd71d3f25a40ab2451f276c9b08cdfda6`
  - t152 `42e23fbdbb9aaae0dcbeacaa0e7ae278c1728bd9ff3a2881c8410e4f81f98e87`
- R20R2 LS_ITERATIONS semantics:
  LS bit is reported but not by itself a hard equality gate
- selected R20R3 stage:
  `_update_gradient_incremental`
- selected candidate:
  exact parent patch, online ascending active IDs, fixed 304 workers.

Parent candidate patch and diagnostic contract are read-only authority.
Do not modify candidate source to pass the new contract.

No NSYS/NCU/NVBit/SASS/Accel-Sim/node174 in this Goal.

---

# 1. G0 — source semantics of residuals and done

CPU/source audit first.

Bind exact source lines/functions for:
- `_update_gradient_zero_grad_dot`
- `_update_gradient_grad`
- `_update_gradient_incremental`
- `_solve_done`
- `_solver_iteration`
- any post-solve use of `ctx.grad_dot`, `ctx.newton_decrement`, `ctx.alpha`, `ctx.improvement`.

Write:
`RESIDUAL_SOURCE_SEMANTICS.md`

Establish explicitly:

For Newton, for an active world at `_solve_done`:
- `solver_niter += 1`
- compute:
  - improvement = rescaled ctx.improvement
  - gradient = rescaled sqrt(ctx.grad_dot)
  - model_improvement = rescaled 0.5*ctx.newton_decrement
- source done predicate:
  - alpha == 0
  - OR (improvement > 0 AND improvement < tolerance)
  - OR gradient < tolerance
  - OR model_improvement < tolerance
- separately, if `solver_niter == iterations`, world is marked done and ITERATIONS bit is written when source done predicate is false.

Verify from source:
- worlds already `ctx.done` are skipped by later gradient/update/done paths;
- graph-end residual arrays for a completed world therefore remain the values associated with its last active solver iteration unless a specific source writer proves otherwise;
- these SolverContext residual arrays are not public physical outputs consumed by the post-solver integrator.

If source contradicts these assumptions, document the exact lifecycle and derive the semantic check from the actual source, without using S1 values.

---

# 2. G1 — proposed replacement contract, frozen before new candidate replay

The old historical residual envelope remains part of R20R1/R20R3P1 history and is not edited.

Create:
`SOURCE_SEMANTIC_STOP_CONTRACT.md`

The new contract must use **no empirical threshold derived from prior S1**.

Hard gates retained unchanged:
1. exact solver-entry / Model / options identity
2. exact world and constraint identity / coverage
3. exact nefc
4. exact outer solver_niter
5. no new true capacity overflow
6. finite qacc/qfrc_constraint/efc.Ma/valid efc.force
7. ctx.done completion semantics
8. unchanged frozen per-world and global-RMS effective-output screens
9. qfrc source relation
10. no stale-output or hidden-state evidence
11. LS_ITERATIONS reported under the R20R2 rule
12. outer ITERATIONS remains an explicit hard status outcome.

Replace only the historical-gradient-value envelope with **source-semantic stop consistency**.

For every world:
- if outer ITERATIONS is newly set at solve exit:
  - require solver_niter == configured iterations;
  - do not claim mathematical convergence;
  - residual values are reported, not required to be below tolerance.
- otherwise:
  - require solver_niter < configured iterations;
  - require at least one actual source done predicate, recomputed from the graph-end state corresponding to the final active iteration, to be true:
    - alpha == 0
    - OR positive improvement < tolerance
    - OR gradient < tolerance
    - OR model_improvement < tolerance.

If source audit shows graph-end values do not faithfully preserve the final active-iteration predicate, add a diagnostic-only observer that records the values **at the moment _solve_done sets done**. The observer:
- default OFF
- preallocated GPU arrays
- no host read inside iterations
- no math/tolerance change
- used for correctness only, never formal timing.

Do not invent a new tolerance multiplier.

The source tolerance remains exactly the configured solver tolerance.

---

# 3. G2 — fresh B0-only qualification

No S1 in this stage.

Use the candidate-capable source tree with candidate OFF.

For each discovery entry t128/t136/t144/t152:
- run 8 independent B0 replays from the exact frozen solver entry;
- restore full input before every replay;
- use identical graph/capture policy;
- collect the revised hard gates plus source-semantic stop consistency.

Eight repeats is fixed before execution; do not extend because a result is inconvenient.

For each entry report:
- solver_niter distribution (must be exact under hard gate)
- ITERATIONS worlds
- LS_ITERATIONS worlds as diagnostic
- count of worlds terminating by each source predicate
- overlaps among predicates
- effective-output screens
- source relation
- any source-semantic stop inconsistency.

B0-only qualification passes only if:
- all 32 replays satisfy all hard gates;
- every non-limit world satisfies at least one source stop predicate;
- all limit worlds have the correct exact outer-limit semantics;
- no hidden-state or stale-output issue appears.

If any B0 replay violates the source-semantic stop contract:
`R20R3P2_RESIDUAL_CONTRACT_NOT_QUALIFIED`
STOP.

No candidate/timing.

---

# 4. G3 — directed offline discrimination tests

Before S1, prove the new contract is not vacuous.

Use copied B0 diagnostic arrays offline or a non-scientific validator.

At minimum construct and verify rejection of:
1. one non-limit world with all four done predicates forced false while ctx.done is marked true;
2. one world with solver_niter decremented to simulate early stop;
3. one missed-constraint / changed-nefc case;
4. one stale qacc/qfrc output case;
5. one false ITERATIONS interpretation (limit bit without niter==iterations).

These are validator negatives, not solver executions.

If the contract cannot distinguish these:
`R20R3P2_RESIDUAL_CONTRACT_NOT_QUALIFIED`
STOP.

If B0-only qualification + directed negatives pass:
freeze:
`R20R3P2_SOURCE_SEMANTIC_CONTRACT_QUALIFIED`

Then continue automatically.

---

# 5. G4 — reuse the exact existing candidate

No new stage selection.
No profiling.
No worker-count change.
No candidate source change except wrapper/observer code required solely to evaluate the new contract.

Reuse:
- selected stage `_update_gradient_incremental`
- ascending active IDs from current ctx.done
- 304 workers
- same two remapped heavy kernels
- same unchanged remaining solver path.

Verify candidate patch SHA/source diff against parent authority before running.

If candidate code identity cannot be reproduced:
`R20R3P2_CANDIDATE_IDENTITY_NOT_QUALIFIED`
STOP.

---

# 6. G5 — four-entry candidate correctness under new contract

For t128/t136/t144/t152:

Run paired B0/S1 correctness from identical frozen entries.

Require all hard gates from Section 2.

For source stop consistency:
- B0 and S1 each independently must satisfy the source-semantic contract;
- do not require gradient/model-improvement scalar equality between B0 and S1;
- exact outer solver_niter remains mandatory;
- if S1 changes which source predicate is true but keeps exact niter/coverage and effective outputs within the frozen contract, record it; do not fail solely on predicate label unless it reflects a materially different propagated path outside the contract.

LS rule remains R20R2:
- bit alone not hard;
- material path/output propagation still fails.

If any entry fails:
`R20R3_CANDIDATE_NUMERICS_NOT_QUALIFIED`
STOP.

No threshold adjustment.

---

# 7. G6 — formal discovery timing if correctness passes

Resume original R20R3 timing exactly.

No profiler.

For each t128/t136/t144/t152:
- B0 candidate OFF
- S1 candidate ON
- 3 paired groups
- 2 warmups/arm/group
- 5 formal samples/arm/group
- alternate order
- exact solver entry restore per sample.

Primary:
`solver input ready -> complete solver.solve outputs committed`

S1 includes active-list/worker/reset/index/sync costs.

Discovery MATERIAL gate unchanged:
1. all four correctness pass
2. all three aggregate groups favor S1
3. median aggregate improvement >=5%
4. gap >3x larger-arm aggregate MAD estimate
5. exact solver work semantics preserved.

Stable <5%:
`R20R3_ACTIVE_WORLD_NO_MATERIAL_GAIN`
STOP.

Mixed:
`R20R3_RESULT_MIXED_NEEDS_REVIEW`
STOP.

No second candidate/worker/stage.

---

# 8. G7 — automatic holdout only for survivor

If discovery MATERIAL, continue automatically.

Use holdout steps:
384, 392, 400, 408.

Generate/freeze all four with original B0 source/control before S1 timing.

Apply the same:
- source-semantic correctness contract
- candidate
- worker count
- formal timing
- >=5% aggregate reproduction rule.

Success:
`R20R3_ACTIVE_WORLD_SOLVER_RESPONSE_REPRODUCED`

Failure to reproduce:
`R20R3_RESULT_MIXED_NEEDS_REVIEW`

No tuning on holdout.

---

# 9. Critical anti-bias rule

Prior R20R3P1 S1 residual values are known and cannot be unseen.

Therefore the new contract is valid only because:
- it is derived from the pinned solver's exact done predicate;
- it introduces no empirical threshold fitted to S1;
- it is qualified on fresh B0-only repeats before any new S1 execution;
- directed negatives prove discrimination.

Do not use:
- prior S1 offending-world count
- prior S1 max gradient excess
- prior S1 gradient distribution
to set any threshold or exception.

If source semantics alone cannot support the replacement, STOP rather than relax the old gate.

---

# 10. Resource limits

This Goal:
- NSYS = 0
- NCU = 0
- NVBit = 0
- SASS = 0
- Accel-Sim = 0
- node174 compute = 0

All CUDA/JIT/capture/replay:
`/data/c16/locks/c16_gpu_campaign.lock`

Large raw -> node164.

No second scene/batch/policy/model.

---

# 11. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R20R3P2_RESIDUAL_CONTRACT_RESUME_109_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- PARENT_AUTHORITY.json
- RESIDUAL_SOURCE_SEMANTICS.md
- SOURCE_SEMANTIC_STOP_CONTRACT.md
- B0_ONLY_RESIDUAL_QUALIFICATION.tsv
- B0_STOP_PREDICATE_SUMMARY.tsv
- DIRECTED_NEGATIVE_VALIDATOR.json
- CONTRACT_DECISION.md
- CANDIDATE_IDENTITY.json if reached
- CANDIDATE_CORRECTNESS.tsv if reached
- DISCOVERY_TIMING.tsv if reached
- DISCOVERY_DECISION.md if reached
- HOLDOUT_INPUT_RECEIPTS.tsv if reached
- HOLDOUT_TIMING.tsv if reached
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Unreached files/stages are marked NOT_RUN.

---

# 12. Closure

Publish one exact commit.
Push/fetch-back verify commit/tree.
Release GPU lock.
Terminate campaign GPU processes.
Clean worktree.
STOP.

Final Chinese report must distinguish:
- old residual envelope failure
- new B0-only source-semantic contract result
- candidate correctness under the new contract
- performance result only if formal timing actually ran
- holdout only if triggered.

Do not describe a contract repair as candidate speedup.
