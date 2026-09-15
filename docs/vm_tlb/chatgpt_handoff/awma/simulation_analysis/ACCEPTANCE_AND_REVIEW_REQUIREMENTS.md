# Acceptance and Review Requirements

## Stage-level acceptance philosophy

Simulation Analysis is accepted by independently reviewable evidence, not by a Codex `PASS` string.

Every completed major stage must bind, as applicable:

```text
source/config identity
input identity
runtime/binary identity
raw-output identity
normalized-output identity
scientific status
execution status
claim boundary
reproducible test/regression evidence
```

The stage is designed for Goal-mode autonomous execution. A recoverable engineering issue is not itself a STOP condition. Codex should repair, test, record and continue whenever scientific meaning is unchanged.

## Parallel-execution acceptance

Because Simulation Foundation may run concurrently with Native Characterization on 174-new/109, the review pack must prove isolation:

1. separate worktree and branch;
2. no mutation/clean/reset of the active Native worktree;
3. no kill/restart of active Native/Codex/SSHFS processes;
4. bounded build/runtime concurrency;
5. dedicated simulation scratch/build paths;
6. writes restricted to authorized AWMA simulation/catalog/provenance namespaces;
7. no accepted C16/native raw, parsed or feature bytes modified;
8. no GPU use in this foundation stage.

A resource-contention issue should normally be solved by reducing concurrency/priority, not by stopping another Goal.

## Simulation Foundation completion states

Preferred:

```text
AWMA_SIMULATION_FOUNDATION_PASS
```

Conditionally acceptable:

```text
AWMA_SIMULATION_FOUNDATION_PASS_RUNTIME_BLOCKED
```

The second status is valid only if:

- the runtime/toolchain blocker is exact and evidenced;
- the recovery ladder has been exercised to a reasonable bounded conclusion;
- alternative evidence-backed runtime/source/toolchain candidates were considered where available;
- no scientific-semantic shortcut was taken;
- all mandatory non-runtime gates below pass;
- the minimum next action is concrete rather than vague.

A first failed build, absent default `nvcc`, stale path, or missing helper binary is **not sufficient** by itself to declare runtime blocked.

## Mandatory non-runtime foundation gates

All must pass:

1. versioned simulation identity schemas exist for `SIM_INPUT`, `SIM_BASELINE`, `SIM_RUN`, telemetry and comparison rows;
2. identities are deterministic under canonical serialization and semantic changes alter identity;
3. simulator input admission is machine-checkable and fail-closed;
4. current C16WARP1/MREF-sharded evidence is explicitly rejected as simulator-eligible (`NOT_PROVEN_LOSSLESS`) unless a future formal proof exists;
5. historical C12 Prefill/Decode F0 are backfilled without pretending they were freshly replayed;
6. C13/C14 diagnostic boundaries and C12 PRE_FIX/diagnostic boundaries are preserved;
7. simulation telemetry normalization exists and is regression-tested on real historical evidence plus negative fixtures;
8. catalog entries are immutable/idempotent and same-ID conflicting content fails closed;
9. `SIM_COMPAT_CAPTURE_V1` consumer schema/validator exists with positive and mandatory negative fixtures;
10. node164 simulation/catalog/provenance metadata outputs are hash-closed;
11. producer-facing contract bundle is sufficient for a later 109 Goal without redesigning the consumer contract;
12. no accepted Native raw/parsed/feature authority is mutated;
13. review pack independently proves all mandatory gates;
14. inline recoveries are recorded with root cause, repair, semantic-neutrality rationale and regression evidence.

If any mandatory gate fails because Codex simply stopped at a recoverable issue, the stage is not accepted.

## Runtime recovery acceptance

Before `BLOCKED_ENVIRONMENT` is accepted, evidence should cover the applicable recovery ladder:

```text
local CUDA/toolchain inventory
shared/mounted toolchain inventory
available source branches/checkouts
available historical/current binaries and receipts
isolated user-space dependency option when safe
non-semantic build portability repair attempts
alternative evidence-backed source/runtime candidate when reasonable
```

It is not necessary to perform destructive/system-wide installation or unlimited network/toolchain archaeology.

The goal is a maintainable current runtime, not exact resurrection of an unavailable historical binary.

## `NEW_SIM_BASELINE_V1` qualification gates

The baseline may be declared only if all applicable gates pass:

1. framework/core source commits are stable, recorded and fetchable or archived;
2. toolchain identity and relevant compiler/CUDA versions are recorded;
3. build command/environment are reproducible;
4. simulator binary SHA256 is frozen;
5. effective base/trace/VM configuration hashes are frozen;
6. required VM/TLB/PTW/cache options are recognized by the runtime;
7. required telemetry schema is actually emitted;
8. at least C12 Prefill F0 and Decode1 F0 are exercised as bounded calibration anchors unless one is independently unavailable;
9. input/list/trace hashes for calibration are exact;
10. parser/record/traffic invariants have no unexplained correctness mismatch;
11. historical-vs-new telemetry/performance deltas are quantified rather than hidden;
12. repeated bounded smoke does not silently alter binary/config/input identity;
13. supported and unsupported claim scope is explicit;
14. a deterministic `SIM_BASELINE_ID`/receipt is produced.

