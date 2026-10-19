# TLS-V10 P9_PUBLIC recovery pointer ? FIRST_RANGE_VERIFIED, not a completed group archive

Current state: the original B0001 passed Source16G admission and exact READY; at07:54:59UTC the same Target receiver accepted144B onto true164, closed/reopened its SHA, and independently restored that range on native tmpfs with frozen numeric metadata. Source READY `e6199c059b52d8ad08eed90c6f0438e42250b431`, raw SHA `ad665c055ad2210bab1df5e9ead075d0fec6344bfa4414db6f0dbe7263101575`. Range content SHA `bc85cb82388094a4cc5f7b9bb58893bd2982ad79e66a29e4fd20fa35d5ac58e6`. Accepted/archive ranges1; native range proofs1; whole-group validated files0/141; full-group native restored files0/141; Source release0. The exact bridge payload remains until independent Source KEEP ACK and cleanup. Source originals are retained and remain the authoritative COMPLETE group copy. Do not treat a range proof, reserved root or synthetic tests as a complete archive or release prerequisite PASS.

Authority: Framework `f8baa3acfdbd2f420c108d4d4baff0432ef38822`, authority text SHA256 `745fb24b603627b63bc43a1cb130a9e61038d23adee618e2850e3d80755c7bf1`, authorization JSON SHA256 `789528e6dd4e7b51c3a437e14f8a9b3df1045bfa5e1eefc71974b3324ce9b61d`. Source-only exact141 release has conditional user approval, but all full-proof and fresh Source gate/journal prerequisites must pass. Target has no Source unlink authority.

## Exact retained mappings

- Original root: `/workspace/worktrees/accel-sim-tls-cache/hw_run/tls-cache-p9-public-v1`.
- Original frozen Source publication: `swayhrl/gpu-l2-cache-verilog@ecb24975c9daed9c42687849e8a2c6b350b470ff`; canonical binding `9651ab64566c1f9539a60f10973267257e543414`.
- Full141-file inventory: `SOURCE_TLS_V10_P9_PUBLIC_FROZEN_FILES.jsonl`, SHA256 `38e5d71dae3d92c8728d511f7d648eb9eca12e99443c2072b4eb531e022072f4`.
- Full4-directory inventory: `SOURCE_TLS_V10_P9_PUBLIC_FROZEN_DIRECTORIES.jsonl`, SHA256 `43589244defa70615b43b031c1df8edd1213e7f967cf93834ff229e4095c918b`.
- Canonical manifest: `SOURCE_TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json`, canonical SHA256 `ad7e45a12d486ea3a62ff8452df321fb9ad093ca582eb23a3c05ac716267c597`.
- Selector: `315c008ee1757637b4f68172f93e58c4916cda061936dc4d0125762e6aa9ba0a`; existing txid `574747b05622a2a0f3ef1a58c11044ee724e5e585d0edd5f0fc32937eda12e6b`.
- True164 native reserved base: `/home/shared/huangrulin/host174_storage_recovery/tls_v10/20261018_P9_PUBLIC_315c008ee1757637b4f68172f93e58c4916cda061936dc4d0125762e6aa9ba0a`.
- Same base on174-new: `/root/share/mnt164/huangrulin/host174_storage_recovery/tls_v10/20261018_P9_PUBLIC_315c008ee1757637b4f68172f93e58c4916cda061936dc4d0125762e6aa9ba0a` via ONLY `admin-wcx@10.208.130.164:/home/shared` fuse.sshfs. The old174 path `/root/share/mnt164` is not a genuine164 view.
- Existing partial transaction manifest: `/root/share/mnt164/huangrulin/host174_storage_recovery/tls_v10/20261018_P9_PUBLIC_315c008ee1757637b4f68172f93e58c4916cda061936dc4d0125762e6aa9ba0a/574747b05622a2a0f3ef1a58c11044ee724e5e585d0edd5f0fc32937eda12e6b.partial/manifest.json`. This is metadata, not a full data archive.
- Future committed tree, CURRENTLY NOT COMPLETE: `/root/share/mnt164/huangrulin/host174_storage_recovery/tls_v10/20261018_P9_PUBLIC_315c008ee1757637b4f68172f93e58c4916cda061936dc4d0125762e6aa9ba0a/574747b05622a2a0f3ef1a58c11044ee724e5e585d0edd5f0fc32937eda12e6b/tree`; same suffix under native164 base. It is usable only after its matching canonical `COMMIT.json`, complete file/dir hash index and full restoration certificate exist and reverify.
- Future full-group independent proof tree, CURRENTLY ABSENT: `/root/tls-v10-native-restore-20261018-target01/full_groups/574747b05622a2a0f3ef1a58c11044ee724e5e585d0edd5f0fc32937eda12e6b/tree` on the Target's native private tmpfs. Tmpfs proofs are volatile; original bytes and frozen metadata must be retained durably on164, with proof indexes in Git/NAS.

