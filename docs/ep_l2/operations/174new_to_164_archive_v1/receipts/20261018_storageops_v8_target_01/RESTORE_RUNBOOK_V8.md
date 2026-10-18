# V8 exact restoration handoff
+
+Genuine mount on174-new is admin-wcx@10.208.130.164:/home/shared at /root/share/mnt164. Old174's same-named directory is not this mount. SOURCE_TO_164_RESTORE_INDEX_V8_R2.json identifies exact R1/R1R/R2 original and164 paths, full inventories, numerical metadata and full historical restore proofs. Match file SHA/source identity and path, never project-name similarity.
+
+Fresh .vvp samples were recovered into independent164 and native shared paths with exact SHA256, UID/GID/mode/mtime_ns and ancestor directory metadata, using tools/restore_verified_selection_v8.py. Each R1/R1R/R2_FRESH_RECOVERY_PLAN_V8.json has a NAS plan path and exact SHA in EXISTING_VVP_FRESH_RECOVERY_DRILLS.json. Dry-run the tool with --plan <NAS-plan> --expected-plan-sha256 <pinned> --destination <new-absent-path-under-V8/recovery_drills>. Only --execute writes; --native-metadata is permitted only on verified native shared storage. It refuses existing paths and never writes original source roots. Native ctime is provenance only.
+
+For future old174 original-path recovery, target supplies the exact <=512MiB verified subset via the existing shared bridge under the one receiver lease, preserving numerical metadata. Source owner independently verifies hashes and imports into a new absent recovery directory on the real old174 namespace with sufficient free reserve, applies native ownership/mode/mtime and directory metadata bottom-up, then rehashes before any owner-reviewed promotion to a project path. Never overwrite active originals, bypass one-stream protocol or confuse the local old174 mnt164 directory with164. Prior actual native B001 and full NAS proofs remain available in R13, but do not grant new source release authority.
+
+Current515 candidate binaries remain SOURCE_KEEP. Target first receipt proves exactly its three fresh samples plus the linked historical full project evidence; it does not claim a new full515 payload rehash or native full515 restore. M5 new compressed copy and independent18-file recovery are being prepared on the sole data stream. No new source bytes are claimed released.
+
## Exact M5 command from a verified174-new mount

First verify the compressed file and metadata SHA against the signed receipt. Pick an absent destination below an existing owned parent with sufficient capacity and the applicable unchanged resource reserve. This command creates only that new recovery path; it does not promote or delete source paths.

```sh
V8_ROOT=/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_fast_v8
NEW_DEST=/absolute/existing/owned/parent/m5-recovery-new
python3 - "$V8_ROOT" "$NEW_DEST" <<'PY'
import hashlib, importlib.util, json, pathlib, sys
base, dest = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
archive = base / 'M5/old174/workspace/m5-trace-immutable/gesu/gesu.tar.zst'
manifest = base / 'metadata/M5_GESU_MEMBER_MANIFEST_V8.json'
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == 'bf38691fdf619ba2bea0aacf3fc65e74a74415aea5d0b2e93c0fb8aeb7dc3b0d'
h = hashlib.sha256()
with archive.open('rb') as stream:
    for block in iter(lambda: stream.read(4*1024**2), b''): h.update(block)
assert h.hexdigest() == '0d2ba5d069a88e331c1575dd8c2f5a8defe4d36d255464f998245454d86d7c03'
spec = importlib.util.spec_from_file_location('m5_restore', base/'tools/restore_m5_archive_v8.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
print(json.dumps(module.extract(archive, manifest, dest), indent=2))
PY
```

The frozen manifest supplies numeric UID/GID/mode/mtime for all18 files and2 inner directories. With appropriate ownership privileges on a native filesystem, apply chown/chmod/utime from those rows, directories bottom-up, then independently stat and rehash before any owner-reviewed promotion. The8 outer temporary-directory metadata rows are separately preserved in SOURCE_M5_DUPLICATE_DIRECTORY_MANIFEST_V8.tsv. Do not use SSHFS projected ownership as original native metadata; ctime is provenance and cannot be restored. On old174, retain its canonical local archive, or use one SHA-pinned <=512MiB reverse bridge at a time to receive the59MB archive from real164 before recovery. Never assume old174's local mnt164 is the genuine mount.

## Exact source selector procedures and current state

The target full-selector receipts contain every original path, preserved164 path, independently restored path, current SHA and numeric source identity. Source R1/R1R/R2_VVP_BOUNDED_REVERSE_PLAN_V8.json and the R1 historical reverse plan divide recovery into <=512MiB batches; source importer/no-overwrite fixtures are pinned in source review pack20261018_fast_reclaim_v8. The source actor owns native old174 imports and any eventual original-path promotion. Native3 ACK38b7fbc01c365c56f23a7cfe2592888ca16661d9 proves actual old174 restoration; it is not a claim that all515 were natively materialized on old174.

At source closeout b7994431e6b052bccd7571802a6c1b60ec1fadfc: only M5 two temporary roots and exact R1/R1R VVP subsets were released. R2 originals and all nonlisted build/log/RTL/PPA/raw/Git remain KEEP. Do not re-run deletion from a recovery instruction. Subsequent experiments require Lane5 own fresh gates; Ops has issued no experiment admission.
