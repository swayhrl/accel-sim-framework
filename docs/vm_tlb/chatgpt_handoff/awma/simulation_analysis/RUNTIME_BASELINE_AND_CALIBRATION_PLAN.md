# Runtime Baseline and Calibration Plan

## Objective

Create **`NEW_SIM_BASELINE_V1`** on 174-new as the future maintainable simulation authority. Historical C12 remains a reference/calibration anchor; the new baseline does not need to be byte-identical to the lost historical executable.

## Baseline selection principles

A candidate baseline is acceptable only when all of the following are explicit:

```text
Framework commit
Core commit
compiler/CUDA/toolchain versions
build environment
binary SHA256
base GPU config
trace config
VM/TLB/cache config
telemetry feature set
run wrapper identity
```

Do not use a random existing binary merely because it launches.

## Phase R0 — Environment/toolchain audit

Inventory without destructive system changes:

```text
nvcc / CUDA roots
host compiler
CMake/make/python
Framework checkout(s)
Core checkout(s)
existing binaries
container/shared toolchains
relevant environment variables
```

Record exact paths and versions.

If system-wide CUDA is absent, prefer an isolated or already available project-local toolchain. Installing/upgrading shared system packages is not the first response.

## Phase R1 — Candidate source baseline

Prefer a current, recoverable source pair over an unavailable historical object.

Selection must answer:

1. Is the Core source available by stable Git SHA?
2. Does it contain the VM/TLB/PTW/cache hooks required by current configs?
3. Can the telemetry required by `export_m4c_telemetry.py` or its successor be produced?
4. Is the trace grammar compatible with the retained historical traceg anchors?
5. Can the binary be rebuilt reproducibly on 174-new?

If small forward-port fixes are required and scientifically obvious, implement them in a dedicated source branch with directed regression tests. Do not hide semantic changes as “build fixes”.

## Phase R2 — Isolated build and receipt

A successful build produces a baseline candidate receipt containing at least:

```text
SIM_BASELINE_CANDIDATE_ID
framework SHA
core SHA
patch/diff SHA if any
compiler versions
CUDA version
build command
build log SHA
binary SHA
config ledger SHA
telemetry schema version
```

A build failure is not enough evidence to stop the entire Simulation Analysis foundation round. Bound the attempt, record the exact blocker, and continue with input/catalog/telemetry infrastructure where possible.

## Phase R3 — Parser/trace smoke

Before timing/performance claims, use retained historical `.traceg.xz` anchors to verify:

```text
trace list parses
expected kernel count is observed
no malformed trace records
record/instruction counts are stable on repeated read
memory addresses survive parsing unchanged
run terminates or reaches a clearly bounded expected checkpoint
```

This is an input/runtime compatibility gate, not a performance experiment.

## Phase R4 — Historical calibration anchors

Minimum preferred anchors:

```text
C12 Prefill F0
C12 Decode1 F0
one M4C control/reference run when identity is closed
```

Calibration compares the new runtime against historical records at several levels.

### Level A — identity/input exactness

Must be exact when claiming the same historical input:

```text
trace/list hash
object/registration sidecar hash
config identity
ROI identity
```

### Level B — parser/traffic invariants

Compare where derivable:

```text
kernel count
instruction/warp count
memory operation count
address/page/cache-line footprint
read/write class distribution
```

Unexpected differences are blockers until explained.

### Level C — modeled telemetry

Compare:

```text
TLB/PTW counts
cache traffic/hits/misses
DRAM traffic
cycles/IPC
queue/stall metrics
```

Exact equality is **not automatically required** for a new source/toolchain baseline. Differences must be quantified and explained.

The result should be classified as one of:

```text
EXACT_REPLAY_PASS
CALIBRATED_NEW_BASELINE_PASS
CALIBRATED_WITH_DOCUMENTED_MODEL_DIFF
INPUT_COMPATIBLE_PERFORMANCE_NOT_CALIBRATED
FAIL_INPUT_OR_RUNTIME_MISMATCH
```

Do not call a non-exact baseline an exact historical reproduction.

## Phase R5 — Baseline freeze

Only after the calibration gates pass may a candidate become:

```text
NEW_SIM_BASELINE_V1
```

Freeze:

```text
SIM_BASELINE_ID
source SHAs
binary SHA
config ledgers
telemetry schema
calibration review pack
known fidelity differences
supported/unsupported claims
```

Every future mechanism run must bind this baseline ID or a later explicitly qualified baseline.

## Runtime evolution

Later baseline upgrades are allowed, but require a new ID and regression against the previous qualified baseline. Never silently rebuild a binary under the same baseline identity.
