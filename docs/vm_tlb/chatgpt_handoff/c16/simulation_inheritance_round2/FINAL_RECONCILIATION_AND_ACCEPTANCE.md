# Final reconciliation and acceptance plan

This file defines how ChatGPT will judge the two Round-2 Goals after both stop.

## Inputs to reconcile

- old174 private closeout review pack/commit
- 174-new canonical inheritance review pack/commit
- shared exchange receipts
- node164 canonical archive receipts
- historical Git authority

## Reconciliation table

The destination review must produce a single table with at least:

- lineage_id
- stage
- scientific_status
- trace_identity
- config_identity
- framework_sha
- core_sha
- binary_identity
- source_raw_path
- canonical_node164_path
- source_sha_or_tree_sha
- node164_sha_or_tree_sha
- raw_output_identity
- derived_result_identity
- replay_status
- current_reuse_status
- unresolved_gap

## Acceptance dimensions

### A. Asset preservation

PASS when every scientifically valuable historical payload is one of:

- canonicalized in node164 and independently hash-closed;
- already canonical/byte-identical and referenced by receipt;
- Git-authoritative and intentionally not duplicated;
- explicitly unavailable with evidence.

No important asset may remain merely `UNKNOWN` because a path was never inspected.

### B. Provenance preservation

PASS when C12-C15 conclusions are traceable to their exact historical authority and scientific statuses are not silently upgraded.

### C. Replay capability

At least one of these must be true:

- exact historical simulator binary is preserved/runnable;
- compatibility runtime is reproducibly rebuilt and a bounded historical replay passes;
- replay remains blocked by a precisely documented external/toolchain issue while trace parser/authority closure passes.

### D. Modern C16 boundary

PASS only if the system clearly distinguishes:

1. current C16 native/offline footprint analysis;
2. historical traceg-based simulator replay;
3. future simulator-compatible capture requirements.

No synthetic cross-shard ordering or fabricated memory-width semantics are allowed.

## Final possible decisions

- `C12_C15_SIMULATION_INHERITANCE_PASS`
- `C12_C15_SIMULATION_INHERITANCE_PASS_WITH_REPLAY_ENVIRONMENT_LIMITATION`
- `C12_C15_SIMULATION_INHERITANCE_PASS_WITH_IRRECOVERABLE_HISTORICAL_GAP`
- `C12_C15_SIMULATION_INHERITANCE_FAIL`

## Old174 retirement condition

Old174 can be retired from routine C12-C15 work only after:

- private-path closeout PASS;
- any private-only scientific payload has a hash-verified canonical copy outside old174;
- node164 canonical historical manifests close;
- no pending migration action points to old174-private storage.

Retirement does not authorize deletion of old data; deletion/cleanup requires a separate explicit task.
