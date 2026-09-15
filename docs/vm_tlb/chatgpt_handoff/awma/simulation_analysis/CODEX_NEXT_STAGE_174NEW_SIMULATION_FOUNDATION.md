# CODEX NEXT STAGE — 174-new AWMA Simulation Foundation

## Status

**ACTIVE / may run now in parallel with the ongoing Native Characterization work.**

Run on **174-new / port 2239** in a fresh worktree/branch and a new Codex window.

Suggested execution branch:

```text
hrl/awma-simulation-foundation-174new-v1
```

GPU use in this stage: **none**.

This Goal is intentionally independent from the active Qwen Decode/native-analysis worktree. Read `PARALLEL_EXECUTION_AND_AUTONOMOUS_RECOVERY.md` before execution.

## Objective

In one substantial solve-and-continue Goal, establish the consumer-side AWMA **Simulation Analysis** foundation far enough that the remaining producer-side dependency is a qualified simulator-compatible trace from 109.

Do not stop after inventory or design documents. Implement, test, catalog, recover/build what is safely recoverable, run bounded historical calibration where possible, and produce the next executable state.

The desired end state is:

```text
historical traceg + current simulation schemas/catalog
                    ↓
       admitted SIM_INPUT identity
                    ↓
       maintainable simulator baseline
                    ↓
      normalized TLB/PTW/Cache/DRAM/perf
                    ↓
 future SIM_COMPAT_CAPTURE_V1 can plug in
```

## Source anchors

Consume at least:

```text
AWMA simulation planning branch:
hrl/awma-simulation-analysis-plan-v1

Historical canonical inheritance:
7b6f2b88c36b4ed1bbdcd72761063f881c7b6c96

Historical review pack:
docs/vm_tlb/review_packs/C12_C15_174NEW_CANONICAL_INHERITANCE_V2/
```

The historical C12 identities remain references, not a requirement to resurrect the exact extinct binary:

```text
Framework: d64408a97d76a320a6d49468653d416e33677af8
Core:      57bb71ecd015b6ec0ab32e45b0815e5beaf69172
Binary:    2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a
```

