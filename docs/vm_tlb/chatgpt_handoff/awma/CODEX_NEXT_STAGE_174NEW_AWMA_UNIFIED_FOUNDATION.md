# CODEX NEXT STAGE — 174-new AWMA Unified Foundation V1

## Status

Executable stage specification.

Run on **174-new / port 2239** in a fresh worktree/branch.

Suggested branch:

```text
hrl/awma-unified-foundation-174new-v1
```

This stage is CPU/filesystem-only. It must not start new GPU capture and must not start a long production simulator sweep.

## Objective

Establish the machine-checkable common foundation for **AI Workload Memory Analysis (AWMA)** so that existing Native evidence and historical Simulation evidence can coexist under one identity/catalog architecture, while preserving their different scientific meanings.

The stage should do as much implementation and bounded qualification as can be done safely in one round:

1. implement common AWMA identity/schema/catalog infrastructure;
2. add non-destructive adapters for existing C16 and historical C12–C15 assets;
3. define/validate Native, Simulation, and Cross-view normalized dataset schemas;
4. backfill a small but representative real catalog from already accepted assets;
5. freeze a machine-checkable `SIM_COMPAT_CAPTURE_V1` contract;
6. attempt bounded bring-up of a maintainable new simulator baseline using currently available source/toolchain, without treating environment absence as a reason to skip the rest of the stage;
7. generate the next-wave execution inputs for 109 capture and 174-new simulator qualification.

## Source anchors to consume

### Coordination

Use the AWMA coordination branch containing this file as the authoritative task definition.

### Historical simulation inheritance

Canonical inheritance commit:

```text
7b6f2b88c36b4ed1bbdcd72761063f881c7b6c96
```

Consume its review pack and node164 historical namespaces as historical authority.

### Current Native/C16 references

Inspect existing C16 analysis code and accepted review packs, including at least:

```text
util/vm_tlb/c16/analysis/c16_analysis.py
util/vm_tlb/c16/formal_campaign/
docs/vm_tlb/review_packs/C16_FIRST_V2_FORMAL_INGEST_174NEW_V1/
```

Fetch/inspect the latest relevant 109/174 C16 branches by explicit SHA where useful, but do not silently merge unreviewed scientific changes into this foundation branch.

Known 109 Decode branch anchor at handoff creation:

```text
hrl/c16-qwen0-decode-formal-109-v3
20ee2e015d3b3eb72b67d03657242887932a925d
```

Treat newer pushes as discoverable evidence, not automatically accepted state.

## Worktree isolation

Create a fresh worktree. Do not modify a worktree that is running or tied to another experiment.

Record:

```text
base commit
branch
worktree path
hostname
mount identity for node164 root
```

in the review pack.

## Allowed scope

### Repository

New code may be added under a logical AWMA namespace, preferably:

```text
util/vm_tlb/awma/
```

Recommended shape:

```text
util/vm_tlb/awma/
├── common/
│   ├── identity.py
│   ├── schemas.py
│   ├── catalog.py
│   ├── status.py
│   └── legacy_adapters.py
├── native/
│   └── normalize.py
├── simulation/
│   ├── normalize.py
│   ├── sim_input.py
│   └── baseline.py
└── crossview/
    ├── align.py
    └── build_dataset.py
```

This is a preferred logical structure, not a requirement to rewrite stable existing tools. Reuse existing C16/simulator parsers where appropriate.

### Schemas

Create versioned machine-readable schemas for at least:

```text
AWMA_PROJECT
AWMA_WORKLOAD
AWMA_TARGET
AWMA_CAPTURE
AWMA_SIM_INPUT
AWMA_SIM_BASELINE
AWMA_SIM_RUN
AWMA_EVIDENCE_ROW
AWMA_CROSSVIEW_ROW
```

JSON Schema is preferred if practical. Every schema must have a version field and strict required identity/provenance fields.

### Node164 metadata

