# Source Classification and Migration Policy

Every discovered historical asset must receive exactly one primary visibility/storage classification and one scientific-status classification.

## Visibility / storage classification

### `SHARED_VISIBLE_UNCHANGED`

Artifact is under a verified host-backed mount visible from both 2233 and 2239, normally `/root/share` or `/root/data`.

Required evidence:

- absolute path;
- `findmnt -T` / mount identity where applicable;
- file or directory size/count;
- for representative/critical files: SHA256;
- corresponding visibility from 174-new must be verified in Round 2 before old174 retirement.

Action: do not duplicate merely to move between containers. Later archive to node164 only if it is scientifically valuable and not already covered by the canonical archive.

### `OLD_DOCKER_PRIVATE_MUST_MIGRATE`

Artifact is scientifically important and exists only in the old Docker private layer or is not visible from 2239.

Typical locations:

```text
/workspace/...
/root/...        # excluding known shared mounts
/tmp/...
```

Action: Round 1 only inventories and hash-closes it. Round 2 uses copy-not-move into a dedicated node164 historical namespace, followed by destination rehash before acceptance.

### `GIT_AUTHORITY_ONLY`

Source/config/analyzer exists authoritatively in Git and filesystem copies are generated/mirrored/archival duplicates.

Action: retain Git path + commit SHA. Do not migrate duplicate source trees as authoritative code.

### `REDUNDANT_ARCHIVAL_COPY`

Byte-equivalent or semantically redundant copy of an already authoritative artifact.

Action: record lineage and duplicate relationship. No deletion in Round 1.

### `MISSING_OR_UNKNOWN`

Historical documentation or result references an artifact that cannot currently be located or whose identity cannot be proven.

Action: preserve the unresolved reference. Do not synthesize a replacement.

## Scientific-status classification

Use only:

```text
FORMAL
DIAGNOSTIC
PRE_FIX
OBSOLETE
UNKNOWN
```

Definitions:

- `FORMAL`: previously accepted scientific evidence tied to a known experiment identity;
- `DIAGNOSTIC`: debugging/qualification evidence not valid as final quantitative evidence;
- `PRE_FIX`: generated before a known correctness fix;
- `OBSOLETE`: intentionally superseded and should not be used for new conclusions;
- `UNKNOWN`: insufficient provenance to classify safely.

Do not upgrade an artifact from UNKNOWN/DIAGNOSTIC to FORMAL solely because it looks plausible.

## Required lineage identity

For every recoverable formal experiment, reconstruct as much of the following chain as evidence supports:

```text
trace/input
  -> trace identity / hash
  -> simulator config
  -> simulator/core/framework commit
  -> executable/build identity
  -> launch command / environment
  -> raw simulator output
  -> post-processing script + version
  -> derived CSV/JSON/TSV
  -> review pack / conclusion / plot/table
```

Unknown links must remain explicit `UNKNOWN`; never infer them from neighboring experiments.

## Round-2 archive targets

Expected long-term namespaces after joint review:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
├── provenance/historical_snapshots/old174_c12_c15_simulation/
├── derived/datasets/historical_simulation/
└── catalog/...
```

Current C16 Pipeline formal raw under `captures/raw/` must remain separate from historical simulator outputs.