Inspect newer accepted simulation-side infrastructure when useful, but do not silently reinterpret active Native evidence.

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
PARALLEL_EXECUTION_AND_AUTONOMOUS_RECOVERY.md
```

## Worktree and process isolation

Create a fresh worktree. Record:

```text
hostname
branch/base SHA
worktree path
node164 mount identity
current CPU/memory/load snapshot
available toolchains
other active Codex/worktree processes observed
```

Do not modify or clean another active worktree. Do not restart/kill the Qwen Goal, extension host, Codex app-server, shared SSHFS mount, or unrelated process.

Use bounded build concurrency and dedicated simulation build/scratch directories. If resource contention appears, lower concurrency/priority and continue rather than disturbing the Native Goal.

## Goal-mode operating rule

This stage is **solve problems, do not stop at the first problem**.

For a recoverable engineering blocker:

```text
diagnose
→ choose narrowest safe repair
→ implement in isolated branch/environment
→ test/regress
→ record evidence
→ continue
```

Do not ask for a separate round for small path, portability, dependency, parser, fixture, schema-plumbing, or deterministic-catalog issues whose intended semantics are clear.

`BLOCKED_ENVIRONMENT` may be used only for the specific runtime/build subphase after evidence-backed recovery attempts are exhausted. It must not terminate independent phases.

Escalate only for scientific-semantic ambiguity, destructive risk, identity changes, simulator architectural-semantic changes, or a truly unrecoverable permission barrier. Even then, finish every independent safe phase first.

## Phase A — Simulation authority inventory refresh

Refresh only what is needed for execution; do not repeat full archaeology.

Confirm authority and exact source/hash/status for:

```text
historical traceg/list inputs
historical C12 raw logs
M4C/M4B configs and controls
run_m4c_replay.sh
export_m4c_telemetry.py
summarize_m4c_runs.py
analyze_m4c_trace_locality.py
C12 formal baselines
node164 historical datasets
available framework/core/runtime source candidates
```

Produce a machine-readable inventory and distinguish:

```text
REUSE
REVALIDATE
REFERENCE_ONLY
UNAVAILABLE
```

## Phase B — Simulation identity and schemas

Implement/reuse versioned schemas for:

```text
SIM_INPUT
SIM_BASELINE
SIM_RUN
SIM_TELEMETRY_ROW
SIM_COMPARISON_ROW
```

If the larger AWMA unified-foundation implementation has not yet run, implement the narrow simulation subset now rather than waiting for another stage.

Required behavior:

- canonical serialization;
- deterministic SHA256 identities;
- conflict detection;
- explicit scientific/execution status;
- evidence origin preserved;
- UNKNOWN remains UNKNOWN;
- field order does not change identity;
- semantic identity changes do change identity.

## Phase C — Fail-closed simulation input admission

Build an admission path for simulator-native trace bundles:

```text
kernelslist.g
*.traceg.xz
required config/registration/object/address sidecars
manifest/receipt hashes
```

Admission must verify at least:

```text
all referenced files exist
hash closure
list/trace grammar
identity consistency
required sidecars
no partial/incomplete input accepted as formal
```

Issue `SIM_INPUT_ID` only after successful admission.

Mandatory negative case:

```text
current C16WARP1 / MREF-sharded evidence
→ NOT_PROVEN_LOSSLESS
→ no SIM_INPUT_ID
```

Never fabricate ordering/opcode/width/access/control semantics.

## Phase D — Historical adapter/backfill

Normalize at least:

```text
C12 Prefill F0
C12 Decode1 F0
one M4C control/reference asset
one M4B/Segment diagnostic asset when identity is sufficient
C13/C14 historical diagnostic records as references
```

Preserve exactly:

```text
HISTORICAL_RECORD origin
FORMAL/DIAGNOSTIC/PRE_FIX boundary
historical framework/core/binary identity
input/raw-log hashes
claim scope
```

Do not label inherited evidence as a fresh replay.

## Phase E — Telemetry normalization and analyzer layer

Implement a canonical Simulation Evidence normalization layer around current telemetry tools.

Prefer reuse/wrapping of existing proven parsers such as `export_m4c_telemetry.py` rather than duplicating parsing logic.

Normalized domains should include, when present:

```text
TLB
PTW/PWC/walker
L1/L2 cache
DRAM/memory traffic
queue/stall/exposure
cycles/IPC/performance
mechanism-specific counters
```

Required tests:

- valid historical log;
- missing/partial telemetry;
- conflicting/duplicate records;
- unknown metric namespace;
- deterministic normalized output;
- historical status preservation.

## Phase F — Runtime/toolchain recovery and `NEW_SIM_BASELINE_V1`

Actively work toward a maintainable current simulator baseline.

Do not spend the entire Goal trying to recover the historical exact binary. Follow the recovery ladder in `PARALLEL_EXECUTION_AND_AUTONOMOUS_RECOVERY.md`.

At minimum:

1. inventory all local/shared CUDA/toolchains, headers, compilers and existing binaries;
2. inventory relevant framework/core branches/checkouts and VM/TLB/PTW/cache hooks;
3. choose evidence-backed current source candidate(s);
4. use an isolated user-space/build environment when dependencies are missing and this is safe;
5. repair non-semantic portability/build issues inline and regression-test them;
6. attempt isolated build(s) with bounded retries/candidates;
7. freeze source/toolchain/config/binary SHA when a usable candidate is built;
8. prove required VM/TLB/PTW/cache config options and telemetry are recognized;
9. produce a deterministic baseline receipt.

A baseline may be called `NEW_SIM_BASELINE_V1` only after the qualification gates in `ACCEPTANCE_AND_REVIEW_REQUIREMENTS.md` pass.

If no runtime can be built after reasonable evidence-backed recovery, mark the runtime subphase `BLOCKED_ENVIRONMENT`, document exact exhausted paths and minimum next action, and continue Phases G–K insofar as they can operate on historical logs/fixtures.

Do not use the previously discovered non-matching EP-L2 binary as a formal baseline.

## Phase G — Bounded historical calibration

If a candidate runtime is available, run bounded anchors only:

```text
C12 Prefill F0
C12 Decode1 F0
```

Optionally one M4C control/reference after the first two are understood.

Validate in order:

```text
input identity
parser/record invariants
run completion
telemetry completeness
repeatability
historical-vs-new metric deltas
```

Classify results explicitly, e.g.:

```text
EXACT_REPLAY_PASS
NUMERICALLY_CLOSE_WITH_EXPLAINED_RUNTIME_DIFF
STRUCTURALLY_VALID_BUT_NOT_NUMERICALLY_EQUIVALENT
BLOCKED_INPUT_OR_RUNTIME
FAIL_UNEXPLAINED_MISMATCH
```

Do not run the complete historical C12 matrix.

## Phase H — `SIM_COMPAT_CAPTURE_V1` consumer contract

Implement the future producer contract now on CPU so 109 capture work will have a strict consumer target.

Machine-check at least:

```text
workload/target identity
kernel launch sequence
phase
stream/context
grid/block
static instruction identity / PC
opcode/access kind
memory space
byte width
warp/CTA
active mask
lane addresses
instruction/event order
sync/control markers
trace schema/version
producer source/binary SHA
object/address-context sidecars
ASID/epoch
VA width/page policy
payload/list/sidecar hashes
terminal completeness/drop/overflow
```

Create positive and negative synthetic fixtures.

Mandatory failures include:

```text
missing global/instruction order
missing width/access kind
missing required warp/CTA/mask semantics
incomplete terminal
nonzero drop/overflow
hash mismatch
```

This phase does **not** capture on GPU.

## Phase I — Catalog and node164 simulation namespace

Use only small metadata/dataset outputs under the existing AWMA logical namespace, for example:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
  catalog/awma/entries/
  catalog/awma/snapshots/
  derived/awma/simulation/inputs/
  derived/awma/simulation/telemetry/
  derived/awma/simulation/datasets/
  provenance/awma/simulation/
```