Small metadata namespaces may be created:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
  provenance/awma/
  catalog/awma/entries/
  catalog/awma/snapshots/
  derived/awma/native/datasets/
  derived/awma/simulation/datasets/
  derived/awma/crossview/datasets/
```

Do not move existing large raw/parsed historical data into these directories merely for organization.

## Explicitly forbidden scope

Do **not**:

- rename `/data/c16`, `c16_ai_workload`, or existing C16 Git paths;
- mutate accepted C16 raw/capture bytes;
- fabricate missing C16WARP1 temporal order/opcode/width/access semantics;
- issue a `SIM_INPUT_ID` for existing MREF-sharded C16 data unless a complete lossless proof is discovered and independently validated;
- reclassify C13/C14 as formal;
- promote C15 static evidence into dynamic evidence;
- copy large historical trees again when the canonical inheritance already references/archives them;
- run a new GPU workload;
- run a large mechanism sweep;
- install/upgrade system-wide packages in a way that risks unrelated projects without documenting necessity and isolation.

## Phase A — Project descriptor and identity implementation

Implement canonical JSON serialization and SHA-based IDs according to `IDENTITY_AND_EVIDENCE_CONTRACT.md`.

Required functions/tests should cover:

```text
compute_workload_id
compute_target_id
compute_capture_id
compute_sim_input_id
compute_sim_baseline_id
compute_sim_run_id
```

Requirements:

- deterministic across re-read;
- full SHA256 retained;
- human-readable shortened form optional;
- timestamp excluded from workload semantics;
- UNKNOWN/null stable rather than guessed;
- schema version included;
- field-order changes do not change identity;
- semantic field changes do change identity.

Create node164 project descriptor:

```text
provenance/awma/AWMA_PROJECT.json
```

Hash-close it.

## Phase B — Status/evidence model

Implement explicit separation of:

```text
scientific_status
execution_status
evidence_origin
sim_input_status
join_relation
```

Enforce allowed enums centrally.

At minimum:

```text
evidence_origin:
  REAL_GPU
  SIMULATOR
  CROSSVIEW_DERIVED
  HISTORICAL_RECORD

scientific_status:
  FORMAL
  DIAGNOSTIC
  PRE_FIX
  OBSOLETE
  UNKNOWN
