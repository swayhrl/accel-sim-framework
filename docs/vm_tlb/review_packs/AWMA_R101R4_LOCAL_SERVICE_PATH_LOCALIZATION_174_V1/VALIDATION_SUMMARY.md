# Validation summary

## P0 finite pre-L1 service

- 22/22 finite-policy directed assertions passed.
- 22/22 source integration checks passed.
- Three accepted VM regressions and inherited transient/O2 helper regressions
  passed.
- Default-absent and explicit-none runs reproduced the accepted small T2
  signature exactly: 93,079 cycles, 43,357,696 instructions and 1,216 CTAs.
- The positive six-kernel integration completed 6/6 kernels, exercised LDG,
  LDGSTS and WRITE, observed maximum scheduled/ready depths 1/1 and fully
  drained.
- Formal CONTEXT2 completed rc=0 with empty stderr and 55/55 gates passing.

## P1 post-L1 local service

- 22/22 finite-policy directed assertions passed.
- 23/23 placement/integration checks passed, including the L1D-instance gate,
  normal L1 lookup,
  MSHR/fill re-entry, hit bypass and finite backpressure.
- Three accepted VM/cache regressions and inherited helper regressions passed.
- Default-absent and explicit-none runs reproduced the accepted small T2
  signature exactly.
- The positive six-kernel integration completed 6/6 kernels, exercised 912
  qualified reads and 96 writes after normal L1 miss handling, observed
  maximum scheduled/ready depths 1/1 and fully drained.
- A formal-input engineering attempt exposed that the initial hook was in the
  generic `baseline_cache::cycle` without an L1-instance guard.  The attempt
  deadlocked at kernel4 and is retained as failed engineering evidence.  After
  adding `m_level == L1_GPU_CACHE`, a bounded six-kernel diagnostic containing
  the formal XXT kernel completed rc=0, 6/6 coverage, 811,008 legal P1 writes,
  maximum depths 1/16 and terminal quiescence.

The formal P1 CONTEXT2 result and its gate count are recorded in
`P1_CONTEXT2_RESULTS.tsv` and `RUN_RECEIPTS.json` after immutable-run
postprocessing.  No FULL5, H1, parameter sweep, Native run or new capture is
part of this stage.

## Formal closure

- P0 CONTEXT2: rc=0, stderr=0, exact context, 55/55 gates PASS.
- P1 CONTEXT2: rc=0, stderr=0, exact context, 57/57 gates PASS after the
  documented postprocess-only recovery; simulator raw was not rerun or changed.
- Both formal runs: six exact trace members, untranslated=0, unobserved=0,
  duplicate=0, exactly-once completion and terminal quiescence.
- Forbidden/untriggered work: 109, FULL5, H1, queue sweep, Lane F and Lane G
  were not run.
