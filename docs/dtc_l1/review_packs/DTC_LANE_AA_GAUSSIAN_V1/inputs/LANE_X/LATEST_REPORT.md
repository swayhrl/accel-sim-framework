# DTC Lane X opt-in invalidation V1

2026-10-17, Asia/Shanghai. Goal: `DTC_LANE_X_OPTIN_INVALIDATION_IMPLEMENTATION_174_V1`.

**SCIENTIFIC_STOP_SOURCE_EVENT_CONTRACT_MISMATCH. K1 is not implemented and
has no correctness PASS.** This is the user's explicitly requested scientific
STOP, not a claim that safe lookup invalidation is inherently impossible.

## Source finding and STOP

The frozen source describes `-gpgpu_flush_l1_cache` as a kernel-end flush, but
the actual predicate is per-cluster idleness on every CORE tick. See
`gpu-sim.cc:2515-2527`: CTA issue and latency decrement precede the loop;
`gpgpu_flush_l1_cache && cluster.get_not_completed()==0` triggers that cluster's
ordinary invalidate. The loop neither tests a unique kernel completion event
nor requires every other cluster to finish. Repeated idle-cluster calls are
possible. These are source-derived possibilities, not observed benchmark
event counts. No Gaussian/GEMM event trace or performance run was dispatched.

The ordinary path also has MEMBAR-release and cache-preference-change callers.
The former checks one warp's scoreboard plus the existing flush flag; the
latter does not check that flag. A shared unconditional DTC hook would include
all of them. This scope cannot silently be called kernel-end-only.

There is also a request/commit distinction: `baseline_cache::invalidate()`
sets `m_invalidate_pending`; `retire_pending_invalidate()` performs conventional
Tag invalidation only after the existing conventional miss lifecycle drains.
An LD/ST hook at request time is not necessarily an actual Tag-commit hook.
No new delay, global drain/reset, conventional-cache change, weakened assertion,
or invented kernel event is used to conceal this distinction.

## Work delivered

Core branch: `hrl/iscas2027-dtc-lane-x-invalidate-optin-core-174-v1`, based exactly
on `6fba0136f8465b59fe5858a950fa39efb265f654`. Its only delta is a scientific STOP
note; simulator, parser, tests, configuration, workloads and traces are unchanged.
No `-gpgpu_dtc_l1_invalidate_on_source_event` option is registered; neither K0
nor K1 with that new option is an executable feature on this branch.

Framework branch: `hrl/iscas2027-dtc-lane-x-implementation-174-v1`, based on
`f5c37d6edcce832a72cb0830021bffa78df6cc13`. Only this review pack is added.
Both worktrees are independent. Original frozen worktree, old build products,
other Lane worktrees and result directories are not modified. No other Lane's
source or results are used as validation evidence.

Core documentation SHA: `f8b34dd7a738caddf4f23dd417e34c0b63c206d9`; pushed and
fetched back with an exact match. The independent baseline build completed,
and all four existing CMake directed regressions passed (4/4, 0 failures).
Exact results are recorded in `SOURCE_AND_BINARY_IDENTITY.json` and
`CORNER_CASE_CHECKS.json`.
Their status is separate from the K1 checks, all of which remain NOT_RUN after
STOP. See those JSON files for exact results and hashes; no baseline test
is relabeled as an invalidation test. Raw build/test logs remain in the new
Lane X evidence directory and are not committed.

## Deliverables and required next gates

- `CORE_DELTA.patch`: complete documentation-only Core delta; zero behavior delta.
- `SOURCE_AND_BINARY_IDENTITY.json`: exact independent baseline source/build identity.
- `SOURCE_EVENT_AUDIT.json`: source-only event evidence and limits.
- `DEFAULT_OFF_EQUIVALENCE_PLAN.md`: future K0 equivalence protocol, not a PASS.
- `FLUSH_STATE_TRANSITION.md`: source timeline and required conservation contract.
- `CORNER_CASE_CHECKS.json`: baseline results and unexecuted K1 checks.
- `GIT_DELIVERY.json`: pushed commits and fetch-back evidence.

Before resuming implementation, resolve the event contract against these exact
source sites: request versus conventional commit; idle-cluster repetitions;
MEMBAR and preference-change scope; applicable original guards. External Lane V
source contract is required and has not been consumed here. Lane Y independent
validation of any later executable implementation is also required and is not
present. Neither gate is waived by the baseline regression or this STOP report.
Full performance matrices are OO-only after both gates. IO stays unimplemented
if implementing ownerless invalidation would expand its passive-release
mechanism. No full Gaussian/GEMM simulation is authorized by this review pack.
