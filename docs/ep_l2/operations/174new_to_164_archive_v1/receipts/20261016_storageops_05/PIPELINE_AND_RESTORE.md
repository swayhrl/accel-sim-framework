# Minimal V6 target workflow

The sole source Ops window owns inventory, owner/active-path decisions, source hashing/staging and source release. This target only accepts immutable READY data and publishes byte integrity evidence. It never runs source scans, source delete commands, auto-release or a second transfer queue. EP-L2, DTC-L1 and other owner-qualified cold projects share one receiver and one 30MiB/s stream.

Both roots are fixed to the V5 authorized bridge and archive. Project names are safe single components; destination paths must begin with the declared project and preserve file-relative structure. Batch IDs are globally unique across projects because the common bridge handshake uses `<batch>_READY.json` / `<batch>_DEST_VERIFIED.json`. Existing archive data/receipts are never overwritten. All tools default to read-only stdout; `--receive` or `--write` explicitly enables the specific target action.

| State | Authoritative evidence / owner |
|---|---|
| DISCOVERED | Source metadata inventory; source Ops |
| OWNER_SCOPED | Explicit project owner/retention and protected-path decision; source Ops |
| SOURCE_STABLE_HASHED | Exact source identities, allocated bytes, hash and reader checks; source Ops |
| STAGED_READY | Closed/reopened bridge hash and immutable READY bound to pinned source inventory; source Ops |
| DEST_VERIFIED | Every reopened SSHFS destination size/hash matches, bridge identities stable; target receiver |
| RESTORE_VERIFIED | Full selected restore scope verified at a separate path; record exact bytes/scope, never extrapolate a sample |
| RELEASE_AUTHORIZED | Existing V5 class or later explicit user authorization plus source owner qualification; never granted by target |
| SOURCE_RELEASED | Independent old174 exact action, allocated bytes and real df before/after; source Ops |

Backup-only batches stop at DEST_VERIFIED + SOURCE_KEEP. Indexing an archive does not advance source authorization. Source-side released allocated bytes and actual df delta are separate counters and may differ because of hardlinks, overlay/whiteouts or concurrent activity. Target indexes remain conservatively zero until a separately pinned source release receipt is consumed in the execution ledger.

`tools/archive_receiver.py` accepts the current V6 READY layout, including the explicit V5 S01/S02 adapter bound to the exact frozen 102-file inventory. S01/S02 have their approved legacy metadata set; missing broader V6 owner/config/ctime fields are not silently invented. New cold batches require owner COLD_COPY_OK, SOURCE_KEEP retention, namespace/mount/source/config/producer/run keys, rehydration recipe and per-file allocated bytes, dev/inode/nlink/mtime/ctime/UID/GID/mode/readers. Project names do not prove ownership. Unknown active state stays SOURCE_KEEP; symbolic, multi-link, sparse/chunked or unscoped inputs require explicit supported manifests instead of guessing.

The receiver checks fixed root identities, 40GiB Share floor, <=512MiB total, exact source membership for S01/S02, canonical paths without symlink traversal, stable stage identities and full hashes. One kernel receiver lock spans all hashing, one exact files-from rsync, reopen hashes and receipt publication. There is no source cleanup flag. Bridge copies remain until the independent source action handshake is complete.

Restore testing uses an independent directory under the authorized archive root. The current `--restore-sample` restores exactly one complete file and reports SAMPLE_RESTORE_VERIFIED_NOT_FULL_BATCH and only those bytes. It is suitable as a minimal receiver exercise for the already qualified reconstructible S01/S02 files; it does not qualify raw/trace offload. Before offloading scientific originals, the project owner must validate a full required restore/rehydration recipe, original metadata/link relationships, canonical archive lookup in the future runner, and any separate source deletion authorization. Test copies are kept as bounded audit artifacts; no source data is changed.

`tools/archive_index.py` reads at most 2048 owned receipt JSONs and checks known destination lengths and stored hash triples. It does not recursively hash history or scan other projects' source directories. It groups batches and counters by project, retains the legacy pack route's noncompliant label, and writes only immutable, uniquely named index snapshots when `--write` is requested. Stored receipt hashes are the authority; index generation is not a new full data checksum run.

Files larger than 512MiB are HOLD until a reviewed plan provides exact chunk offsets/lengths and chunk hashes, whole-file SHA256, independent reassembly restore and adequate bridge capacity. The receiver never increases the batch limit or labels a partial upload DEST_VERIFIED.

Read-only plan example: `python3 archive_receiver.py --manifest <READY.json> --inventory <frozen.csv> --expected-ready-sha256 <sha256>`. Add `--receive --restore-sample` only after the source READY is consumed and resources checked. Receiver tools run only in the verified 174-new namespace; old174's same-looking mnt164 path is not the SSHFS target. No daemon, scheduler or unattended release is installed.
