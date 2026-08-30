# EP-L2 Speculative Parallel Execution Policy

Status: **authorized for calibration lanes when compute resources are abundant.**

This policy changes execution scheduling, not scientific acceptance criteria.

## Core rule

> A dependency may block **promotion of evidence** without blocking **launch of computation**.

When the upstream source/config candidate is frozen and the remaining gate is a validation/acceptance gate, downstream experiments may start early as **provisional/speculative** work. They become usable evidence only after every declared promotion dependency passes.

This is intentionally different from a strict chapter-by-chapter workflow.

## Evidence maturity labels

Use these exact labels in manifests/status notes where practical:

```text
SPECULATIVE_PENDING_GATE
PROMOTED_VALID_CALIBRATION
INVALIDATED_BY_UPSTREAM_GATE
```

`COMPLETE_VALID` continues to describe whether a simulator run itself completed normally with local invariants. It does **not** by itself mean the run has passed all cross-lane promotion gates.

Thus a run may be both:

```text
run_status = COMPLETE_VALID
maturity   = SPECULATIVE_PENDING_GATE
```

until upstream validation passes.

## Launch requirements

A speculative downstream run may launch only if all of the following are true:

```text
1. the candidate Core SHA is frozen and recorded;
2. the candidate Framework SHA is frozen and recorded;
3. effective runtime config / overlay hashes are frozen and recorded;
4. workload/trace identity is frozen;
5. the only unresolved dependencies are validation/promotion gates,
   not an unknown architectural definition;
6. the lane uses isolated worktrees, binaries, result roots and manifests;
7. the result manifest records every unresolved promotion dependency.
```

Do not speculatively run from a moving branch tip. Use exact immutable SHAs or an isolated worktree pinned to them.

## Promotion

A speculative result may be promoted without rerunning the simulator only if:

```text
- its exact Core/Framework/config/trace identity matches the candidate that passed;
- every declared upstream promotion gate is PASS;
- no producer/source defect was discovered that affects the generated telemetry or timing;
- local COMPLETE_VALID/invariant/parser requirements pass;
- the relevant lane acceptance criteria pass.
```

Promotion changes evidence maturity only. It does not change raw simulator results.

## Invalidation

If an upstream gate fails:

### Source/producer/timing-equivalence defect

All descendant runs based on that candidate are:

```text
INVALIDATED_BY_UPSTREAM_GATE
```

Keep them for diagnosis, but do not use them in calibration conclusions. Fix the source/config candidate and rerun affected descendants.

### Packaging/parser/analysis-only defect

If raw producer output and simulated timing remain valid, descendants do not automatically require simulator reruns. Repair/reprocess and re-evaluate promotion.

### Preflight finds a real D512 semantic/config defect

All D512 mirror and D512×L1 descendants from that candidate are invalidated. Do not silently reinterpret them.

## Speculative chaining allowed

A provisional result may feed another speculative experiment only when the child records the entire promotion chain.

Example:

```text
D512 candidate
  depends on: D256_EQ_SCAN_PASS + D512_PREFLIGHT_PASS

D512 + L1 META-HR speculative child
  depends on: D256_EQ_SCAN_PASS + D512_PREFLIGHT_PASS
              + Lane-C config-delta/local validation
```

No speculative chain may be used for `BASELINE-DECISION` until all dependencies are promoted.

## Lane B authorization

Given the currently frozen candidate:

```text
Core candidate:      878f80869ce212e779df20b6421e4dc7f987825d
Framework candidate: aae62b66685f15437cecf0193934f628e6fac6ae
```

and the already-passing short D256 equivalence checks for `vectorAdd_4M` and `spmv`, Lane B is authorized to launch **now**, in parallel with the still-running long `scan` D256 equivalence:

```text
D512 natural preflight subset
D512 full 13x2 speculative mirror
```

These runs must be labeled `SPECULATIVE_PENDING_GATE` with promotion dependencies including:

```text
D256_EQ_SCAN_PASS
D512_PREFLIGHT_PASS
```

Prefer one frozen D512 mirror campaign whose highest-priority jobs are the preflight workloads; those same completed mirror rows may serve as preflight evidence if their configuration and provenance are identical. A separate duplicate preflight campaign is not scientifically required.

Lane B may declare `D512_READY` only after the original mandatory B0-B6 acceptance gates pass. The early mirror launch does not weaken that gate.

## Lane C authorization

Lane C D256 cells remain independent and continue normally.

Lane C is additionally authorized to start **speculative D512 interaction cells before `D512_READY`** using the exact Lane-B candidate SHAs/config definition above (or a later explicitly superseding frozen candidate recorded by Lane B).

Allowed provisional cells:

```text
D512 + L1 META-HR
D512 + L1 BANK-HR
```

They must:

```text
- derive from the exact Lane-B D512 candidate, not recreate D512 independently;
- use isolated Lane-C worktrees/results;
- carry promotion dependencies D256_EQ_SCAN_PASS and D512_PREFLIGHT_PASS;
- remain SPECULATIVE_PENDING_GATE until Lane B publishes D512_READY;
- be invalidated/rerun if the Lane-B D512 source/config candidate changes.
```

Lane C may also trigger one-at-a-time D256 decomposition per workload as soon as that workload's META-HR result shows the acceptance-defined material response; it need not wait for all seven screening workloads.

## Lane D handling

Lane D may ingest speculative outputs early for tooling/debugging and provisional dashboards, but must retain maturity labels and must not emit them as accepted calibration deltas until promotion contracts pass.

`CAL-ANALYSIS` and `BASELINE-DECISION` use only promoted evidence.

## Workboard semantics

For rows covered by this policy, the `Dependency` column is a **promotion dependency** unless explicitly marked as a launch-hard dependency.

Use `Execution status = RUNNING` for speculative jobs that are actually running, and put `SPECULATIVE_PENDING_GATE` plus the unresolved gate names in `Progress / result`.

Do not mark the row `DONE` until its original acceptance criteria are satisfied.

## Scientific boundary

This policy spends extra compute to reduce wall-clock time; it does not lower evidence standards. We explicitly accept the possibility that failed upstream gates force reruns of speculative descendants.