```

Unknown/unsupported values must fail closed in formal normalization paths.

## Phase C — Legacy adapters

Implement adapters that produce AWMA metadata from existing authority without rewriting source files.

### C16/native adapter

Support representative existing artifacts such as:

- historical RTX3090 Q2 Prefill/Decode native parsed/fingerprint assets;
- first V2 formal Qwen0 Prefill Attention/GEMM ingest;
- any already accepted Qwen0 Decode artifact visible by the time this Goal runs, but only if its producer/consumer closure is explicit.

For each mapping record:

```text
source path
source SHA
legacy identity
AWMA identity
mapping relation
scientific status
claim boundary
```

### Historical simulation adapter

Support at least:

- C12 Prefill F0;
- C12 Decode F0;
- one M4C/M4B diagnostic archive;
- C13/C14 as diagnostic historical records.

Preserve historical status exactly.

## Phase D — Catalog implementation

Implement immutable per-entity catalog entries and deterministic snapshot rebuild.

Minimum entry types:

```text
workload
target
capture
sim_input
sim_baseline
sim_run
evidence
```

Required behavior:

- deterministic sorting;
- duplicate identity with identical content = idempotent/no-op;
- duplicate identity with conflicting content = fail closed;
- snapshots rebuilt from entries, never append-mutated as authority;
- every entry has source/provenance hashes;
- no scan of giant raw payload content is required merely to list catalog entries when authoritative receipts already provide hashes.

Generate representative snapshots under `catalog/awma/snapshots/`.

## Phase E — Native normalized dataset schema

Define and implement a normalized Native evidence row format.

Minimum fields:

```text
WORKLOAD_ID
TARGET_ID
CAPTURE_ID
evidence_origin = REAL_GPU
scientific_status
phase/decode-step/semantic-stratum
metric_name
metric_value
unit
source_artifact_sha256
analyzer/parser identity
claim_scope
```

Normalize a bounded representative subset of existing accepted Native evidence. Do not regenerate every raw trace.

Include examples for:

- page footprint;
- cache-line footprint;
- object attribution when valid;
- NCU metric or explicit unavailable/unknown example;
- executed/zero static-MREF completeness where applicable.

## Phase F — Simulation normalized dataset schema

Define and implement Simulation evidence rows.

Minimum fields:

```text
WORKLOAD_ID/TARGET_ID if exact mapping exists
SIM_INPUT_ID or historical input identity
SIM_BASELINE_ID or historical baseline reference
SIM_RUN_ID where runnable/current
mechanism/arm identity
evidence_origin = SIMULATOR or HISTORICAL_RECORD
scientific_status
metric_name/value/unit
source log/receipt SHA
simulator/analyzer identity
claim_scope
```

Backfill at least historical C12 Prefill/Decode F0 records from canonical historical datasets without pretending they are newly replayed.

## Phase G — Cross-view alignment and dataset skeleton

Implement a fail-closed join function.

It must:

- join Native and Simulation rows by explicit identity/lineage;
- emit `join_relation`;
- reject direct calibration for `UNALIGNED`;
- never match solely on similar filenames/kernel names;
- preserve both metric origins.

Create a bounded example dataset demonstrating:

1. one valid same-workload/different-capture relation if available;
2. one historical-reference relation;
3. one intentionally unaligned case that is rejected for direct quantitative comparison.

It is acceptable that no current C16 Qwen capture has a valid Simulation counterpart yet. The schema must represent this as `NOT_SELECTED` or `NOT_PROVEN_LOSSLESS`, not fabricate a join.

## Phase H — `SIM_COMPAT_CAPTURE_V1` machine-checkable contract

Convert the inherited prose future-capture contract into a precise schema/specification.

The contract must cover, at minimum:

```text
workload/target identity
kernel launch sequence
phase
stream/context identity
grid/block
static instruction identity / PC
opcode/access kind
memory space
byte width
warp ID
CTA ID
active mask
lane addresses
instruction/event order
synchronization/control markers
trace schema/version
producer source/binary SHA
object/address-context sidecars
ASID/epoch
VA width/page policy
payload/list/sidecar SHA256
terminal completeness/drop/overflow state
```

State exactly which fields are needed for:

- parser validity;
- coalescing fidelity;
- TLB/PTW fidelity;
- cache/timing fidelity;
- object attribution.

Create synthetic CPU fixtures that demonstrate:

- valid minimal input passes;
- missing ordering fails;
- missing width/access kind fails for simulation eligibility;
- incomplete terminal/overflow fails;
- deterministic re-read produces the same identity.

Do not instrument the GPU in this stage.

## Phase I — New simulator baseline bounded bring-up

The purpose is to learn whether 174-new can begin forming a maintainable baseline now, not to reproduce the historical binary exactly.

Perform a bounded audit/attempt:

1. inventory available CUDA/toolchain locations locally and on already mounted/shared paths;
2. inventory current framework/core source candidates;
3. choose a clearly documented current candidate for future `NEW_SIM_BASELINE_V1`;
4. if a compatible local toolchain is available, attempt an isolated build;
5. if build succeeds, run only a tiny historical traceg/parser/simulator smoke and record binary/config hashes;
6. if local toolchain is absent, close as `BLOCKED_ENVIRONMENT` for runtime build while still completing all other phases.

Do not spend the entire Goal repeatedly fighting an absent nvcc. After reasonable bounded attempts, preserve the exact requirement/toolchain gap and continue.

Do not claim compatibility from the previously found non-matching EP-L2 binary.

## Phase J — Regression and tests

Required CPU tests:

- identity determinism;
- schema validation positive/negative cases;
- status enum fail-closed behavior;
- legacy adapter exact/path/hash preservation;
- catalog idempotence/conflict detection;
- cross-view alignment acceptance/rejection;
- sim-input eligibility negative tests for existing C16 MREF evidence;
- synthetic `SIM_COMPAT_CAPTURE_V1` validity tests.

Preserve existing C16 analysis regressions, especially historical Q2 anchors and any already accepted V2 closure tests that are available in the branch/worktree.

Do not weaken old tests to make new code pass.

## Phase K — Required node164 outputs

At minimum create/hash-close small outputs:

```text
provenance/awma/AWMA_PROJECT.json
catalog/awma/snapshots/AWMA_WORKLOADS.tsv
catalog/awma/snapshots/AWMA_CAPTURES.tsv
catalog/awma/snapshots/AWMA_SIM_INPUTS.tsv
catalog/awma/snapshots/AWMA_SIM_RUNS.tsv
catalog/awma/snapshots/AWMA_EVIDENCE.tsv
```

If the actual implementation uses JSON/Parquet additionally, retain a human-reviewable TSV/JSON summary.

## Acceptance criteria

The stage is `PASS` only if all of the following are true:

1. AWMA project descriptor and schema versions are explicit.
2. Identity functions are deterministic and tested.
3. Native/Simulation/Cross-view evidence are structurally distinct.
4. Existing C16 data is not renamed or mutated.
5. Existing C16WARP1 is explicitly non-simulator-eligible unless proven otherwise.
6. At least representative Native and historical Simulation assets are successfully adapted/cataloged.
7. Catalog conflict/idempotence behavior is tested.
8. Cross-view alignment fails closed on unaligned evidence.
9. `SIM_COMPAT_CAPTURE_V1` is machine-checkable and has negative fixtures.
10. Historical scientific status boundaries remain unchanged.
11. Existing Q2/native regressions still pass.
12. Review pack and node164 metadata outputs are hash-closed.

Simulator runtime build may be `BLOCKED_ENVIRONMENT` without failing the entire stage **only if** the toolchain blocker is exact, bounded attempts are documented, and all non-runtime acceptance criteria pass. In that case the overall stage may be:

```text
AWMA_UNIFIED_FOUNDATION_PASS_SIM_RUNTIME_BLOCKED
```

## Required review pack

Create:

```text
docs/vm_tlb/review_packs/AWMA_UNIFIED_FOUNDATION_174NEW_V1/
```

Required files:

```text
README.md
SOURCE_ANCHORS.md
IMPLEMENTATION_SUMMARY.md
SCHEMA_INDEX.tsv
IDENTITY_TESTS.md
LEGACY_MAPPING_SUMMARY.tsv
CATALOG_SNAPSHOT_SUMMARY.md
NATIVE_EVIDENCE_EXAMPLES.tsv
SIMULATION_EVIDENCE_EXAMPLES.tsv
CROSSVIEW_ALIGNMENT_TESTS.tsv
SIM_COMPAT_CAPTURE_V1.md
SIM_COMPAT_CAPTURE_V1.schema.json
SIM_RUNTIME_BRINGUP.md
VALIDATION_SUMMARY.md
OPEN_ISSUES.md
NEXT_WAVE_READINESS.md
SHA256SUMS
```

Large external artifacts remain outside Git and are referenced by path/hash.

## Codex report

Create/update:

```text
docs/vm_tlb/codex_handoff/awma/LATEST_REPORT.md
```

It must state:

```text
Stage
Status
Branch
Final commit
Node164 metadata roots
What was implemented
What existing evidence was mapped
Simulator-runtime readiness
109 SIM_COMPAT_CAPTURE readiness
Open correctness-relevant issues
Recommended next action
Review-pack entry point
```

## Git requirements

- commit semantically;
- use explicit paths rather than blind `git add -A` where practical;
- `git diff --check`;
- clean final worktree;
- push branch;
- report final SHA.

## STOP boundary

STOP after the unified foundation closeout.

Do not begin GPU `SIM_COMPAT_CAPTURE_V1` production capture.
Do not begin a production Accel-Sim mechanism sweep.
Do not expand to unrelated models/backends merely because the infrastructure exists.