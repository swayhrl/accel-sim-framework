# Codex Goal — Lane F / node109
## AWMA R20R2 t152/world413 line-search semantic-materiality diagnostic V1

Date: 2026-10-01

Repository:
`swayhrl/accel-sim-framework`

Execution branch:
`hrl/awma-r20r2-linesearch-semantic-materiality-109-v1`

Scientific parent:
`8a1a8baf6ac5b6eff0c32f04b572eb1d34873d24`

Stage:
`AWMA_R20R2_LINESEARCH_SEMANTIC_MATERIALITY_109_V1`

This Goal is correctness/semantics only.

It must not run the active-world performance candidate.
It must not time B0/S1.
It must not change `ls_iterations`, solver tolerance, scene, batch, precision, contact ordering or solver algorithm.

---

# 0. Frozen authority

Reuse exactly:

- MuJoCo Warp source:
  `3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`
- solver.py blob:
  `090061796792f4d11408eaa69b4ef3c44465c705`
- RTX4080 / SM89
- B=1024
- G1 hfield / shuffle_dance authority inherited from R20/R20R1
- R2 continuous B0 lineage
- exact t152 solver-entry:
  `42e23fbdbb9aaae0dcbeacaa0e7ae278c1728bd9ff3a2881c8410e4f81f98e87`
- target world:
  `413`
- target world nefc in parent:
  `46`
- target world solver_niter in parent:
  `8`
- frozen local numerical contract SHA:
  `456ca1fa3cbca9aa8d4a6c1cae14ea85a176f23660c9d0c8754a141eb70af66d`

Parent raw/review pack is read-only authority.
Do not regenerate a different t152 entry because the target flip is inconvenient.

All CUDA operations use:
`/data/c16/locks/c16_gpu_campaign.lock`

---

# 1. Source-semantics audit first

Before any new GPU run, bind the exact source facts in `SOURCE_SEMANTICS.md`.

Verify from pinned source:

1. `OverflowType.LS_ITERATIONS` means line-search iteration limit reached.
2. In the iterative line-search kernel, qacc / efc.Ma / Jaref are updated using the chosen alpha before thread 0 ORs the LS_ITERATIONS bit when `ls_converged` is false.
3. The bit is written to `d.overflow`.
4. Search all fixed-source readers of `d.overflow` and classify:
   - diagnostic / reporting;
   - capacity/error accumulation;
   - actual numerical-control input.
5. Verify whether any solver/integrator path consumes LS_ITERATIONS to alter later arithmetic.
6. Record that the official G1 benchmark descriptor masks ITERATIONS and LS_ITERATIONS from `warn_overflow`; do not interpret that mask as proof the bit is numerically meaningless.

If source shows LS_ITERATIONS directly changes subsequent numerical control in the fixed path, record that and keep the parent exact-signature requirement as presumptively semantic. Continue only to localize the observed flip; do not weaken the gate.

---

# 2. Build one opt-in observer, default OFF

The observer must be a diagnostic-only source patch, isolated from the pinned checkout.

Requirements:
- default OFF reproduces parent B0;
- no change to solver math, tolerances, iteration counts, block size, algorithm or data ordering;
- no per-line-search host read;
- write to preallocated GPU arrays and copy out only after the complete solver replay;
- target world 413 only to minimize perturbation;
- no timing claim while observer is ON.

Record, for each outer solver iteration reached by world413 and each line-search iteration actually evaluated:

### Entry state
- outer solver iteration index
- nefc
- search_dot / search norm
- tolerance / ls_tolerance
- gtol
- gtol_accept
- noise_floor if applicable
- p0 cost / derivative / curvature
- lo_alpha_in
- initial lo_in cost / derivative / curvature
- initial_converged

### Per inner line-search iteration
- iteration index
- lo_alpha / hi_alpha before update
- candidate lo_next_alpha / hi_next_alpha / mid_alpha
- lo_next / hi_next / mid cost, derivative and curvature
- conv_lo / conv_hi / conv_mid
- swap_lo / swap_hi
- each ls_done component if practical
- selected best alpha / improvement after that iteration
- whether the loop breaks

### Exit
- final ls_converged
- final alpha
- final improvement
- LS_ITERATIONS bit written or not
- solver_niter
- outer done state
- relevant qacc / qfrc_constraint / efc.Ma / valid efc.force checksums or world-local numerical summary.

If logging every scalar would materially alter register pressure or liveness, reduce to the smallest set that still distinguishes the exact convergence predicate and selected alpha. Document the reduction before using data.

Observer OFF must pass a small exact regression:
- same t152 entry;
- same source/options;
- existing parent local numerical validator;
- no new stop-signature behavior introduced by the OFF path.

If OFF is not baseline-equivalent:
`R20R2_OBSERVER_NOT_QUALIFIED`
STOP.

---

# 3. Capture the phenomenon under observation

Use the exact frozen t152 entry.

Do not tune input or reselect a world.

Run observer-ON same-graph B0 replays until:
- both LS_ITERATIONS outcomes have been captured for world413, or
- 16 valid repeats are complete.

If only one outcome appears after 16 valid repeats, continue up to a hard maximum of 32 total observer-ON same-graph repeats.

This is a bounded correctness campaign, not performance sampling.

For every repeat require:
- exact same solver-entry hash;
- nefc=46 for world413;
- solver_niter=8 unless the replay itself demonstrates a new unresolved baseline problem;
- parent floating local contract remains satisfied;
- no new capacity overflow or NaN/Inf.

