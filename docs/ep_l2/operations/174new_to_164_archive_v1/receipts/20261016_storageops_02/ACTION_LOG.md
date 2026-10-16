# Action log — incremental V2 revision

- Read complete amendment from GitHub at 0ca1fe76a30b70240b8d56f299f2685cf3282445; read previous STATUS/PRECHECK/SOURCE_FS_MAP/REMOTE_164_AUDIT.
- Independent Windows checkout fetched amendment and Lane5 branch via existing local proxy; no lane branch/worktree writes.
- Read and SHA256-verified all four Lane5 mapping evidence files at 2fb8a6d1144f6fce038f51e60192f9fa8b0207af.
- Reused existing trusted hrl SSH alias to check exact source identities; no SSH fingerprint relaxation.
- Remote shell wrappers used timeout -k; individual metadata/du commands were bounded to 8–10 seconds.
- Direct SSH attempts to 164 in this revision: 0. C16/model content reads/writes: 0.

- 174-new: `hostname`; exit=0.
- 174-new: `readlink /proc/self/ns/mnt`; exit=0.
- 174-new: `findmnt -T /root/share/mnt164 -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT,OPTIONS`; exit=0.
- 174-new: `df -B1 -P /root/share/mnt164 /root/share/mnt164/huangrulin`; exit=0.
- 174-new: `stat -c '%d %i %u %g %a %F %n' /workspace /root/workspace /root/share/container-workspaces/hrl-174-new/workspace /root/share/mnt164 /root/share/mnt164/huangrulin`; exit=1.
- 174-new: `find /root/share/mnt164/huangrulin -mindepth 1 -maxdepth 1 -printf '%f	%y	%u:%g	%m
'`; exit=0.
- 174-new: `sh -c 'if command -v getfacl >/dev/null 2>&1; then getfacl -p /root/share/mnt164/huangrulin; else printf "GETFACL_UNAVAILABLE
"; fi'`; exit=0.
- 174-new archive metadata: `stat -c '%d %i %u %g %a %F %n' /root/share/mnt164/huangrulin/archives /root/share/mnt164/huangrulin/host174_storage_recovery /root/share/mnt164/huangrulin/archived_runtimes_174new`; exit=0.
- 174-new archive metadata: `find /root/share/mnt164/huangrulin/archives -mindepth 1 -maxdepth 1 -printf '%f	%y
'`; exit=0.
- 174-new archive metadata: `find /root/share/mnt164/huangrulin/host174_storage_recovery -mindepth 1 -maxdepth 1 -printf '%f	%y
'`; exit=0.
- actual Lane5 source via hrl: `hostname`; exit=0.
- actual Lane5 source via hrl: `id`; exit=0.
- actual Lane5 source via hrl: `readlink /proc/self/ns/mnt`; exit=0.
- actual Lane5 source via hrl: `stat -c '%d %i %u %g %a %n' /workspace`; exit=0.
- actual Lane5 source via hrl: `df -B1 -P /workspace`; exit=0.
- actual Lane5 source via hrl: `findmnt -T /workspace -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT`; exit=0.
- actual Lane5 source via hrl: `findmnt -T /root/share/mnt164 -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT`; exit=0.
- actual Lane5 source candidates: `findmnt -T /tmp -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT`; exit=0.
- actual Lane5 source candidates: `df -B1 -P /workspace /tmp`; exit=0.
- actual Lane5 source candidates: `find /workspace/.git -maxdepth 1 -name '*.lock' -printf '%f	%s	%T@
'`; exit=0.
- actual Lane5 source: `timeout -k 2s 10s nice -n 19 ionice -c 3 du -sx -B1 /tmp/m5-gesu-unpack-check.F9XDGy`; exit=0.
- actual Lane5 source: `timeout -k 2s 10s nice -n 19 ionice -c 3 du -sx -B1 /tmp/m5-gesu-unpack-check.FGnex7`; exit=0.
- actual Lane5 source: `timeout -k 2s 10s nice -n 19 ionice -c 3 du -sx -B1 /tmp/m5-2mm-source-tar-verify.PhemE1`; exit=0.
- actual Lane5 source: `timeout -k 2s 10s nice -n 19 ionice -c 3 du -sx -B1 /tmp/m5-spmv-parboil-verify.rz7Qu5`; exit=0.
- actual Lane5 source: `timeout -k 2s 10s nice -n 19 ionice -c 3 du -sx -B1 /tmp/c2p-gpgpu-build-20260821`; exit=0.
- actual Lane5 source: `timeout -k 2s 10s nice -n 19 ionice -c 3 du -sx -B1 /tmp/c2p-accel-build-20260821`; exit=0.

- Metadata-only enumeration inspected 1474 immediate /tmp directories and 126 exact Git temporary packs; no recursive history scan.
- A visible process-name snapshot found no matching git/rsync/make/ninja/cc1plus/g++/ld/tar/gzip/zstd processes; this is not sufficient candidate inactivity proof.
- Source after df snapshot returned 0; output retained in SPACE_BEFORE_AFTER.json.
- Probe mkdir/write/fsync/reopen/hash/unlink: NOT_RUN, exact archive root approval pending.
- Transfer/dry-run/source hash/SSHFS data readback/cleanup/Git fsck: NOT_RUN, no archive batch admitted.
- Staging is restricted to this new receipt revision. PUBLICATION.json records the completed audit commit push/fetch/readback separately.
