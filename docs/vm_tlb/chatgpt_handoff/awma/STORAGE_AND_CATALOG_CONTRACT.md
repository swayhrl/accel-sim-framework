# AWMA Storage and Catalog Contract

## 1. One durable root

Continue using the existing canonical root:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
```

The path is a historical compatibility path. It is not renamed merely because the logical project name is now AWMA.

## 2. Logical AWMA namespaces

New AWMA metadata/derived outputs may use:

```text
provenance/awma/
catalog/awma/
derived/awma/native/
derived/awma/simulation/
derived/awma/crossview/
```

Existing authoritative data under paths such as:

```text
derived/parsed/
derived/features/
derived/datasets/
provenance/historical_snapshots/
```

remain valid and should be referenced through catalog entries/adapters. Do not bulk-move them during the foundation stage.

## 3. Raw data rule

Large raw data remains immutable-by-hash and outside Git.

Examples:

- NVBit/C16WARP1 payloads;
- traceg archives;
- Nsys/NCU reports;
- simulator raw logs;
- historical private export payloads.

Git stores schemas, code, manifests, receipts, indexes, and review packs.

## 4. Catalog model

Use immutable per-object/per-run catalog entries and deterministic snapshots.

Suggested structure:

```text
catalog/awma/
├── entries/
│   ├── workloads/
│   ├── targets/
│   ├── captures/
│   ├── sim_inputs/
│   ├── sim_baselines/
│   ├── sim_runs/
│   └── evidence/
└── snapshots/
    ├── AWMA_WORKLOADS.tsv
    ├── AWMA_CAPTURES.tsv
    ├── AWMA_SIM_INPUTS.tsv
    ├── AWMA_SIM_RUNS.tsv
    └── AWMA_EVIDENCE.tsv
```

Do not maintain a fragile single TSV by concurrent append. Snapshots are rebuilt deterministically from immutable entries.

## 5. Legacy adapter policy

Existing `C16_*` manifests, catalog entries, review packs, and historical C12–C15 indexes must be consumed through adapters that:

- preserve original path and SHA;
- add AWMA logical identity without rewriting source;
- keep original scientific status;
- record whether identity mapping is exact, partial, or historical-reference only.

Recommended adapter relation:

```text
EXACT_IDENTITY_MAPPING
PARTIAL_IDENTITY_MAPPING
HISTORICAL_REFERENCE_ONLY
NOT_MAPPABLE
```

## 6. Native derived data

Recommended new logical layout:

```text
derived/awma/native/
├── parsed/
├── features/
└── datasets/
```

The foundation stage should not duplicate existing large parsed data simply to fit this layout. Register legacy paths instead.

## 7. Simulation data

Recommended layout:

```text
derived/awma/simulation/
├── inputs/
├── runs/
├── telemetry/
└── datasets/
```

`inputs/` contains validated simulator-input metadata and receipts; large trace payloads may remain in canonical capture/archive locations if cataloged by hash.

`runs/` contains run manifests/links/metadata, not necessarily copied giant logs.

## 8. Cross-view data

Recommended layout:

```text
derived/awma/crossview/
├── datasets/
└── reports/
```

Cross-view outputs must reference source Native and Simulation evidence IDs, not copy or mutate them.

## 9. Project metadata

Create a small project descriptor under:

```text
provenance/awma/AWMA_PROJECT.json
```

with at least:

```text
project_name
project_slug
legacy_campaign_namespace
canonical_storage_root
identity_schema_version
catalog_schema_version
```

## 10. Historical C12–C15 data

The inherited canonical historical simulation namespace remains historical evidence. Do not merge its raw bytes into new production simulator runs.

Historical C12 F0 may be referenced as a formal baseline record; C13/C14 remain diagnostic; C15 remains static/diagnostic as already closed.

## 11. Storage safety

The node164 mount is accessed through the 174-new environment and must retain the established fail-closed discipline:

- write temp/partial first when large data transfer is involved;
- size/hash verify;
- admit/rename only after validation;
- never delete source merely because copy returned success;
- preserve receipts.

The current AWMA foundation stage is mostly metadata/small derived output and should not trigger new bulk transfer.