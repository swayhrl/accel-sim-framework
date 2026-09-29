# Engineering fixes

All fixes remained inside the R101R4 execution workspace/runtimes and did not
change accepted comparator data or trace bytes.

1. The inherited P0 positive-smoke validator contained two S1-specific output
   expectations.  The validator was corrected after the successful simulator
   run and the immutable log was revalidated; no scientific input or simulator
   source changed and no rerun was needed.
2. P1 initially sampled ready depth only after same-cycle delivery, which made
   the observational maximum appear as zero.  Sampling was moved to the actual
   READY enqueue boundary.  The isolated P1 runtime was rebuilt and the full
   P1 qualification suite was rerun before formal execution.
3. A missing `apply_patch` convenience command on 174-new was installed as a
   thin `git apply --whitespace=nowarn` wrapper for review-pack editing.  It
   has no simulator/runtime role.
4. The first P1 formal attempt completed the exact three-kernel context and
   then deadlocked early in kernel4.  Source audit showed that interception in
   generic `baseline_cache::cycle` lacked an L1-instance guard, allowing
   non-L1 cache miss queues to be misrouted.  Adding the exact
   `m_level == L1_GPU_CACHE` gate restores the intended post-L1D-only scope;
   it changes no queue size, latency, service policy or accepted comparator.
   The rebuilt binary was fully requalified and passed a bounded formal-XXT
   liveness diagnostic before the complete formal rerun.
5. The complete repaired P1 simulator run finished rc=0 with immutable 6/6
   evidence, but the formal-at-run summarizer required both nonzero LDGSTS
   local service and nonzero L1 pending-hit telemetry.  Neither is a
   preregistered outcome gate; both observed values are legitimately zero.  A
   hash-bound postprocess-only recovery replaced these assumptions with
   presence/accounting checks, changed no simulator raw, and closed 57/57
   gates without a simulator rerun.

These are engineering corrections, not additional candidate points.  Failed
or superseded evidence is not promoted as a scientific result.
