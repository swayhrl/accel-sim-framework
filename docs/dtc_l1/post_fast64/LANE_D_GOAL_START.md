# POST-FAST64 Lane D — Goal Start Prompt

Paste the block below into a new Codex window.

```text
START GOAL MODE NOW.

You own POST-FAST64 LANE D — OBSERVER TELEMETRY AND DIAGNOSTIC EXECUTION.

This lane is now scientifically authorized by reviewed Lane B/C gaps. It is no longer speculative instrumentation.

First:
  git fetch origin

Use a separate Framework worktree on:
  hrl/post-fast64-observer-v0

Read and obey:
  docs/dtc_l1/post_fast64/POST_FAST64_MULTI_GOAL_CONTRACT.md
  docs/dtc_l1/post_fast64/POST_FAST64_LANE_HANDOFFS.md
  docs/dtc_l1/post_fast64/LANE_D_OBSERVER_EXECUTION_HANDOFF.md

Frozen accepted FAST64 authority:
  hrl/decoupled-l1-fast64-v0
  18a68dcccd795f1b6cda75504e9450d00c9cee02
  FAST64_COMPLETE_READY_FOR_REVIEW

Reviewed lane inputs:
  Lane A:
    hrl/post-fast64-paper-v0
    c1774a452e244d431c215010b1039e9d3e074f2a

  Lane B:
    hrl/post-fast64-physical-causal-v0
    757b8cbf2c536b04f8a6ef4db847af04f337378d

  Lane C:
    hrl/post-fast64-duplicate-miss-v0
    18800873478576309b08b538974c3872fc2cb6df

Fetch/read those exact handoffs before implementation. Do not copy stale local versions over them.

Formal Core parents:
  non-2D Core95:
    95ccdb7a056f2d53f740d90869785cac6d4ee0f5

  2D Core658:
    6587238c60214d99491f4048e28ce8a3458c1509

Create/use isolated diagnostic Core branches/worktrees only:
  hrl/dtc-l1-post-fast64-observer95-v0
  hrl/dtc-l1-post-fast64-observer658-v0

Never modify the formal Core95/Core658 branches.
Never modify the completed FAST64 branch/results.
Every new simulator row is:
  POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT

============================================================
D0 — AUTHORITY / COVERAGE FREEZE
============================================================

Bind the exact FAST64/A/B/C commit identities above.
Read:
  Lane-B PHYSICAL_POOL_CAUSAL_HANDOFF.md
  Lane-B LANE_D_TELEMETRY_REQUIREMENTS_FROM_LANE_B.md
  Lane-C DUPLICATE_MISS_HANDOFF.md
  Lane-C DUPLICATE_MISS_SOURCE_SEMANTICS.md

Inventory existing post-FAST64 live/terminal rows.
Do not duplicate exact telemetry work.
Produce a compact D0 authority/coverage manifest.

============================================================
D1 — FREEZE OBSERVER SEMANTICS
============================================================

Implement only telemetry that closes a named unresolved question.

Required families:

1. IO/OO alloc -> ready latency:
   count / sum_cycles / max_cycles
   keyed by exact physical {id,generation}.

2. IO/OO pending Tag eviction count:
   increment only when a valid Tag is replaced while its physical allocation
   is still not ready.

3. IO pending-Tag-eviction -> original response latency:
   count / sum_cycles / max_cycles.

4. OO deferred Tag eviction -> final-reference reclaim latency:
   count / sum_cycles / max_cycles.
   Immediate zero-ref reclaim is excluded.

5. OO duplicate-after-eviction:
   exact observer analogue of the already source-proven IO definition.
   Count only a successful same-line NEW_MISS created before the original
   pending allocation completes after its Tag was evicted.
   Do not count pending hits, post-response reaccesses, allocation retries,
   or stale/recycled identities.

6. Exact time-integrated physical / in-flight exposure:

   observer_sample_sm_cycles
   physical_allocated_line_cycles
   physical_full_sm_cycles
   inflight_request_cycles

   Sample only at a source-proven once-per-active-SM simulation-cycle hook.
   If ldst_unit::cycle() is not exactly such a hook, find the correct hook.
   Do NOT mislabel opportunistic samples as SM-cycle integrals.

Derived later:
   avg physical occupancy
   pool-full fraction
   avg lower in-flight requests per SM

Optional lower-create/lower-issue queue integrals are allowed only if source
inspection shows they are low-risk and directly needed.

Observer state MUST NEVER affect:
  lookup
  victim choice
  allocation/free selection
  admission
  retirement
  reclaim
  lower scheduling
  completion
  assertions
  simulator termination

Document exact event/key/cleanup/unit semantics before using data.

============================================================
D2 — IMPLEMENT + DIRECTED TESTS
============================================================

Implement on isolated Core95 observer branch first.
Port the same observer-only patch to Core658 only when 2D telemetry is needed.

Required OO duplicate tests:
  positive pending-evict -> same-line NEW_MISS-before-completion => +1
  pending-hit negative => 0
  post-response reaccess negative => 0
  recycled-generation negative => no stale match
  no-free/allocation-width retry negative => 0

Required lifetime tests:
  alloc->ready exact interval
  stale completion does not close a newer generation
  IO pending-eviction->response exact interval
  OO deferred eviction->final reclaim exact interval
  immediate reclaim excluded

Required occupancy tests:
  deterministic sample count
  allocated-line-cycle integral
  full-cycle count
  in-flight integral

Run all existing DTC tests too.

Do not continue to expensive waves if directed observer correctness is not clean.
Ordinary test/build problems must be investigated and repaired, not returned as a stop.

============================================================
D3 — EXACT OBSERVER EQUIVALENCE HARD GATE
============================================================

Before using any expensive diagnostic result, prove the observer does not
change pre-existing simulated behavior.

Minimum Core95 qualification:
  NN PAPER_IO
  NN PAPER_OO
  Btree PAPER_IO
  Btree PAPER_OO
  plus one cheap Base control if common stats/plumbing changed.

Use exact accepted parent evidence when config/payload/Core identity matches;
otherwise run only the minimum required parent control.

Require exact equality of:
  cycles
  instructions
  every pre-existing compact scientific counter
  L1/L2/global traffic counters
  lower create/issue/response
  lower credit accounting
  dependency accounting
  terminal PIB/inflight/lower/active-ref drains

Only new observer counters may be additional.
Host walltime/RSS are not required to match.

Any simulated difference is an observer correctness problem.
Investigate, fix and rerun only affected qualification.
Do not use telemetry until:
  D3_OBSERVER_EQUIVALENCE_PASS

For Core658 / 2D, the first new 2D OO observer run may double as the Core658
observer-equivalence qualification only if all pre-existing metrics exactly
match the accepted Core658 2D OO result.

============================================================
D4 — PHYSICAL-POOL ROOT-CAUSE TELEMETRY WAVE
============================================================

After D3 PASS, launch high-information nonduplicate rows using dynamic safe
parallelism.

Workloads:
  BICG
  GESUMMV
  Btree

First-wave physical points:
  24 KiB
  32 KiB
  48 KiB

Modes:
  IO
  OO

Maximum first wave = 18 rows minus any exact telemetry rows already available.

Use the frozen Stage6 workload/config semantics; only observer Core/runtime
identity may differ.

Collect per row:
  avg physical occupancy
  pool-full fraction
  avg in-flight lower requests
  alloc->ready avg/max
  pending Tag eviction count/rate
  IO duplicate count/share
  IO pending-eviction->response avg/max
  OO deferred eviction->final reclaim avg/max
  L2 misses/reservation fails normalized by lower and instructions
  cycles/instruction
  same-mode performance normalization

Do not automatically infer causality.

After enough first-wave evidence terminates, decide from evidence whether
40-KiB telemetry can discriminate H2/H3/H4. If yes, launch it automatically.
If no, do not run it merely for symmetry.

Important reviewed H2 boundary:
  universal cross-workload H2 is not supported;
  BICG/GESUMMV already show a meaningful measured pattern in which normalized
  front-end no-free exposure can fall while L2 pressure and cycles rise;
  use the new occupancy/in-flight/lifetime data to decide whether the LOCAL
  BICG/GESUMMV pressure-transfer hypothesis gains support.
  Btree is a control workload.

============================================================
D5 — OO DUPLICATE FAST12 EXPLORATORY WAVE
============================================================

After D3 PASS, quantify OO duplicate-after-eviction on the frozen FAST12 roster.

Use primary FAST64 OO payload/config semantics.
Use observer95 for non-2D workloads.
Use observer658 for 2DConvolution.

If resources are objectively safe, launch all 12 nonduplicate OO rows.
If prioritization is needed:

  1. Gaussian, 2DConvolution, GEMM, LUD
  2. ATAX, BICG, GESUMMV, Hotspot1
  3. Btree, DWT2D, NN, MRI-Q

For each row report:
  lower created
  pending hits
  Tag evictions
  OO duplicate-after-eviction
  duplicate/lower
  duplicate/Tag-eviction
  duplicate/(duplicate+pending-hit) only as a descriptive event ratio
  duplicate request-payload bytes only if 128-B whole-line semantics remain
  source-proven for that exact mode/config

Do NOT call this DRAM traffic unless downstream evidence proves it.

Accepted Lane-C IO data remains the IO authority.
Do not rerun IO just to reproduce known duplicate counters, except for D3
observer qualification or D4 physical telemetry.

============================================================
POST-REVIEW DUPLICATE TRAFFIC EXTENSION
============================================================

In addition to Lane-C:

  duplicate_share_of_lower = duplicate / lower_created

derive:

  duplicate_traffic_inflation =
      duplicate / (lower_created - duplicate)

Handle zero denominator explicitly.
This is lower-request PAYLOAD inflation per nonduplicate lower request,
not DRAM traffic and not total network-link traffic.

Do not rewrite Lane-C accepted tables; produce a provenance-bound extension.

============================================================
D6 — INTEGRATED OBSERVER ANALYSIS
============================================================

Build the evidence chain:

  physical pool
  -> physical occupancy/full exposure
  -> lower in-flight concurrency
  -> L2 miss/reservation pressure
  -> alloc-to-ready pending lifetime
  -> pending Tag eviction
  -> duplicate lower traffic
  -> performance

Also separately:

  OO Tag eviction
  -> deferred physical lifetime
  -> final reclaim
  -> exposed concurrency/performance

For EACH arrow classify only:
  SOURCE_PROVEN
  MEASURED_CORRELATION
  NOT_SUPPORTED
  INSUFFICIENT

Do not promote correlation into causality.

Explicitly test whether duplicate traffic is:
  negligible
  measurable but secondary
  potentially major
for each representative workload.
Do not define those terms with an after-the-fact threshold presented as a theorem.

A key possibility to test is:
  downstream L2 contention is the primary physical-pool limiter while duplicate
  requests form a secondary positive-feedback mechanism.
Do not assume this; test it.

============================================================
D7 — CLOSEOUT
============================================================

Produce compact, committed artifacts only:

  observer source/runtime identity manifests
  D3 exact-equivalence package
  D4 physical telemetry table + provenance
  D5 OO duplicate FAST12 table + provenance
  duplicate-traffic-inflation extension
  integrated arrow-classification table
  LANE_D_OBSERVER_FINAL.md
  raw-run index only

No multi-GB simulator output in Git.

Terminal state:
  D_OBSERVER_EVIDENCE_READY

============================================================
RESOURCE POLICY
============================================================

The researcher reports CPU/memory are currently largely idle.
Use dynamic measured admission and exploit safe parallelism.
Do not impose arbitrary 1/2-worker limits.

Check:
  physical CPU/core placement
  cgroup CPU quota/throttle
  RSS p95/max
  MemAvailable / cgroup headroom
  sustained swap-out / PSI / OOM
  I/O
  output filesystem

Researcher-authorized disk rule:
  projected free space after admitted wave >= 10 GiB

Do not reject merely because filesystem percentage-used is high.
Do not delete accepted FAST64 evidence.

============================================================
GOAL BEHAVIOR
============================================================

THIS IS GOAL MODE.

Ordinary problems are work to solve, not reasons to stop.

For:
  build errors
  unit-test errors
  parser/schema errors
  stale paths
  observer implementation bugs
  one failed exploratory row
  resource scheduling/admission
  rejected hypotheses
  negative/nonmonotonic results
  a counter proving uninformative
  workload-local execution issues

use:

  OBSERVE
  -> REPRODUCE
  -> CLASSIFY
  -> INSPECT SOURCE / EVIDENCE
  -> TRY SOURCE-CORRECT FIX
  -> REGRESS
  -> INVALIDATE ONLY AFFECTED EXPLORATORY DATA
  -> RERUN ONLY AFFECTED WORK
  -> RESUME

Do not return control after an ordinary problem appears.

Pause only if continuing would require:
  changing accepted DTC mechanism semantics;
  changing accepted FAST64 membership/results;
  inventing a meaning-changing proxy;
  choosing between genuinely irreconcilable scientific interpretations after
  source inspection;
  deleting unique accepted evidence;
  unavailable required infrastructure with no source-correct alternative;
  or researcher review after Lane-D scientific closeout is ready.

Commit/push meaningful checkpoints only.
Do not commit polling/timestamps.
Never git add . or git add -A.
Never modify active long-running script/controller bytes in place; use
future-only versioned paths.

START THE GOAL NOW AND CONTINUE AUTOMATICALLY UNTIL:
  D_OBSERVER_EVIDENCE_READY
```
