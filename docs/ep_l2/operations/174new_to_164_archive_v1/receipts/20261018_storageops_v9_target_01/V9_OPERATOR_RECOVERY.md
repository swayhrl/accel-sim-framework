# V9 transaction and recovery operator notes

V9 is a new target-only task on the original Ops branch. V8/R13 archives and
receipts remain frozen. Never use this target tooling to delete an old174 file.
The existing source-owned V8 R2 executor is unchanged; its production gates use
the unchanged V8 receipt plus the fresh V9 exact191 readback and source checks.

## Locate evidence

Repository: `swayhrl/accel-sim-framework`, execution branch
`hrl/ops-174new-164-archive-exec-v1`. This directory contains the frozen contract,
source raw inventories, exact transaction manifests, SHA256SUMS, batch receipts,
restoration receipts and SOURCE_TO_164_INDEX_V9.json. Each published Git commit is
read back after push. `TARGET_V9_CONTROL_<commit12>_PUBLICATION.json` records the
exact filenames and SHA values also read back from 164 and the shared bridge.
Versioned controls do not overwrite earlier records.

On **174-new (2239)**, the sole genuine164 mount is
`admin-wcx@10.208.130.164:/home/shared`, type `fuse.sshfs`, at
`/root/share/mnt164`. The same pathname in old174 (2233) is not this mount.
Native164 paths replace `/root/share/mnt164` with `/home/shared`. Archive scope is
only `huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02`.
V9 controls/tools live in `increments/20261018_v9`; the three cold transaction
bases live in `increments/20261018_v9_cold_source_01`. Exact source-to-target
paths and transaction IDs are recorded in the index, not inferred from names.

## Frozen identity and sole transport

Production uses the source V2 canonical manifests byte for byte. TXID is SHA256
of sorted, compact UTF-8 JSON plus newline containing exactly these five keys:
`source_filesystem_identity`, `source_root`, `selector_sha256`,
`source_frozen_commit`, `genuine164_destination_root`. The production selector is
SHA256 of the exact normalized file-row JSON array in the same canonical
encoding. Raw source file and directory JSONL hashes are independently joined.
The entire immutable transaction manifest SHA additionally binds directory
metadata. Old newline-joined V1 TXIDs/window are HOLD and must never be used.

One receiver, one existing `.TARGET_RECEIVER.lock`, one bridge batch at a time.
Bridge root:
`/root/share/host174_storage_recovery_bridge/20261016_storageops_02`.
No source stager may launch another batch before its prior source KEEP ACK,
target exact payload cleanup receipt and next-window request. Logical and
allocated staging are each <=256MiB; transport is <=30MiB/s, one CPU with low
I/O priority. Share free remains >=40GiB; old174 physical workspace >=48GiB and
available RAM >=64GiB. No Lane resource policy, PID, lease, result or registry is
modified by target Ops. A resource conflict is HOLD, not permission to lower a
floor. Never count an archive or bridge cleanup as source workspace recovery.

## Durable copy, resume and atomic publication

Each `<base>/<txid>.partial` preserves the immutable manifest, bounded durable
chunks, offsets, reopened hashes and receipt chain. Resume accepts only the
same TXID/manifest. Re-hash existing chunks before reuse; a valid duplicate does
not upload again. A complete orphan chunk can be adopted only against the
exact pinned offset, size and chunk SHA using `reconcile_partial_chunk`.
An incomplete/corrupt orphan is HOLD; inspect it before any bounded reset of
only the owned temporary. Never truncate or overwrite a verified archive.

`renameat2(RENAME_NOREPLACE)` is unsupported on the actual SSHFS filesystem.
Actual exclusive LINK collision refusal and complete archive/resume were
tested there. Durable regular-file temporaries finalize through an exclusive
LINK and removal of only that owned temporary. Directory publication uses an
exclusive reservation, exclusive files, full hashes and an atomic
`COMMIT.json` published **last**. Without a valid COMMIT marker, a reserved
directory is not a verified archive. Directory fsync is used where supported;
regular files/records are fsynced before publication. A crash between link and
temporary removal, truncated temporary, unexpected final path or wrong marker
is HOLD for exact reconciliation, never a reason to replace an existing path.
The independent partial evidence may remain on 164 after sealing.

Ordered immutable receipt states reference the previous receipt SHA:
DISCOVERED -> SOURCE_FROZEN -> COPY_READY -> ARCHIVE_STAGED -> ARCHIVE_VERIFIED
-> RESTORE_VERIFIED. Target cannot create RELEASE_ELIGIBLE/SOURCE_RELEASED.
The source owns those separate transitions and all original-file eligibility.

## Restore without overwriting

Get the exact project manifest and its SHA from SOURCE_TO_164_INDEX_V9.json.
Choose a **new absent native** destination outside an original/live build.
Check current space, ownership, readers and required privileges first. Use the
preserved V9 tool version/hash from the protocol receipt. For example:

```python
# Run as an authorized owner on a native filesystem, with sufficient capacity.
import hashlib, json, pathlib, sys
sys.dont_write_bytecode = True
sys.path.insert(0, '/exact/preserved/v9_tool_directory')
from v9_transaction import native_restore
manifest_path = pathlib.Path('/exact/preserved/PROJECT_V9_TRANSACTION_MANIFEST.json')
raw = manifest_path.read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'EXACT_MANIFEST_SHA_FROM_INDEX'
manifest = json.loads(raw)
receipt = native_restore('/exact/verified/transaction/tree', manifest,
                         '/new/absent/native/recovery_root')
print(json.dumps(receipt))
```

The function rejects a populated destination, symlink traversal and SSHFS as a
native metadata proof. It verifies every restored byte and UID/GID/mode/mtime,
then applies/verifies directory metadata deepest first. ctime/dev/inode are
historical provenance and cannot be restored. Root/owner privilege may be
needed for numeric chown. If source-side network visibility differs, use the
same sole <=256MiB bridge in reverse with per-file hashes and an owner-approved
new native root; do not bypass the transport contract. Promotion into an
original path is a separate source-owner action and must fail on EEXIST.

Full independent content restoration on 164 and a representative complete
native selection are recorded separately. A native sample is not a claim that
all original files were imported natively. SSHFS projected UID/inode/mode are
never substitutes for numeric native restoration proof. A missing metadata
proof is explicitly UNVERIFIED and blocks any future release proposal gate.

## Source crash reconciliation is not a delete retry

New V9 release code is **synthetic-fixture-only**, with no production command.
Tests operate only in newly marked `ops_v9_fixture_*` temporary trees. A crash
after INTENT with an existing path reports HOLD without automatic unlink;
missing path before DONE reports UNCERTAIN/manual readback; DONE plus absent
path reports RELEASED_NO_RETRY. A reappeared path is HOLD. No retry issues a
second blind delete. Real V8 R2 interrupted release likewise requires the
source owner to reconcile its exact existing journal; target never repairs it
by deleting source files.

C2P/M2D are ARCHIVED_SOURCE_KEEP even after successful target verification.
All prospective per-file release lists require new exact user consent and
fresh source activity/identity/provenance checks. Lane5 admission remains a
separate owner chain and is not a prerequisite to declaring target archival
work DONE.
