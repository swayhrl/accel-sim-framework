# C16 RTX4080 rollback plan

This plan is fail-closed: no change begins without an approved PRECHANGE receipt and a timestamped, SHA256-closed backup. Rollback restores only the exact approved target; it never deletes Docker assets, reformats storage, or decides a driver version autonomously.

## Change lifecycle

| Phase | Required evidence/action | Stop rule |
| --- | --- | --- |
| PRECHANGE | Read-only receipt, package/module/Docker/storage baseline, explicit compatibility decision, target-file backup and SHA256 manifest | Any missing/ambiguous baseline blocks change |
| CHANGE | Administrator modifies only the approved file/package target; record exact argv, before/after mode/owner/SHA256 | No opportunistic package, disk, network, or security change |
| REBOOT | Only if the approved driver/module operation requires it; record intended reboot reason and console/access recovery plan | No unattended reboot without host-owner approval |
| POSTCHECK | Re-run inventory, confirm current kernel/modules/parameters/Docker/runtime, and execute only the approved next acceptance gate | Drift or failure triggers rollback decision |
| ROLLBACK | Restore the backed-up bytes/metadata; use only the prechange package set when an explicit package rollback was approved; reboot if required; re-run POSTCHECK | If rollback cannot be proven, stop and preserve evidence |

## Module configuration: NCU profiling setting

The narrow approved module change is the administrator-owned file:

```conf
options nvidia NVreg_RestrictProfilingToAdminUsers=0
```

PRECHANGE records `/proc/driver/nvidia/params`, every relevant modprobe file and SHA256, SecureBoot state if queryable, installed NVIDIA packages, current kernel, and whether the target file existed. Back up the exact target file before writing. CHANGE writes only this reviewed option. REBOOT follows the distribution-required initramfs/module reload/reboot procedure. POSTCHECK proves the loaded equivalent state (typically `RmProfilingAdminOnly: 0`), research-user N0 status, and unchanged no-sudo/no-Docker/no-SYS_ADMIN policy.

Rollback restores the original target file byte-for-byte and metadata; if it was absent, remove only the newly created C16 target file. Then apply the distribution-required reload/reboot procedure, verify the original loaded parameter state, and mark ordinary-user NCU acceptance suspended until N0 is repeated. On an untrusted shared host, the desired rollback state is restricted profiling (`NVreg_RestrictProfilingToAdminUsers=1` or no C16 override).

## Driver or CUDA decision path

The PRECHANGE receipt must first show why the installed stack is incompatible with the approved 4080 acceptance plan. If it is compatible, preserve it. If it is not, stop and request a user-approved change record that names the desired package source/version, the exact prechange package versions, the rollback package availability, disk-space impact, reboot requirement, SecureBoot implications, and console recovery path.

Only after that approval may an administrator perform a package change. `purge`, kernel changes, shared `/usr/local/cuda` symlink changes, system-Python changes, and driver downgrade are not implicit rollback methods. If a changed driver fails POSTCHECK, the rollback target is the exact prechange package inventory; if that package set cannot be restored safely, stop rather than improvise.

## Docker configuration and assets

Before editing daemon configuration, save `/etc/docker/daemon.json` if present with SHA256 and metadata, record Docker version/info, and record every existing container/image/volume summary. Change only an approved daemon setting. Rollback restores the saved daemon configuration and follows the host's approved service-restart procedure. No rollback step removes Docker containers, images, or volumes.

The C16 research container itself is additive and administrator-created from an immutable digest, fixed GPU UUID, and reviewed mount whitelist. If it must be retired, stop for explicit user direction; deletion is not part of this plan.

## Data root rollback

`/data/c16` may be created only on an approved existing mount. Its rollback is limited to C16-owned additive directories after a user-approved retention/deletion decision. Never change partition tables, filesystems, LVM, fstab, or the ownership of other users' data. If storage is insufficient, retain the receipt and report the block.

## Required postcheck receipt fields

Postcheck repeats all GPU UUIDs, kernel, loaded NVIDIA parameters, package inventory, CUDA symlink state, Docker daemon/configuration summary, mount/fstab/space state, and Smart status where available. It includes the backup manifest SHA256, exact change argv, exact rollback argv if used, reboot evidence, and a statement that no forbidden operation occurred.