If both flag outcomes are not captured by 32 observer-ON repeats:
- compare observer-ON distributions with the accepted parent 1/5 flip;
- run at most 4 fresh-capture observer-ON repeats from the same frozen entry to test graph-reuse sensitivity;
- if still no pair, use:
  `R20R2_FLAG_OUTCOME_PAIR_NOT_CAPTURED`
  and STOP.

Do not change observer, block size, seed, tolerance or ls_iterations just to reproduce both outcomes.

---

# 4. Rule out trivial hidden-state packaging errors

Only if evidence suggests unclosed graph-local state, do one bounded scratch audit.

Audit the exact arrays in SolverContext that can affect:
- line-search Jaref / jv / quad
- search direction / search_dot
- alpha / improvement
- ls_exhausted
- done / state_changed_count
- any incremental fast-path reuse.

Determine for each:
- initialized from deterministic input;
- zeroed/overwritten before read in every solve;
- reused across outer iterations by design;
- potentially read before write / capture-owned state.

Do not add clears to the baseline merely to force determinism.

If a real read-before-write or unclosed scratch dependence is found:
`R20R2_LINESEARCH_HIDDEN_STATE_UNRESOLVED`
STOP with exact source/field evidence.

A debug-only forced-clear experiment is allowed only as a non-performance canary after the dependency is identified, and must not be relabeled as the accepted B0.

---

# 5. Classification

Use the parent local floating contract unchanged.

Do not retroactively change R20R1.

## A. R20R2_LINESEARCH_DIAGNOSTIC_THRESHOLD_ONLY

Use only if the set-bit and clear-bit replays show:

- identical frozen solver entry;
- identical nefc and outer solver_niter;
- same constraint coverage;
- all final solver outputs satisfy the already-frozen local numerical contract;
- the difference is localized to one or more line-search convergence predicates near their threshold / iteration limit;
- selected alpha/improvement and downstream solver state remain within the established B0 numerical envelope;
- fixed-source audit finds no downstream numerical-control use of the LS_ITERATIONS bit itself;
- no hidden-state packaging error is required to explain the result.

Interpretation:
the exact LS_ITERATIONS bit is a diagnostic limit-status boundary, not by itself a valid future B0/S1 numerical-equivalence gate for this solver-entry study.

This does **not** authorize active-world performance automatically; it makes a new contract proposal review-ready.

## B. R20R2_LINESEARCH_NUMERIC_PATH_MATERIAL

Use if the flag outcome corresponds to a materially different line-search/solver path beyond the parent local contract, for example:
- different outer solver_niter;
- selected alpha/improvement diverges materially and propagates;
- qacc/qfrc/efc outputs exceed the frozen local contract;
- downstream numerical behavior depends on the bit/path.

Interpretation:
the current R20 active-world performance line remains blocked by solver numerical instability.

## C. R20R2_LINESEARCH_HIDDEN_STATE_UNRESOLVED

Use if the same frozen entry depends on graph-local state/read-before-write behavior that cannot be closed without modifying baseline semantics.

## D. R20R2_FLAG_OUTCOME_PAIR_NOT_CAPTURED

Use if the accepted parent flip exists but this bounded observer campaign cannot capture both outcomes cleanly.

## E. R20R2_OBSERVER_NOT_QUALIFIED

Use if the observer itself cannot be shown baseline-neutral enough for semantic diagnosis.

No other positive label is allowed.

---

# 6. If A is reached, freeze a future contract proposal — but do not run S1

Create:
`FUTURE_ACTIVE_WORLD_NUMERICAL_CONTRACT_PROPOSAL.md`

It may propose:

Exact gates:
- solver-entry identity
- nefc / constraint coverage
- solver_niter
- true capacity-overflow bits
- no NaN/Inf
- existing frozen floating output contract
- any source-justified residual checks

Reported-but-not-hard-gate:
- LS_ITERATIONS bit by itself, only if R20R2 class A is established.

The proposal must explicitly distinguish:
- capacity overflows
- outer solver iteration limit
- line-search iteration-limit diagnostic
- mathematical convergence claims.

Do not edit R20R1's historical contract.
Do not execute active-world candidate in this Goal.

---

# 7. Forbidden

Do not:
- modify `ls_iterations=20`;
- change tolerance / ls_tolerance;
- change solver, cone, sparse mode, batch, scene or precision;
- sort/canonicalize data fed to solver;
- drop world413;
- select another step because it is easier;
- run active-world S1;
- run formal performance timing;
- run NSYS, NCU, NVBit, SASS or Accel-Sim;
- start node174 work;
- design hardware.

No new RL/policy workload.

---

# 8. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R20R2_LINESEARCH_SEMANTIC_MATERIALITY_109_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- PARENT_AUTHORITY.json
- SOURCE_SEMANTICS.md
- OBSERVER_CONTRACT.md
- OBSERVER_OFF_REGRESSION.json
- T152_REPEAT_SUMMARY.tsv
- WORLD413_LINESEARCH_TRACE_SUMMARY.md
- WORLD413_LINESEARCH_TRACES.json or indexed raw equivalent
- SCRATCH_AUDIT.md if triggered
- FUTURE_ACTIVE_WORLD_NUMERICAL_CONTRACT_PROPOSAL.md only if class A
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Large raw stays on node164.

---

# 9. Closure

Publish one exact commit.
Push/fetch-back verify commit and tree.
Release GPU lock.
Exit all campaign GPU processes.
Clean worktree.
STOP.

Final report should state in Chinese:
- whether both flag outcomes were captured;
- what exact line-search predicate differed;
- whether final solver numerics materially differed;
- whether LS_ITERATIONS is semantic, diagnostic-only under this scope, or unresolved;
- whether a future active-world contract is review-ready.

Do not summarize this Goal as an active-world performance result.