Do not reorganize large historical/native raw for cosmetics.

Create deterministic snapshots for at least:

```text
SIM_INPUTS
SIM_BASELINES
SIM_RUNS
SIM_EVIDENCE
```

Idempotent identical entries = no-op. Conflicting same-ID content = fail closed.

## Phase J — Integration/regression tests

Required tests include:

```text
identity determinism
schema positive/negative validation
input hash mismatch rejection
missing trace-list member rejection
C16WARP1 simulator-ineligible rejection
historical status preservation
telemetry normalization determinism
catalog idempotence/conflict detection
SIM_COMPAT_CAPTURE_V1 positive/negative fixtures
runtime receipt determinism when runtime exists
bounded repeated smoke consistency when runtime exists
```

Do not weaken existing C16/native/historical tests.

## Phase K — Handoff to producer and next simulation stage

Generate an executable producer-facing contract bundle for the later 109 Goal, containing:

```text
SIM_COMPAT_CAPTURE_V1 schema
consumer validator entrypoint
minimal valid fixture
negative fixtures
required sidecars
expected admission receipt
expected SIM_INPUT_ID derivation
example kernelslist/trace bundle layout
```

Also generate the exact next 174-new acceptance path for the first real current-model simulator trace.

Do not run the 109 capture in this Goal.

## Required review pack

Create:

```text
docs/vm_tlb/review_packs/AWMA_SIMULATION_FOUNDATION_174NEW_V1/
```

At minimum:

```text
README.md
SOURCE_ANCHORS.md
EXECUTION_CONTEXT.md
SIMULATION_AUTHORITY_INVENTORY.tsv
SIM_INPUT_ADMISSION_SUMMARY.tsv
HISTORICAL_BACKFILL_SUMMARY.tsv
TELEMETRY_SCHEMA_AND_EXAMPLES.md
RUNTIME_TOOLCHAIN_INVENTORY.tsv
RUNTIME_BASELINE_STATUS.md
CALIBRATION_RESULTS.tsv                 # when attempted
RUNTIME_BLOCKER_AND_RECOVERY_PLAN.md    # when any runtime gate remains blocked
SIM_COMPAT_CAPTURE_CONSUMER_CONTRACT.md
CATALOG_SNAPSHOT_SUMMARY.md
INLINE_RECOVERY_LOG.tsv
TEST_AND_REGRESSION_SUMMARY.md
OPEN_ISSUES.md
SHA256SUMS
```

Codex report:

```text
docs/vm_tlb/codex_handoff/awma/SIMULATION_FOUNDATION_174NEW_REPORT.md
```

Large raw logs/traces remain outside Git; store paths, sizes and SHA256 indexes.

## Completion states

Preferred:

```text
AWMA_SIMULATION_FOUNDATION_PASS
```

Allowed only if runtime remains genuinely unavailable after autonomous recovery but all independent mandatory gates pass:

```text
AWMA_SIMULATION_FOUNDATION_PASS_RUNTIME_BLOCKED
```

Failure is reserved for correctness/provenance violations or a blocker that prevents the mandatory non-runtime foundation from closing.

## STOP boundary

STOP only after the entire Goal has been carried through implementation, recovery attempts, tests, catalog/node164 metadata, review pack, commit and push.

Do not stop merely because one build attempt, path lookup, dependency, parser, or bounded calibration attempt fails.

Do not in this Goal:

- use 109 GPU;
- capture current-model simulator traces;
- start Qwen mechanism sweeps;
- run large historical matrices;
- run multi-model simulation campaigns;
- mass-rename C16 paths.
