# Acceptance and Review Requirements

## Stage-level acceptance philosophy

Simulation Analysis must be accepted by evidence, not by a Codex `PASS` string.

Every completed stage requires:

```text
source/config identity
input identity
runtime/binary identity when applicable
raw-output identity
normalized-output identity
status/claim boundary
reproducible test evidence
```

## Simulation foundation acceptance

The first 174-new Simulation Foundation stage may close as either:

```text
AWMA_SIMULATION_FOUNDATION_PASS
```

or:

```text
AWMA_SIMULATION_FOUNDATION_PASS_RUNTIME_BLOCKED
```

The second form is acceptable only when the runtime blocker is exact and bounded, and all non-runtime infrastructure passes.

Required non-runtime PASS gates:

1. simulator input identity/admission is machine-checkable;
2. current C16WARP1 is explicitly rejected as simulator-eligible input;
3. historical C12 F0 records are backfilled without status promotion;
4. simulation telemetry normalization exists and is regression-tested;
5. catalog entries are immutable/idempotent and conflicting content fails closed;
6. future `SIM_COMPAT_CAPTURE_V1` consumer schema has positive/negative fixtures;
7. node164 small metadata/dataset outputs are hash-closed;
8. no accepted Native raw is mutated;
9. no historical DIAGNOSTIC evidence is promoted to FORMAL;
10. review pack independently proves the above.

## Runtime baseline qualification gates

`NEW_SIM_BASELINE_V1` may be declared only if:

1. source commits are stable and fetchable;
2. toolchain/build identity is recorded;
3. binary SHA256 is frozen;
4. required VM/TLB/PTW/cache features parse and run;
5. telemetry required by the baseline schema is emitted;
6. at least two bounded historical anchors are understood, preferably C12 Prefill F0 and Decode1 F0;
7. parser/traffic invariants show no unexplained mismatch;
8. historical-vs-new performance/telemetry differences are quantified;
9. supported/unsupported claim scope is written explicitly;
10. repeated smoke run does not silently change identity/config.

## Simulator-compatible capture qualification gates

`SIM_COMPAT_CAPTURE_V1_QUALIFIED` requires:

1. exact workload/target binding;
2. complete trace semantics required by the simulator;
3. no drops/overflow/incomplete terminal state;
4. payload/list/sidecar hash closure;
5. 174-new admission and stable `SIM_INPUT_ID`;
6. decoded record/address sanity;
7. bounded simulator smoke on the qualified baseline;
8. evidence that no missing semantics were synthesized from C16WARP1.

## Current-model baseline simulation acceptance

For every current-model formal simulation target:

```text
WORKLOAD_ID
TARGET_ID
SIM_INPUT_ID
SIM_BASELINE_ID
SIM_RUN_ID
```

must all be closed.

At minimum retain:

```text
input manifest/hash
config/overlay hash
simulator binary hash
command/environment receipt
raw log hash
normalized telemetry hash
completion status
```

Partial/time-bounded runs are diagnostic unless the analysis contract explicitly supports them.

## Mechanism experiment acceptance

Every mechanism result must provide:

```text
explicit baseline run
mechanism run
same admitted input
same qualified baseline unless intentionally comparing baselines
only intended config delta
performance result
mechanism-relevant counters
regression cases, not only wins
```

A mechanism cannot be called effective from one target alone unless the claim is explicitly target-specific.

## Cross-view acceptance

Native and Simulation rows may be quantitatively compared only when an explicit identity relation exists.

Allowed examples:

```text
EXACT_WORKLOAD_TARGET_DIFFERENT_CAPTURE
HISTORICAL_REFERENCE
STRUCTURALLY_ALIGNED
```

`STRUCTURALLY_ALIGNED` does not automatically permit absolute metric calibration.

Disallowed:

```text
similar kernel name only
same model family but different scenario
retokenized input
changed backend/dtype/context
unknown target mapping
```

## Review pack standard

Every major stage review pack must include:

```text
README entry point
source anchors
changed files/commits
validation summary
formal-vs-diagnostic boundary
raw artifact index/hashes
open issues
SHA256SUMS
```

Large raw traces/logs stay outside Git; Git stores indexes and hashes.

## Efficiency rule

Do not create extra stages for small issues that are:

```text
obvious
safe
non-scientific
locally testable
```

Fix them inline and report the fix.

Do create a new explicit decision/stage when a change affects:

```text
workload identity
trace semantics
simulator model semantics
scientific status
baseline definition
mechanism definition
formal claim scope
```
