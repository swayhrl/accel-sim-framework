# EP-L2 M0a Generic Observability — Acceptance Criteria

Status: mandatory self-gating contract.

## A. Exact source parent / isolation

PASS only if the implementation derives from the accepted D512 research semantic parent:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

Use dedicated M0a worktrees/branch/result root. Do not modify historical D256/D512 calibration or M1 worktrees/results.

## B. Observation-only semantics

No M0a value may be read by:

```text
admission
replacement
payload allocation
MSHR/descriptor allocation
bank arbitration
lower routing
scheduler/DRAM behavior
```

M0a is a producer/parser/reporting change only.

## C. Cycle-based admission accounting

For a frontend head with an exact preview evaluated in a cycle:

```text
observed_cycles += 1 exactly once
```

If it cannot admit:

```text
any_blocked_cycles += 1 exactly once
```

Each independently true reason may also increment once in that cycle. Reason counts may overlap; `any_blocked` may not.

If current preview logic short-circuits before all independent reason predicates are known, PASS requires either:

1. a side-effect-free reason-bitset audit that evaluates all required resource predicates without changing the existing final admit decision; or
2. narrower explicitly-primary reason semantics.

Do not silently label a single primary reason as independent multi-cause evidence.

## D. No retry-event relabeling

The new blocked-cycle fields must be produced at the cycle-level exact frontend admission point. Existing retry/full event counters may be compared but cannot be reused as blocked-cycle values.

Directed tests must distinguish repeated retry events from one-cycle accounting.

## E. Useful service semantics

`m0_useful_frontend_admit` increments only after the frontend request is actually accepted/mutated once.

`m0_useful_response_enqueue` increments only when the requester response is accepted into L2->ICNT at the real retirement boundary.

No re-presented blocked head or failed enqueue may increment a useful count.

## F. Resident payload sampling

Resident occupancy/free must derive from actual production resident state at one documented sampling point.

No current dormant bypass slot count may be presented as workload opportunity. M0a must not create a bypass consumer or bypass demand proxy.

## G. Scope / temporal integrity

Required cumulative/application and 5K-window output must document:

```text
scope
sampling/production point
reset/delta rule
denominator
overlap policy
configured slice count
window interval
```

5K records must preserve exact 64-slice time-group/cardinality semantics or fail closed.

## H. Existing telemetry semantics

Do not rename or reinterpret C7e/Lane-D fields. New M0a fields use a new schema/family/version or an explicitly additive compatible extension.

Parser tests must reject missing/malformed required new fields when M0a mode is declared enabled.

## I. OFF/ON timing neutrality

A config switch may disable M0a emission/collection. With M0a OFF, the new source must reproduce the accepted D512 parent on representative natural workloads.

With M0a ON, simulated functional behavior must remain identical to OFF:

```text
cycles
instructions
existing parsed C7e/B0 counters where deterministic
DRAM read/write issues/bytes
terminal invariants
payload consistency
```

At minimum require OFF-vs-ON equivalence on:

```text
vectorAdd_4M
convolutionSeparable
sad
```

Host wall time may differ.

## J. Correctness / regression

Required:

```text
Release build
relevant existing C3-C7/EP-L2 directed regressions
new unit tests for cycle/overlap/useful-count semantics
parser/analyzer tests
git diff --check
clean frozen source worktrees
terminal no-leak invariants
```

## K. Representative characterization output

After correctness freeze, M0a ON must produce usable evidence for at least:

```text
convolutionSeparable
scan
vectorAdd_4M
spmv
cfd_097k
sad
```

Runs may execute in parallel in unique result roots. A long scan must not block launching the other rows.

The report should provide per workload:

```text
blocked-cycle fraction = any_blocked / observed
reason fractions
reason overlap note
resident occupancy/slack
useful admits
useful response enqueues
5K p50/p95/max / high-pressure phase summaries where meaningful
```

Do not upgrade these observations to a functional mechanism benefit.

## L. Packaging

Required review pack:

```text
docs/ep_l2/review_packs/M0A_OBSERVABILITY_r1/
  README.md
  SOURCE_ANCHORS.md
  CHANGED_FILES.md
  FIELD_SEMANTICS.md
  VALIDATION_SUMMARY.md
  TIMING_NEUTRALITY.csv
  WORKLOAD_M0A_SUMMARY.csv
  TEMPORAL_M0A_SUMMARY.csv
  RAW_LOG_INDEX.tsv
  SHA256SUMS
  validation/
```

Update:

```text
docs/ep_l2/codex_handoff/LANE_M0A_LATEST.md
```

## M. STOP

Only declare:

```text
M0A_OBSERVABILITY_REVIEW_READY
```

Do not implement M0b, Unified, RO, TVD, adaptive policy or headroom experiments in this stage.
