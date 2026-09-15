# CODEX NEXT STAGE — 174-new AWMA Simulation Foundation

## Status

**Prepared but NOT ACTIVE while the current Qwen Decode/analysis Goal is running on 174-new.**

Run only after the current active Goal is cleanly closed and the user/ChatGPT explicitly activates this stage.

Suggested branch when activated:

```text
hrl/awma-simulation-foundation-174new-v1
```

Primary node:

```text
174-new / port 2239
```

GPU use: **none in this stage**.

## Objective

In one substantial round, establish the consumer-side Simulation Analysis foundation far enough that the only major remaining dependency is simulator-compatible trace production from 109.

Do not stop after writing design docs. Implement, test, catalog and bounded-qualify as much as is possible on 174-new.

## Source anchors

Consume at least:

```text
AWMA coordination:
hrl/awma-simulation-analysis-plan-v1
<this document's activation commit>

Historical canonical inheritance:
7b6f2b88c36b4ed1bbdcd72761063f881c7b6c96

Historical simulation review pack:
docs/vm_tlb/review_packs/C12_C15_174NEW_CANONICAL_INHERITANCE_V2/
```

Also inspect current repository state for newer accepted simulation-analysis infrastructure, but do not silently reinterpret active Native evidence.

## Read first

```text
docs/vm_tlb/chatgpt_handoff/awma/simulation_analysis/README.md
CURRENT_STATE.md
SIMULATION_ANALYSIS_ARCHITECTURE.md
RUNTIME_BASELINE_AND_CALIBRATION_PLAN.md
SIMULATOR_INPUT_AND_CAPTURE_PLAN.md
SIMULATION_METRICS_AND_DATA_MODEL.md
EXECUTION_ROADMAP.md
ACCEPTANCE_AND_REVIEW_REQUIREMENTS.md
```

## Worktree isolation

Create a fresh worktree. Record:

```text
hostname
branch/base SHA
worktree path
node164 mount identity
available toolchains
```

Do not modify a worktree currently used by another experiment.

## Phase A — Simulation authority inventory refresh

Quickly refresh, do not re-run full archaeology.

Confirm current authority for:

```text
historical traceg/list inputs
historical raw logs
M4C/M4B configs
run_m4c_replay.sh
export_m4c_telemetry.py
summarize_m4c_runs.py
analyze_m4c_trace_locality.py
C12 formal baselines
node164 historical datasets
```

Produce a concise machine-readable inventory with source path/SHA/status.

## Phase B — AWMA simulation identities and schemas

Implement or reuse versioned schemas for:

```text
SIM_INPUT
SIM_BASELINE
SIM_RUN
SIM_TELEMETRY_ROW
SIM_COMPARISON_ROW
```

Use AWMA common identity rules where already implemented; if the unified foundation stage has not yet run, implement the narrow simulation subset now without blocking on a separate naming/cleanup round.

Required behavior:

- canonical serialization;
- deterministic SHA-based IDs;
- conflict detection;
- explicit scientific/execution status;
- evidence origin preserved;
- UNKNOWN never guessed.

## Phase C — Simulation input admission

Build a fail-closed admission path for simulator-native inputs.

At minimum support historical/native traceg bundles:

```text
kernelslist.g
*.traceg.xz
config/registration/object sidecars where required
manifest/receipt hashes
```

Admission verifies:

```text
all referenced files exist
hashes match
trace/list grammar is acceptable
terminal/list closure where applicable
identity sidecars are consistent
```

Issue `SIM_INPUT_ID` only to admitted bundles.

Explicit negative test:

```text
current C16WARP1/MREF-sharded input
→ NOT_PROVEN_LOSSLESS / no SIM_INPUT_ID
```

Do not create a converter that fabricates missing order/opcode/width/control semantics.

## Phase D — Historical simulation adapter/backfill

Normalize at least:

```text
C12 Prefill F0
C12 Decode1 F0
one M4C control/reference asset
one M4B/Segment diagnostic asset if identity is sufficient
```

Preserve:

```text
HISTORICAL_RECORD evidence origin
FORMAL/DIAGNOSTIC status
historical framework/core/binary identities
raw log/input hashes
claim boundaries
```

These are inherited records, not fresh runs.

## Phase E — Telemetry normalization

Implement a canonical AWMA Simulation Evidence normalizer around current telemetry tools.

Reuse `export_m4c_telemetry.py` where practical instead of duplicating a proven parser.

Normalized output must support translation, cache/memory and performance domains from `SIMULATION_METRICS_AND_DATA_MODEL.md`.

