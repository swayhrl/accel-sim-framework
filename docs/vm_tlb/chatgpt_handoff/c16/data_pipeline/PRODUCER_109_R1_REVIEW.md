# ChatGPT Review — C16 Pipeline V1 Producer 109 R1

Ownership: ChatGPT
Reviewed branch: `hrl/c16-data-pipeline-v1-producer-109-r1`
Reviewed commit: `805522f1b0b34ca69d25c3d5b5204324668a328a`

## Decision

`PRODUCER_PREP_R1_NOT_ACCEPTED`

The R1 branch is correctly isolated and performed no remote/GPU mutation, but it does not implement the frozen producer contract sufficiently to authorize real cross-node integration.

## Accepted parts

- branch is exactly one commit ahead of coordination `8ad5d0feeb15e4b8deb79f01d91cd1ccb9dff828`;
- 10k generated RUN_IDs were unique in the synthetic test;
- artifact inventory computes SHA256 and rejects symlinks;
- simple ready-destination collision is rejected;
- no 174-new contact, no real transfer, no scientific workload rerun, no source deletion occurred.

## Blocking findings

### B1 — Public CLIs are stubs

The required scripts:

- `generate_run_id.py`
- `finalize_capture.py`
- `publish_capture.py`
- `verify_remote_ack.py`
- `cleanup_transferred.py`

contain only imports and expose no functional CLI. `publish_capture.py` therefore does not construct or dry-run the required rsync transport at all.

### B2 — Schemas are vacuous

`run_manifest.schema.json`, `transfer_ack.schema.json`, and `catalog_entry.schema.json` require only `schema_version` and do not enforce the frozen Pipeline V1 contract.

### B3 — finalize is not sufficiently fail-closed

Current `finalize()` does not validate:

- required top-level/semantic manifest fields;
- malformed model/input/scenario/runtime/capture identity;
- required artifact declarations;
- manifest-vs-filesystem artifact mismatch;
- exact schema;
- local close receipt;
- atomic/fsync durability of manifest/READY before promotion.

It only requires that at least one regular artifact exists, scientific_status is in the enum, no symlink is seen, and ready destination is absent.

### B4 — ACK binding is incomplete

Current ACK validation checks only:

- `verification_status=PASS`;
- source manifest SHA;
- destination path.

It does not bind `run_id`, full ACK schema, catalog entry SHA, file count/total bytes, destination verification SHA, or expected destination identity. It also does not perform/verify the required ready -> transferred state transition.

### B5 — cleanup contract is not implemented

`cleanup_transferred.py` is a stub. The required default non-destructive inventory/report mode and explicitly gated deletion mode are absent.

### B6 — Claimed T1–T13 coverage is not evidenced

The single unit test exercises only:

- 10k RUN_ID uniqueness;
- one happy-path finalize;
- one ready collision;
- one minimal ACK happy path.

It does not independently test the required T1–T13 matrix (missing artifact, mutation/hash mismatch, symlink, invalid schema/status, deterministic ordering, publish dry-run, malformed ACK, wrong manifest SHA, real state transition, cleanup non-deletion, etc.). `TEST_MATRIX.tsv` therefore overstates coverage.

### B7 — Samples do not conform to the frozen contract

The sample RUN_MANIFEST omits required producer/git/model/input/scenario/runtime/capture identity, and the sample ACK omits multiple required fields from `PIPELINE_V1_CONTRACT.md`.

## Consequence

- R1 must not be used for real 109 -> 174-new transfer.
- 174-new may continue receiver-side implementation locally, but must STOP before cross-node transfer until Producer R2 passes review.
- No scientific evidence is invalidated because R1 did not perform real transfer or GPU work.
