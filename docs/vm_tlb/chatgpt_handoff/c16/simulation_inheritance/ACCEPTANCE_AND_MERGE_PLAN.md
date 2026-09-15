# Acceptance and Merge Plan

This file defines what must be true before old174 can be considered fully retired from the C12–C15 simulation-analysis workflow.

## Round 1 — parallel inventory

Two independent branches/worktrees run in parallel:

### Old174

Produces authoritative filesystem/provenance inventory.

Expected branch suggestion:

```text
hrl/c12-c15-old174-source-archaeology-v1
```

### 174-new

Produces Git/shared-storage/current-interface inventory.

Expected branch suggestion:

```text
hrl/c12-c15-174new-repo-shared-inventory-v1
```

Neither branch migrates large files or reruns long simulations.

## ChatGPT joint review gate

ChatGPT must compare the two review packs and build a reconciliation table with one row per important artifact/experiment.

Required reconciliation fields:

```text
stage
experiment_id
scientific_status
old174_path
174new_visible_path
visibility_class
trace_identity
config_identity
framework/core identity
raw_output identity
derived_result identity
migration_required
migration_destination
anchor_replay_required
open_issue
```

A historical experiment cannot be accepted as inherited if its conclusion is known but the supporting artifact chain is unresolved, unless it is explicitly retained as historical `UNKNOWN`/`UNRESOLVED` rather than FORMAL.

## Round 2 — migration and inheritance

Round 2 is expected to run primarily on 174-new, with old174 used only as a source for any `OLD_DOCKER_PRIVATE_MUST_MIGRATE` assets.

### Migration principles

- copy-not-move;
- source untouched;
- source inventory + SHA before copy;
- destination inventory + SHA after copy;
- no overwrite of an existing destination with mismatched identity;
- generate archive receipt;
- keep old absolute path in provenance metadata;
- never mix historical simulator output with current C16 `captures/raw/`.

### Expected node164 namespace

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
├── provenance/historical_snapshots/old174_c12_c15_simulation/
│   ├── traces/
│   ├── run_outputs/
│   ├── logs/
│   ├── receipts/
│   └── lineage/
│
└── derived/datasets/historical_simulation/
    ├── c12/
    ├── c13/
    ├── c14/
    └── c15/
```

The exact sublayout may be refined after Round-1 evidence, but historical and current formal-capture namespaces must remain distinct.

## Historical anchor replay

Do not rerun every experiment.

Select a bounded anchor set that covers the important analysis dimensions discovered in Round 1, for example:

- one representative TLB/PTW baseline;
- one Segment-related run;
- one Selective-related run;
- one Cache-focused run;
- one historically important Prefill/Decode contrast if applicable.

For each anchor:

1. verify exact trace/config identity;
2. run with current inherited simulator code only if the environment is sufficiently reproducible;
3. compare key outputs against historical formal result;
4. classify compatibility as:

```text
EXACT_REPLAY_PASS
NUMERICALLY_EQUIVALENT_WITH_DOCUMENTED_DIFF
NOT_REPLAYABLE_MISSING_ENVIRONMENT
NOT_REPLAYABLE_MISSING_ARTIFACT
FAIL_RESULT_MISMATCH
```

Do not silently change simulator parameters to make a result match.

## Inheritance acceptance criteria

Old174 simulation-analysis responsibility can be retired only when all of the following are satisfied:

1. all important historical experiments are present in a lineage catalog or explicitly marked unresolved;
2. all scientifically valuable old-container-private artifacts are safely copy-not-move archived with source/destination SHA closure;
3. shared-mounted artifacts have been independently verified visible from 174-new;
4. Git-owned code/config authority is identified and duplicate filesystem source trees are not treated as authoritative;
5. historical FORMAL / DIAGNOSTIC / PRE_FIX / OBSOLETE boundaries are preserved;
6. a bounded historical anchor replay or equivalent compatibility validation has been completed where feasible;
7. 174-new has documented entry points for TLB/PTW/Segment/Selective/Cache analysis;
8. the remaining interface gap from current C16 formal traces/derived fingerprints to simulator analysis is explicit;
9. no critical C12–C15 asset remains only in an untracked old174 private path without a migration plan;
10. final review pack and SHA256SUMS are complete.

## Final decision vocabulary

Use only:

```text
C12_C15_SIMULATION_INHERITANCE_PASS
C12_C15_SIMULATION_INHERITANCE_PASS_WITH_UNRESOLVED_HISTORICAL_GAPS
C12_C15_SIMULATION_INHERITANCE_BLOCKED
```

Only the first two allow old174 to stop being a routine dependency. In the second case, unresolved gaps must be documented and must not be silently used for new scientific claims.