Tests must include:

- valid historical log;
- missing/partial telemetry;
- duplicated/conflicting records;
- unknown metric namespace;
- deterministic normalized output.

## Phase F — Runtime/toolchain bring-up

Actively attempt to establish a maintainable candidate for `NEW_SIM_BASELINE_V1`.

Do not waste the full round searching indefinitely for the historical binary.

Perform bounded steps:

1. inventory local/shared CUDA and build toolchains;
2. inventory source candidates and relevant branches;
3. select a current source pair with VM/TLB/PTW/cache hooks;
4. build in isolation if a compatible toolchain exists;
5. record source/toolchain/build/binary hashes;
6. if build fails, classify exact cause and continue remaining phases.

Small obvious build portability fixes may be made inline if they do not change simulator semantics. Semantic changes require explicit diff/rationale/tests.

## Phase G — Historical calibration smoke

If a candidate binary builds, run bounded anchors only:

```text
C12 Prefill F0
C12 Decode1 F0
```

Optionally one M4C control after the first two are understood.

Check in order:

```text
input identity
parser/record invariants
execution completion
telemetry presence
historical-vs-new metric deltas
```

Classify per the calibration categories in `RUNTIME_BASELINE_AND_CALIBRATION_PLAN.md`.

Do not run the whole historical C12 matrix.

If runtime is blocked, create a precise `RUNTIME_BLOCKER_AND_RECOVERY_PLAN.md` containing the minimum next action; do not fail the entire stage if all non-runtime foundation work passes.

## Phase H — Future `SIM_COMPAT_CAPTURE_V1` consumer contract

Implement machine-readable validation/schema for the future producer contract now, on CPU.

Create positive/negative synthetic fixtures covering:

```text
ordering
opcode/access kind
width
warp/CTA/mask
addresses
control/sync markers
terminal completeness
drop/overflow
sidecar hashes
```

The consumer validator must be ready before 109 begins GPU capture qualification.

## Phase I — Catalog and node164 layout

Create only small metadata/dataset outputs under the existing AWMA logical namespace, e.g.:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
  catalog/awma/entries/
  catalog/awma/snapshots/
  derived/awma/simulation/inputs/
  derived/awma/simulation/telemetry/
  derived/awma/simulation/datasets/
  provenance/awma/simulation/
```

Do not move/rename existing large historical data merely for aesthetics.

Create snapshots for at least:

```text
SIM_INPUTS
SIM_BASELINES
SIM_RUNS
SIM_EVIDENCE
```

## Phase J — Tests and regressions

Required tests:

```text
identity determinism
schema validation positive/negative
input hash mismatch rejection
trace-list missing file rejection
C16WARP1 simulator-ineligible rejection
historical status preservation
telemetry normalization determinism
catalog idempotence/conflict behavior
runtime receipt determinism when built
```

Do not weaken historical/native tests.

## Phase K — Required deliverables

Review pack:

```text
docs/vm_tlb/review_packs/AWMA_SIMULATION_FOUNDATION_174NEW_V1/
```

Required files at minimum:

```text
README.md
SOURCE_ANCHORS.md
SIMULATION_AUTHORITY_INVENTORY.tsv
SIM_INPUT_ADMISSION_SUMMARY.tsv
HISTORICAL_BACKFILL_SUMMARY.tsv
TELEMETRY_SCHEMA_AND_EXAMPLES.md
RUNTIME_BASELINE_STATUS.md
CALIBRATION_RESULTS.tsv  # if runtime available
RUNTIME_BLOCKER_AND_RECOVERY_PLAN.md  # if blocked
SIM_COMPAT_CAPTURE_CONSUMER_CONTRACT.md
CATALOG_SNAPSHOT_SUMMARY.md
TEST_AND_REGRESSION_SUMMARY.md
OPEN_ISSUES.md
SHA256SUMS
```

Codex report:

```text
docs/vm_tlb/codex_handoff/awma/SIMULATION_FOUNDATION_174NEW_REPORT.md
```

Commit/push all source/control-plane/review material and STOP.

## Small-issue policy

If a problem:

- does not alter scientific meaning/provenance;
- has an obvious safe repair;
- can be regression-tested locally;

fix it inline, document it in the review pack, and continue. Do not create a separate round merely for such cleanup.

## STOP boundary

STOP after the 174-new foundation is closed.

Do not:

- use 109 GPU;
- capture current-model simulator traces;
- start Qwen mechanism sweeps;
- start multi-model simulator campaigns;
- mass-rename C16 paths.

Those belong to later activated stages.