All relative file names map unchanged between original root, committed164 tree and full native proof tree. No concatenated/compressed reinterpretation of original bytes is proposed. Frozen original logical bytes2,897,196,811 and allocated bytes2,897,674,240 are distinct from actual NAS use and measured source df gain.

## Recovery only after full archive acceptance

Future owner must locate and hash the exact manifest/COMMIT/full-file metadata index and `TLS_V10_P9_PUBLIC_ALL141_ARCHIVE_AND_NATIVE_RESTORE_PASS.json` in this receipt lineage and durable164 base. If any is absent or inconsistent, HOLD recovery/deletion claims. Today's first-range state still lacks that full141 certificate.

Use the byte-pinned unchanged `tools/v9_transaction.py` (SHA256 `6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe`) from this Target execution branch. On a qualified native filesystem, select a NEW ABSENT directory with sufficient resource budget and root privileges for original numeric UID/GID. Verify original content SHA before and after copying; never restore over an existing worktree. Core API:

```python
# Run ONLY after full committed archive is independently verified and resource gates pass.
# archive_tree is the committed genuine164 tree above; destination MUST be new and absent.
import json
from pathlib import Path
import v9_transaction as tx
manifest = json.loads((Path(archive_tree).parent / 'manifest.json').read_bytes())
assert tx.validate_manifest(manifest) == '574747b05622a2a0f3ef1a58c11044ee724e5e585d0edd5f0fc32937eda12e6b'
assert (Path(archive_tree).parent / 'COMMIT.json').is_file()
assert not Path(destination).exists() and not Path(destination).is_symlink()
proof = tx.native_restore(archive_tree, manifest, destination)
assert proof['status'] == 'RESTORE_VERIFIED'
```

The implementation copies every original file, including empty files; checks full SHA; restores numeric UID/GID/mode/mtime_ns; then restores directory metadata in deepest-first order. It refuses an existing destination or SSHFS as native proof. ctime is preserved in provenance only. Actual native identity/metadata must be reread independently, not inferred from SSHFS's UID/GID projection. The new read-only all-file index helper `tools/tls_v10_full_restore_index.py` checks exact finalized archive/native file+directory inventories, full SHA and every numeric metadata field and requires the prior absent-destination ownership reservation. Its13 native synthetic tests do not certify P9 science.

The16GiB exception is for frozen TLS COPY_ONLY and separately qualified Source-only exact P9 release. Reverse restoration into old174, builds/sims and other operations retain their original resource/authorization policy (normally48GiB). No Source deletion command is provided here.

## Next exact closure

1. DONE for existing B0001: Source16G45-case policy/test review, Source fresh-at-stage actual resource/activity/identity PASS and exact144B READY.
2. DONE real164 close/reopen SHA + native range proof. Publish/read back both exact receipt SHAs; await independent Source KEEP ACK, then exact unchanged bridge cleanup. See `TLS_V10_P9_PUBLIC_B0001_TARGET_RECEIVING_RECEIPT_COPY16.json`.
3. Qualify small grouped sender/receiver fixtures, then serial bounded frozen ranges and actual allocated bridge costs. Reuse verified owned duplicates; no duplicate upload or second stream.
4. Full141+4 original metadata/content coverage, committed durable archive, NEW absent full native restoration, immutable three-way all-file index and certificate. Publish source-readable exact release prerequisites.
5. Only Source can evaluate the already-approved separate release policy and execute its qualified exact141 fsync INTENT/DONE journal. Target records a release only after Source immutable journal and actual measured df evidence. All other24 groups remain SOURCE_KEEP.
