# Default-OFF equivalence plan

Status: `PLAN_ONLY_K1_NOT_IMPLEMENTED_SCIENTIFIC_STOP`.

The current Core delta is documentation only. It establishes source equality
of executable inputs, not runtime K0/K1 equivalence of a future feature. The
proposed option does not exist yet; do not pass it to this baseline binary.

After resolving the source-event contract, use a separately reviewed
`OPT_BOOL` option `-gpgpu_dtc_l1_invalidate_on_source_event` with parser default
`0`, if compatible with the production parser. Test the production parser with
the option omitted, explicit `0` and explicit `1`; reject unsupported modes
explicitly rather than implying that a no-op mode implements K1. No performance
threshold, workload identity, or posterior target enters option semantics.

1. Freeze the new Core SHA, Framework harness SHA, complete configuration,
   compiler, linked binary hashes and workload/input identity before execution.
   Record own worktree cleanliness and source hashes again afterwards. Do not
   inspect another Lane's changing source/results to construct identity.
2. Build the frozen anchor and implementation separately with matching compiler
   options and assertions enabled. Never reuse or overwrite an old binary or
   build tree. The current Lane X baseline build has a distinct directory.
3. Run existing directed regressions, then tiny deterministic CPU production-
   interface tests for absent/0/1 parser behavior and event paths. Include
   ordinary event disabled, event guard false, repeated idle-cluster events,
   request/commit separation, MEMBAR and preference-change scope. A mock-only
   predicate test cannot establish production-path correctness.
4. For omitted/0, require identical architectural completions, simulated cycles,
   every legacy mechanism counter, lower traffic, dependencies, Ref and credit
   conservation against the frozen baseline. Compare stdout after removing only
   documented source/build identities, wall time and host throughput fields.
   Do not ignore unexplained legacy counter differences. Test LEGACY,
   PAPER_BASE, PAPER_IO, PAPER_OO and MODERN_OO_SECTOR for unchanged K0 behavior.
5. For 1, require the exact approved event guards; no event means no mutation.
   Preserve in-flight identities, return-sector ownership, pending metadata,
   collection state, retirement width, service quotas, PIB and capacities.
   Verify the cases in `CORNER_CASE_CHECKS.json` before any formal simulation.
6. Gate later runs on the external Lane V immutable source contract and Lane Y
   independent validation, recording each reviewed SHA and outcome. This window
   provides neither. Complete performance matrices are for OO only. Do not run
   complete Gaussian/GEMM simulations in this window.

Controls must differ only in the new option. Existing flush flags stay fixed.
No kernel extension/shortening, conventional-cache rewrite, finite-service quota,
PIB, physical capacity, clock, global lower cap, trace or workload change is an
equivalence remedy. Preserve previous accepted evidence with its old identities.
