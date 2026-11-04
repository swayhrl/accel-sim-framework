# Node109 full-asset and true164 archive audit — 2026-11-04

Task: `NODE109_STORAGE_AND_TRUE164_ARCHIVE_AUDIT_20261104_V1`. Read-only source/target audit; no deletion, copying, task suspension or GPU inference was performed. Node174 served solely as the SSHFS bridge to true164; its original assets remain Lane T2's scope.

## Current state and decision

- Node109 `/`, `/data/c16`, and owner home have the same ext4 device ID `66306` on `/dev/nvme0n1p2`; `/data` is **not a separate capacity pool**. Root is 835.05 GiB used of 936.79 GiB, 54.08 GiB available, 94% at 2026-11-04T02:26:07Z.
- `/data/c16` is 361.76 GiB allocated, ImageLab project 196.77 GiB, current ImageLab model files 180.42 GiB (44 files). These are overlapping scopes; do not sum them.
- Compared with the Oct28 41-file ImageLab manifest: 36 files retain exact source dev/inode/size/mtime and target size; 8 files totaling 58.57 GiB logical (62892833575 B) are newly present; 5 historical files are absent. Two of the 8 have a matching Oct31 164 six-file archive with target full-SHA receipt, but **today's source hash is not proven**. The other six have no matched scoped ImageLab archive path on true164. The three absent H3 weights have no supplied retirement receipt; the two absent LTX files do.
- C16 Qwen3-30B 26-file revision is 56.89 GiB allocated with historical exact source/target SHA evidence and unchanged Nov04 file identities. This is a scientific dependency, not an approved deletion. StageA two revisions total 8.27 GiB; 164 file-set/size evidence exists but no complete current SHA/restore proof.
- True164 identity was independently confirmed from the bridge mount source and `fuse.sshfs` at 2026-11-04T02:29:36Z. A matching name, historical claim or directory presence alone was not treated as full archive proof.

## Activity and retention gates

ImageLab has two visible Python processes, Ollama and a tunnel process with project FDs/maps; one GPU compute process is visible. RTX4080 C16 suite has active mmap/FD evidence. Process inspection saw 436 PID directories, but 105 FD and 105 maps views were unavailable or raced. Thus no global idle finding. AWMA R26/R27 publication manifests/checkpoints are present on 164, yet current full source/target tree hashes and downstream scientific dependencies are not closed. E1 original traces, A26/A61/NequIP assets, AWMA results and C16 raw Trace remain protected. Existing 164 raw bundle directory has 96 entries, but no complete one-to-one mapping of 109 originals was proven.

The only priority-review cold group is StageA, with a conditional upper bound of 8.27 GiB. It still needs full SHA, restore and science-owner checks. Qwen3 offers a larger physical upper bound (56.89 GiB) but carries higher ongoing research-dependency risk. **No asset satisfies all cleanup prerequisites in this read-only audit.** The `CLEANUP_CANDIDATES.csv` upper bounds are nonadditive and are not deletion authorization.

## Method, evidence and limits

Used `df`, `findmnt`, metadata-only `du -x`, selected `lstat`/file identity, bounded `/proc` FD/mmap inspection, scoped true164 directory metadata, small receipts/manifests, and existing SHA/COMMIT evidence. Did not rehash the 361.8 GiB C16 tree or transfer model/data payloads. Historical full-SHA labels preserve their original proof dates and are coupled to current identity/target-size checks, not a fresh full target read. A root used-space gap remains beyond scoped user-readable directories. Native 164 ACLs were not directly verified through SSHFS.

This public review copy replaces private host, account and bridge identifiers with placeholders. Exact internal endpoint resolution and raw evidence remain in the private local working artifacts. `HISTORICAL_REPORT_PROVENANCE.json` records each original report SHA256 and redaction counts; those public copies are explicitly incomplete originals. No credentials, raw Trace, model weights or binary files are published.

## Deliverables

`STORAGE_AND_MOUNT_STATE.json` gives filesystem/mount/process limits. `ASSET_INVENTORY.csv` inventories physical/allocation scopes and key files. `SOURCE_TO_TRUE164_ARCHIVE_MATRIX.csv` records source, true164 path, file identity, archive proof, current users, restore entry and cleanup gate. `IMAGE_LAB_NEW_ASSETS_AUDIT.csv` lists all 8 additions. `CLEANUP_CANDIDATES.csv` ranks by actual releasable bytes and risk. `HISTORICAL_RETIREMENT_CLOSURE.md` reconciles prior deletions and current absence. The four historical review copies and provenance ledger preserve earlier context.

Audit conclusion: **STOP; await ChatGPT review and a separately defined next cleanup scope.**
