Industrial L2 nineJSON cold archive: recovery instructions

Persistent native164 archive root:
/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261022_industrial_l2_r8p_9json_v1/NINE_JSON_2fff84498f202d2e

On174-new ONLY, map /home/shared to /root/share/mnt164 and verify findmnt source admin-wcx@10.208.130.164:/home/shared with fstype fuse.sshfs. Original174 same-named mnt164 is local Share and must never be used as the archive source.

1. Verify the immutable COMMIT.json, ARCHIVE_VERIFIED.json, SOURCE_MANIFEST.json, original frozen_source_sidecars/SOURCE_FROZEN_MANIFEST.json and TRANSACTION_CHUNK_INDEX.json against the final Git/readback SHA index. Missing COMMIT means an unfinished archive, never a full verified nine-file set.
2. Pick a new ABSENT destination on a separately authorized native filesystem with enough room for15,498,539,389raw bytes plus overhead/reserve. Do not overwrite original source paths or active worktrees. This Goal performs no full recovery writes.
3. For each frozen relative_path, take only its TRANSACTION_CHUNK_INDEX rows sorted by raw offset. Verify txid, compressed SHA and original chunk SHA, decompress the independent gzip members and concatenate exact raw bytes to a new file. Require contiguous offsets/no overlap, exact original size and entire original SHA from SOURCE_MANIFEST. Filenames are generated hash+offset chunk keys, not raw relative-path traversal.
4. Restore each file numeric UID/GID/mode/mtime_ns from the original sidecar or PATH_MAP, then directory metadata from SOURCE_DIRECTORY_METADATA bottom-up. Rehash every actual native file and compare all file/directory numeric metadata. Source dev/inode/ctime remain historical provenance; SSHFS projected1011/0777 attributes are not the restore metadata.
5. Independently retain recovery evidence. Existing v9_transaction.py/chunk_codec_adapter_v2.py preserve no-overwrite and native metadata routines, but native164 execution requires an actual authorized164 command entry. No native execution or full restoration is claimed by this archive-only delivery.

Source files always remain KEEP. PROPOSED_EXACT_SOURCE_RELEASE.tsv is only a future review proposal and authorizes no unlink, move or rewrite. PPA/Yosys source/version, original recipes and scientific TIMING_INFRA_BLOCKED/proxy limitations are preserved in frozen_source_sidecars/PPA_PROVENANCE.json. No original RTL/build environment is needed merely to recover these exact JSON bytes.
