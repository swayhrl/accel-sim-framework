# Environment, namespace and access evidence

Trusted existing SSH aliases were used with BatchMode and strict host-key checking: `hrl` (root@10.208.130.174:2233, hostname `huangrulin-174`) and `hrl-174-new` (same host:2239, hostname `huangrulin-sshfs-174`). No credentials or new access rights were requested. Commands were metadata reads, bounded existing control-file reads, Git reads, compiler/Python version queries, and `readelf`; there was no binary/application execution. A few small control/executable files were hashed; no large trace/model/result was streamed or rehashed.

| Location | Source / filesystem | Source device | Target device | Free bytes at initial snapshot |
|---|---|---:|---:|---:|
| Source `/workspace`; Target `/` and `/root/workspace/accel-sim-framework` | Separate overlay namespaces; backing Docker data under `/mnt/data/docker` |156|1048578|8,074,100,736|
| Both `/root/data` | `/dev/sdf[/huangrulin]`, ext4, SSD HFS3T8G3H2X069N, rotational0 |2128|2128|8,074,100,736|
| Both `/root/share` | `/dev/md127`, ext4, rotational1 |2431|2431|44,190,019,584|
| Source `/root/share/mnt164` | Local `/dev/md127` directory, **not164** |2431|--|Same Share pool|
| Target `/root/share/mnt164` | `admin-wcx@10.208.130.164:/home/shared`, `fuse.sshfs` |--|39|51,575,894,458,368|
| Target old TLS native-proof tmpfs |24 GiB total, noexec, existing other-task ownership |--|95|23,262,310,400|
| `/dev/shm` | Container tmpfs,64 MiB total |separate|separate|67,108,864 each|

Mount namespace IDs: Source `mnt:[4026534768]`, Target `mnt:[4026535153]`. Boot ID is identical. Separate overlay device numbers do not mean separate physical disks. Source Docker `/etc/hostname` bind mount identifies `/dev/sdf[/docker/containers/.../hostname]`; overlay upper directories are under `/mnt/data/docker/overlay2/...`. Overlay and `/root/data` report identical capacity/free space; `/root/data` has the same device/inode61603841 in both containers. These observations support a common SSD backing pool; overlay virtual filesystem IDs are different and were not presented as identical physical FSIDs.

`/root/share` root inode2 and an existing bridge receipt were checked on both sides. Exact sample: `/root/share/host174_storage_recovery_bridge/20261016_storageops_02/LANE_BA_COLD_V3_C16_PRIORITY_HANDOFF_20261020.json`; device2431, inode103548268, size8425, mtime_ns1792489877718156834 and SHA256 `100101b2288fd4992acc116700f371e944f63b3c1be22c0aba73a47331b1c9c6` agree. This proves that shared route, not a route into Source's private overlay. `/root/data` shallow names are C16-owned assets; no new workspace was created there.

CPU quota in each container is38400000/100000 (384 CPU equivalents), cpuset0-511; memory.max is274,877,906,944 B (256 GiB). Target memory.current3,879,194,624 B and Source93,949,984,768 B are snapshots. Host MemAvailable was approximately318.3 GB. All compete on one host; cgroup availability, CPU affinity, physical memory reserve, pressure, OOM deltas and other-project reservations must be admitted together. Zero Target cgroup IO PSI is not zero host pressure. The stored JSON includes host PSI; no I/O threshold was changed.

No available independent SSD mount was found in the bounded current mount inventory. Options for a later authorized phase:

1. Allocate a genuinely separate local SSD/NVMe filesystem or adequate owner-approved quota with reserved capacity, then expose only the new project's private work directory to Target. Verify actual device/backing pool, bytes and inodes, not path names.
2. A dedicated directory on `/root/data` avoids overlay copy-up but cannot solve its current7.52 GiB shared free-space limit. It is conditional on sufficient future capacity and ownership approval.
3. `/root/share` has only about1.15 GiB above its40 GiB protection line and rotational storage; it is a shared bridge, not a ready fast working disk.
4. A new bounded tmpfs could support a specifically approved small engineering fixture after cgroup/RAM accounting; the existing TLS tmpfs must not be reused, and tmpfs is neither long-term storage nor an adequate general project workspace.

True164 access is currently SSHFS data access. At15:53 UTC, this study read existing `COMMIT.json` (2056 B, SHA256 `520c5c66dff019c4d7d7b6daca30ac02702734a6eaf79f5160232c2fab9023a8`) and `ARCHIVE_VERIFIED.json` (526 B, SHA256 `49faadc5446aa3fe01764e5fea2794830193805cbe5aa7f6f8a98a1d9a0ee978`) under the exact previous industrial archive root. Both were device39 and stable before/after. See `evidence/TRUE164_EXISTING_OBJECT_READ.json`. These small reads confirm actual file access on the mounted route, not a new full archive verification. This does not grant native164 command execution or prove remote uid/gid, fsync durability and server-local restoration. This study did not retry failed authentication, scan the NAS or create a test directory. New production storage roots and native verification/cooperation must be explicitly arranged later.