A non-matching historical/EP-L2 binary cannot qualify merely because it executes some trace.

## Historical calibration result classes

Each bounded historical anchor must be classified explicitly:

```text
EXACT_REPLAY_PASS
NUMERICALLY_CLOSE_WITH_EXPLAINED_RUNTIME_DIFF
STRUCTURALLY_VALID_BUT_NOT_NUMERICALLY_EQUIVALENT
BLOCKED_INPUT_OR_RUNTIME
FAIL_UNEXPLAINED_MISMATCH
```

Only the first two are candidates for strong numerical calibration claims. Structural validity alone is useful for parser/runtime qualification but not exact historical reproduction.

Timed-out runs are diagnostic unless the specific acceptance contract explicitly treats a bounded prefix as valid evidence.

## Simulator-compatible capture consumer qualification gates

The 174-new consumer side may be called ready only if:

1. `SIM_COMPAT_CAPTURE_V1` is versioned and machine-readable;
2. exact workload/target binding fields are required;
3. launch/instruction/warp/CTA/order semantics required by the simulator are explicit;
4. opcode/access kind/width/memory-space requirements are explicit;
5. active mask/lane addresses and required control/synchronization markers are explicit;
6. terminal completeness/drop/overflow semantics are explicit;
7. payload/list/sidecar SHA closure is required;
8. required address-context/object/ASID/VA/page sidecars are defined;
9. valid synthetic fixture passes;
10. missing order fails;
11. missing width/access kind fails;
12. incomplete/drop/overflow fails;
13. hash mismatch fails;
14. deterministic re-read yields stable input identity.

No producer GPU capture is required for this consumer-side gate.

## `SIM_COMPAT_CAPTURE_V1_QUALIFIED` producer+consumer gates

Later, a real 109 capture may receive the full qualification only when:

1. exact workload/target binding is closed;
2. required simulator semantics are present from the producer, not inferred from C16WARP1;
3. zero drop/overflow and complete terminal/list closure are proven;
4. payload/list/sidecar hashes close;
5. 174-new consumer admission succeeds;
6. stable `SIM_INPUT_ID` is produced;
7. decoded record/address/instruction/warp sanity checks pass;
8. bounded replay on `NEW_SIM_BASELINE_V1` succeeds;
9. repeat capture/re-read checks required by the capture contract are satisfied;
10. unsupported claims remain explicit.

## Current-model formal simulation acceptance

For every current-model formal simulation target, close:

```text
WORKLOAD_ID
TARGET_ID
SIM_INPUT_ID
SIM_BASELINE_ID
SIM_RUN_ID
```

Retain at minimum:

```text
input manifest/hash
config/overlay hash
simulator binary hash
command/environment receipt
raw log hash
normalized telemetry hash
completion status
scientific status
claim scope
```

Partial/time-bounded runs remain diagnostic unless a specific analysis contract formally supports them.

## Mechanism experiment acceptance

Every mechanism result must provide:

```text
explicit baseline run
mechanism run
same admitted input
same qualified baseline unless intentionally comparing baselines
only intended config/model delta
performance result
mechanism-relevant counters
negative/regression cases, not only wins
```

A mechanism cannot be generalized from one target unless the claim is explicitly target-specific.

Mechanism semantics changes require an explicit design decision and cannot be hidden as a build/portability fix.

## Cross-view acceptance

Native and Simulation evidence remain separate origins.

Quantitative comparison requires an explicit identity relation. Examples:

```text
EXACT_WORKLOAD_TARGET_DIFFERENT_CAPTURE
HISTORICAL_REFERENCE
STRUCTURALLY_ALIGNED
```

`STRUCTURALLY_ALIGNED` does not automatically authorize absolute calibration.

Disallowed joins include:

```text
similar kernel name only
same family but different scenario
retokenized input
changed dtype/backend/context/batch without explicit relation
unknown target mapping
```

Native measurements must never be overwritten by simulated values; disagreement is calibration evidence.

## Review pack standard

Every major stage review pack must include at least:

```text
README entry point
source anchors
execution context / parallel-isolation evidence
changed files/commits
validation and regression summary
formal-vs-diagnostic boundary
raw artifact index/hashes
inline recovery log
runtime/build status
open issues
SHA256SUMS
```

Large raw traces/logs stay outside Git; Git stores indexes, identities and hashes.

## Efficiency and autonomy rule

Do not create separate stages for issues that are:

```text
obvious
safe
non-scientific
locally testable
```

Fix them inline, test them, record them and continue.

A new explicit decision/stage is justified when a change affects:

```text
workload identity
trace semantics
simulator architectural semantics
scientific status
baseline definition
mechanism definition
formal claim scope
accepted raw/provenance authority
```

The purpose of Goal mode is to complete coherent scientific-engineering stages, not to turn each recoverable defect into another coordination round.
