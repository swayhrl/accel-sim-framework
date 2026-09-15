# Current State — C12–C15 Simulation Inheritance

## Known host/container topology

Old Docker:

```text
ssh root@10.208.130.174 -p 2233
```

New analysis Docker:

```text
ssh root@10.208.130.174 -p 2239
```

Known shared mounts:

```text
/root/share
/root/data
```

The administrator mapped these paths from both containers to the same host-backed storage. This must be verified with filesystem evidence, not merely assumed for every historical path.

Container-private paths such as `/workspace`, non-mounted `/root/*`, `/tmp`, and other overlay paths may differ between 2233 and 2239.

## Existing C16 long-term root

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
```

Current structure already separates:

- canonical reusable model assets;
- historical provenance snapshots;
- current Pipeline captures;
- derived analysis;
- catalog.

The existing C16 model/data migration is **not** to be redone by this task.

## Current ownership state

### Already owned by 174-new

- current C16 raw-capture ingest and Pipeline V1;
- C16WARP1 / sharded analysis implementation;
- page/cache-line fingerprinting;
- current derived-data / catalog infrastructure;
- Git repository and current analysis implementation.

### Available in Git but not yet formally inherited as historical simulation baseline

Historical TLB/Cache simulation code/configs/analyzers are believed to remain in the repository, including VM/TLB replay/finalize/analyzer utilities and simulator configuration material. Their exact stage coverage, commit authority and continued usability must be inventoried rather than assumed.

### Not yet formally inherited

The following C12–C15 historical simulation lineage has not yet been fully reconstructed and accepted on 174-new:

- exact trace inputs used for each formal simulation experiment;
- exact simulator/framework/core/config SHAs;
- exact launch commands and runtime environment;
- raw simulation output directories and logs;
- post-processing inputs and outputs;
- formal CSV/JSON/TSV summaries;
- result-to-conclusion mapping;
- FORMAL / DIAGNOSTIC / PRE_FIX / OBSOLETE classification;
- whether each filesystem artifact is shared-visible, old-container-only, redundant, or missing.

## Critical preservation rule

No historical source directory may be deleted, moved, rewritten, compressed in place, or cleaned during Round 1.

Round 1 is inventory + provenance reconstruction only.

## Mainline isolation

This archaeology work must not interrupt or redefine the current Qwen0/RTX4080 formal-capture and analysis mainline.

No GPU workload is required for Round 1.
