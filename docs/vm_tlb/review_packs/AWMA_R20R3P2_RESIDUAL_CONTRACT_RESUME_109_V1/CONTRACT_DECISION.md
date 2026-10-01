# B0-only contract decision, frozen before any R20R3P2 S1 replay

`R20R3P2_SOURCE_SEMANTIC_CONTRACT_QUALIFIED`

The old R20R3P1 final-gradient B0-maximum envelope is retained as historical evidence and is **not** widened or rewritten. The prospective replacement checks the exact pinned Newton `_solve_done` predicates at graph end with the original solver tolerance, plus exact limit-stop semantics, while retaining every other frozen effective-output, identity, coverage, niter, status, capacity, finite, done, qfrc-relation and LS diagnostic rule.

Before any new S1 execution, each of t128/t136/t144/t152 had exactly eight full-entry restored B0 replays (32 total). All 32 passed the retained hard gates and source-stop consistency; no extra samples were added. `B0_ONLY_RESIDUAL_QUALIFICATION.tsv` and `B0_STOP_PREDICATE_SUMMARY.tsv` preserve every result and predicate distribution. A CPU-only directed negative validator accepted its unmodified B0 control and rejected all six mutations covering false done, early niter, missed constraint, stale qacc, stale qfrc and false new ITERATIONS status.

The selected candidate is source-identical to accepted R20R3P1 (`868cf9b0420d61656b3698ba7ddc93b6aa3d6a031d825c939a9868adf916a8e3`), with the same `_update_gradient_incremental` stage and 304 workers. This qualification permits the Goal's preregistered four-entry B0/S1 correctness test next. It is **not** a candidate correctness or performance result; R20R3P1's accepted failed label remains untouched.
