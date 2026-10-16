# Storage-Ops revision 02: ARCHIVE_ROOT_APPROVAL_PENDING

V2 amendment `0ca1fe76a30b70240b8d56f299f2685cf3282445` has been read in full and applied. Original Goal and all scientific/safety/resource constraints remain in force. Previous revision `20261016_storageops_01` is retained unchanged.

- **Resolved:** current 164 SSHFS mount and user directory enumeration succeeded. Level: `SSHFS_MOUNT_READ_VERIFIED`; no fresh 164 SSH authentication was attempted.
- **Resolved:** actual Lane5 source is reachable via the existing trusted SSH alias `hrl`. Hostname `huangrulin-174`, mount namespace `mnt:[4026534768]`, `/workspace` device 156 and inode 32926662 exactly match Lane5's independently published `2fb8a6d1144f6fce038f51e60192f9fa8b0207af` receipt. Its four evidence hashes match.
- The source container's `/root/share/mnt164` resolves to local ext4, so that path will not be used as a destination. A future controlled transfer must reach the verified SSHFS in the **174-new** namespace.
- **Sole remaining copy gate:** no exact independent archive write root is yet expressly authorized under V2 section 2.4. Proposal: `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02`. Approval question is pending; no target directory/probe has been created.
- Actual Lane5-source workspace free: `43968081920` B (40.948 GiB); floor remains 48 GiB. Ops-released bytes: **0**. No post-cleanup Lane5 measurement exists.
- Targeted metadata lists six temporary candidates and 126 Git temp packs (39444614257 logical bytes); none is approved for deletion. No source-data hashes, copies, probes or cleanup ran.
- Six lane worktrees, registry, locks, binaries and scientific results were not modified. No process was stopped.

Next: authorize the proposed exact archive path or specify a replacement. Then perform the tiny flush/reopen/hash/delete probe only there, admit one bounded candidate batch, establish inactivity/nonuniqueness/reproducibility and full copy/readback integrity, and release only permitted exact temporary objects. Git pack deletion still needs a later separate approval after full backup and Git-object analysis.
