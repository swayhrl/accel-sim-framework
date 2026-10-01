# R20R1 review after t152 LS_ITERATIONS stop

Date: 2026-10-01

Execution authority:
- branch: `hrl/awma-r20r1-solver-entry-local-contract-109-v1`
- commit: `8a1a8baf6ac5b6eff0c32f04b572eb1d34873d24`
- formal label: `R20R1_SOLVER_BASELINE_NOT_QUALIFIED`

## Accepted R20R1 facts

The real solver-entry isolation succeeded.

The predeclared four-entry B0 qualification:
- t128 PASS
- t136 PASS
- t144 PASS
- t152 FAIL only because one of five same-input replays newly set `LS_ITERATIONS` for world 413

For the t152 failing world:
- entry LS_ITERATIONS bit = clear
- 4/5 exits LS_ITERATIONS bit = clear
- 1/5 exits LS_ITERATIONS bit = set
- nefc = 46 in all compared runs
- solver_niter = 8 in all compared runs
- floating qacc/qfrc/etc remain inside the pre-frozen local numerical contract

Thus the authorized R20R1 exact stop-signature gate correctly fails.
No S1 or performance conclusion exists.

## Source semantics of LS_ITERATIONS

Pinned source:
`google-deepmind/mujoco_warp@3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`.

In the iterative line-search kernel:
1. the kernel evaluates/brackets candidate alphas for up to `ls_iterations`;
2. it maintains the best improved alpha/improvement;
3. after the search loop, it updates qacc, efc.Ma and Jaref using that alpha;
4. only afterward, thread 0 writes improvement/alpha and, when `ls_converged` is false, ORs `OverflowType.LS_ITERATIONS` into d.overflow.

Therefore the flag says:
> the line-search convergence rule did not fire before the configured iteration limit

It does not by itself say:
> solver_niter changed, constraints changed, or the chosen final numerical state is invalid.

The source search in this fixed tree found `d.overflow` used as an output/status accumulator and by benchmark error reporting. No solver/integrator path was found that consumes `LS_ITERATIONS` as an input to alter qacc integration or subsequent solver arithmetic.

The G1 benchmark descriptor explicitly applies:
`opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS`.

The testspeed path masks reported overflow with `warn_overflow`, so this benchmark configuration does not treat these two bits as fatal benchmark errors.

Important:
- this does not mean the bit is semantically meaningless;
- it records failure of a numerical line-search criterion;
- R20R1 was correct to require exactness under its frozen contract;
- we must not retroactively relax R20R1.

## Scientific interpretation

The current evidence is narrower than "solver baseline is generally nondeterministic".

Three of four predeclared real solver entries qualified fully.

At t152, a single world on a single repeat crossed a line-search convergence/limit boundary while:
- nefc stayed exact;
- outer solver_niter stayed exact;
- output floating values stayed inside the independently frozen local contract.

This is consistent with a reduction/rounding-sensitive line-search threshold or graph-local scratch sensitivity, but the internal cause is still UNKNOWN.

## Recommended next step — not automatically authorized

`R20R2_LINESEARCH_SEMANTIC_MATERIALITY_DIAGNOSTIC`

Use only the frozen t152 solver entry and world 413 first.

No active-world performance candidate yet.

Instrument the existing line-search path to record, per outer solver iteration for world 413:
- whether line search initially converged
- each iteration's lo/hi/mid convergence predicates
- ls_done reason
- selected alpha and improvement
- gtol and gtol_accept
- p0 / lo-in derivative terms needed to explain the decision
- final ls_converged
- LS_ITERATIONS bit
- solver_niter
- qacc/qfrc outputs

The observer must not change solver math. Prefer writing diagnostics into preallocated arrays; no per-iteration host reads.

First repeat the same frozen t152 B0 enough times to capture both bit outcomes without tuning inputs. Do not change ls_iterations or tolerances.

Then determine whether the bit flip is:

A. `DIAGNOSTIC_THRESHOLD_ONLY`
- same outer solver_niter
- same constraints
- final qacc/qfrc within the existing frozen local contract
- only the exact line-search convergence predicate near its threshold differs
- no downstream path consumes the bit

or

B. `NUMERIC_PATH_MATERIAL`
- alpha/improvement or later solver state diverges in a way that changes a meaningful stop/solution property beyond the existing contract

or

C. `HIDDEN_STATE_UNRESOLVED`
- repeated identical entry still depends on graph-local/unclosed state that cannot be bounded cleanly.

Only case A would justify a **new future contract** in which LS_ITERATIONS is reported but is not an exact equality gate by itself; such a change must be explicitly justified and frozen before any active-world candidate.

Cases B/C close the current R20 active-world line until solver correctness/determinism is independently addressed.

No performance timing, NSYS/NCU, S1, holdout, 174 or hardware work is part of this proposed R20R2 diagnosis.

## Current state

- R20R1: STOP, accepted
- active-world performance: NOT TESTED
- architecture opportunity: UNKNOWN / NOT QUALIFIED
- Lane F: STOP pending explicit R20R2 authorization
- Lane E/G: STOP
- 174/Accel-Sim: STOP
