# PolyBench bounded range protocol — copy only

This adapter serves only the source-requested immutable `polybench.tgz`, size 17943970556 B and SHA256 `9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca`. Original tar and both closeout stages stay SOURCE_KEEP. Neither a range receipt nor a whole archive receipt authorizes scientific source release.

The same single bridge window is used. Each `PB_CHUNK_000` through `PB_CHUNK_034` has exactly one `files/payload.bin`, at most 524288000 B. Last range length is 118178556 B. Offset is index times 524288000; ranges must be ordered, gap-free and nonoverlapping. Share must remain >=40GiB; the source must reserve space for the next physical batch. Transfer payload is limited to 30MiB/s. No second rsync or other data worker runs alongside it.

Before any range is received, Source Ops publishes and target independently GitHub-pins `POLYBENCH_SOURCE_COPY_SCOPE.json`. Required fields:

```json
{
  "source_archive_path": "/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz",
  "source_archive_size_bytes": 17943970556,
  "source_archive_sha256": "9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca",
  "source_archive_identity": {"device":156,"inode":33890200,"nlink":1,"size_bytes":17943970556,"mtime_ns":"ACTUAL_INTEGER","ctime_ns":"ACTUAL_INTEGER"},
  "owner": "ACTUAL_REVIEWED_OWNER",
  "owner_authorization": "COPY_OK_ONLY",
  "no_active_readers_or_writers": true,
  "original_archive_retained": true,
  "both_closeout_stage_roots_retained": true,
  "source_action": "SOURCE_KEEP",
  "source_release_authorized": false
}
```

Placeholders must be replaced with actual evidence. If that copy qualification cannot be established, do not stage data; report the precise scope issue. Preserve active DTC-L1/EP-L2 and other projects. Original archive references/future closeout consumers remain a separate source release gate.

Each atomic bridge `PB_CHUNK_NNN_READY.json` uses this schema, with actual numeric values/digests:

```json
{
  "schema":"STORAGE_OPS_V7_ARCHIVE_RANGE_READY",
  "batch_id":"PB_CHUNK_000",
  "project":"Decoupled-L2",
  "source_receipt_commit":"SCOPE_GIT_COMMIT_40_HEX",
  "source_scope_sha256":"EXACT_SCOPE_SHA256_64_HEX",
  "source_archive_path":"/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz",
  "source_archive_size_bytes":17943970556,
  "source_archive_sha256":"9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca",
  "source_archive_identity":{"device":156,"inode":33890200,"nlink":1,"size_bytes":17943970556,"mtime_ns":"ACTUAL_INTEGER","ctime_ns":"ACTUAL_INTEGER"},
  "source_archive_identity_rechecked_before_after_stage":true,
  "source_action":"SOURCE_KEEP",
  "source_release_authorized":false,
  "chunk_index":0,
  "chunk_count":35,
  "offset_bytes":0,
  "length_bytes":524288000,
  "source_range_sha256":"ACTUAL_RANGE_SHA256_64_HEX",
  "bridge_sha256":"SAME_REOPENED_BRIDGE_SHA256",
  "bridge_reopened_sha256_verified":true,
  "bridge_root":"/root/share/host174_storage_recovery_bridge/20261016_storageops_02",
  "bridge_path":"/root/share/host174_storage_recovery_bridge/20261016_storageops_02/PB_CHUNK_000/files/payload.bin",
  "destination_archive_root":"/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02",
  "final_destination_relative_path":"Decoupled-L2/old174/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz"
}
```

The target uses the frozen, GitHub-read-back scope descriptor and exact READY SHA256. Default CLI is a read-only validation; `--receive` explicitly copies one range to a new, exclusively owned partial archive, fsyncs/closes it, reopens and hashes that exact range. A journal records ordered verified extents and the source identity/scope. It never overwrites a preexisting unowned final/partial file. `--resume` replaces only the current unverified tail of that owned partial; verified predecessors stay. Completed components and journal-only completion recover without retransmission.

Target writes an immutable `infrastructure/archive_range_receipts/polybench_9feffb121c30/PB_CHUNK_NNN_DEST_VERIFIED.json` and identical bridge marker. Status is **RANGE_DEST_VERIFIED**, not whole-file verification. Source independently compares/rechecks it, publishes a GitHub-pinned `PB_CHUNK_NNN_SOURCE_KEEP.json`, binding `batch_id`, `source_ready_sha256`, `target_receipt_sha256`, `source_range_sha256`, `source_action: SOURCE_KEEP`, `source_released_bytes: 0`. Only then target removes the exact inventoried payload and empty known parents, publishes `PB_CHUNK_NNN_BRIDGE_CLEANED.json`, and source may stage the successor.

After all 35 ranges and source KEEP/bridge closeouts, `--finalize` requires exact full extent coverage, rereads the complete 17943970556-byte archive and checks the frozen whole SHA256 before publishing the canonical `.tgz` and **WHOLE_ARCHIVE_DEST_VERIFIED**. No second assembly transfer is needed: each bounded range already appended at its exact offset in the owned partial. Whole receipt lives under `infrastructure/project_receipts/POLYBENCH_WHOLE_ARCHIVE_DEST_VERIFIED.json` and the bridge. Primary compressed archived bytes count once; component extents and restore copies are separate counters.

Next gates remain independent bounded reverse validation, exact stage-member recovery hashes/metadata, fresh source current/future consumer and registry review, and explicit user approval of any exact scientific stage release manifest. Original tgz remains kept. No source release is implemented in this tool.
