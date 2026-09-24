# AWMA C1 fanout-aware within-model holdout V1

Status: **COMPLETE / FANOUT_ONLY_GATING_INSUFFICIENT_ON_WITHIN_MODEL_INDEPENDENT_TARGETS**

## Outcome

Both independent kernel identities pass every correctness, exactly-once,
coverage, controller-drain, candidate-state-drain, and provenance gate.  They
also show only cohorts of size 4 or larger, so frozen Fanout-4 gates nothing and
is identical to accepted raw C1-2 in every recorded operational metric; only
the configured threshold field differs.

| target | accepted OFF | C1-2 | C1-4 | C1-4 vs OFF | lookup suppression |
|---|---:|---:|---:|---:|---:|
| SPLITKV | 73,923 | 75,950 | 75,950 | 2.742% | 99.237% |
| COMBINE | 10,480 | 10,615 | 10,615 | 1.288% | 99.057% |

This is the specified stop condition: Fanout-4 still has a clear negative
performance response on both targets despite very large physical-lookup
suppression.  Therefore cohort fanout alone is not a sufficient gate for C1.
No threshold was changed or swept, and no additional simulation was run.

## Cohort and wait evidence

- SPLITKV: 14,826 shared cohorts (126 size-4, 252 size-5..8, 14,448
  size-9..16), zero gated cohorts, 7,883,943 member owner-wait cycles and
  791,317 C1 head-block cycles.
- COMBINE: 74 shared cohorts (11 size-5..8, 63 size-9..16), zero gated
  cohorts, 32,263 member owner-wait cycles and 3,745 C1 head-block cycles.
- C1-2 and C1-4 are exactly equal for cycles, lookup/probe counts, all cohort
  bins, owner wait, head blocking, admissions, deliveries, coverage, and
  downstream issue timing on each target.
- Repeated admissions and readmitted UIDs are zero for all four runs.  This
  rules out re-admission as the immediate explanation here, while the large
  owner-wait/head-block signal remains consistent with the accepted Phase 3
  attribution.

## Validation scope

The two kernel identities did not participate in selecting
`MIN_COHORT_SIZE=4`, so this is a
`WITHIN_MODEL_INDEPENDENT_TARGET_VALIDATION`.  Both remain Qwen2.5 S2 assets;
this is **not** cross-context or cross-model scientific holdout evidence.

The accepted 10/80 OFF results were reused without rerun.  The experiment used
an independent worktree, runtime, build, binary, and durable output path.  The
accepted mechanism source is reused unchanged; `SOURCE_REUSE.tsv` verifies the
Core source hashes.  The fixed RTX4080/V1 configuration and downstream memory
semantics were not modified.

## Interpretation and next discriminating experiment

The discovery result does not promote a baseline and does not establish a
paper mechanism.  A future, separately authorized experiment should test a
readiness/wait-cost-aware gate (for example, share only when the owner result is
already ready, with lookup-suppression loss reported) on independent targets.
That directly distinguishes high fanout from owner-ready timing.  It must not
reuse this holdout to tune `MIN_COHORT_SIZE`.

## Limits

- Two kernels from one Qwen2.5 S2 workload context.
- Simulator-relative RTX4080/V1 10/80 configuration, not a hardware latency
  claim.
- No threshold sweep, no cross-model trace, no baseline promotion, and no
  novelty or paper-level conclusion.
