# C16 Data Pipeline — Discussion Reference

## Why this stage exists

C16 is moving from one-off GPU qualification to a repeatable cross-model memory-characterization workflow.

The stable division of responsibility is:

- node109 produces GPU-dependent evidence;
- new174 validates, catalogs and analyzes it;
- node164 stores large raw/derived scientific data;
- GitHub stores the control plane and auditable metadata.

The data plane must make later TLB/Cache conclusions traceable back to exact model, input, runtime, profiler/tracer and raw-artifact identities.

## Why ad-hoc rsync is insufficient

A successful copy alone does not prove scientific admission. Every run needs an explicit lifecycle:

```text
CAPTURING
-> LOCAL_CLOSED
-> READY_TO_TRANSFER
-> TRANSFERRING
-> REMOTE_HASH_VERIFIED
-> TRANSFER_ACKED
-> ANALYSIS_READY
-> PARSED
-> FEATURED
-> DATASET_ADMITTED
```

No source deletion follows mere rsync success.

## Storage constraints

new174's local filesystem is nearly full, so large traces must not be staged on its overlay/root-data filesystem. The node164 SSHFS mount is the intended large-data destination.

SSHFS is not assumed to provide every local-ext4 durability/atomicity semantic. Phase B therefore qualifies the actual usable subset and records limitations rather than silently assuming them.

Required semantics to probe include:

- write/read/reopen/hash;
- file `fsync` where supported;
- same-mount rename visibility;
- no-overwrite/collision behavior;
- bounded medium-file write/reopen/hash;
- directory fsync support or lack thereof;
- cleanup of test fixtures.

If directory fsync or `renameat2(RENAME_NOREPLACE)` is unsupported, record the limitation. Phase C must then implement an explicit collision-safe protocol using immutable RUN_IDs, destination-exists fail-closed checks and receipts/markers. Do not weaken hash verification.

## Canonical data layout

The long-term root is frozen by Phase B, with intended structure:

```text
inbox/
raw/
provenance/
parsed/
features/
datasets/
catalog/
  entries/
  snapshots/
reports/
quarantine/
legacy/
tmp/
```

Raw scientific evidence is immutable after admission.

Catalog writes should be append-safe by immutable per-run entries under `catalog/entries/`; TSV/Parquet catalog files are deterministic snapshots, not concurrent append logs.

## Historical-data policy

Old174 remains a historical source only.

Do not bulk-copy all of `/root/share/c16_recovery_v3` or `/workspace/c16_exchange/autodl_wave1` into node164 merely for tidiness. Curate only artifacts that have a concrete future scientific role and close source/destination size+SHA.

The first historical archive candidate is the ~763.9 MB minimum 3090 comparison set documented by the old174 handover. It is not needed for Phase B.

## RTX4080 R5 policy

R5 does not need to be rerun for the data-plane project.

Its existing artifacts on node109 are imported later by a legacy-import manifest after the R5 provenance-only closeout is accepted. Copying must not alter producer identity: the data remains `producer=node109/RTX4080` after archival on node164.

## Future multi-model policy

Qwen2.5 historical input bindings are useful authorities, but a future node109 capture must bind to the exact local input receipt used by that run. Old174 absolute paths are catalog/provenance references, not execution paths on node109.

Qwen3-8B and DeepSeek-V2-Lite require new prospective input authorities before capture. Do not manufacture them as historical bindings.

## Phase boundaries

Phase B is storage admission only.

Phase C is transfer-protocol implementation with synthetic fixtures only.

Formal scientific raw transfer/import starts only after both phases are reviewed.
