# C16 RTX4080 host change guard

This guard extends the administrator bootstrap without changing the established research-account permissions. It is CPU-only planning, based on `6327b2080648491e96355ca74e406681d10910af`; it authorizes no host change by itself.

## Governing rule: audit first, preserve if compatible

`570.124.04` is a known-good source-environment reference, not an instruction to overwrite an existing RTX4080 driver. Before any change, inventory the installed driver, kernel/module state, CUDA toolkits/symlinks, Docker/Container Toolkit, NCU, NVBit closure, disks, and existing workloads. Preserve each compatible component.

Compatibility is established by recorded evidence, not package-name resemblance. A currently installed driver/toolkit stack may be preserved when it supports the selected RTX4080, the container runtime admits the selected UUID, and the later N0–N6/NVBit gates can re-close their 4080-specific evidence. The existing RTX3090/570 source closure is valuable reference evidence but cannot prove an untested 4080 code object. A mismatch only creates a reviewed decision point; Codex must not select a driver upgrade or downgrade.

## Absolute default prohibitions

The following are **FORBIDDEN** unless the user later gives specific approval naming the target and scope:

- `mkfs`, `fdisk`, `parted`, destructive LVM changes, partition-table changes, or reformatting;
- kernel upgrade/downgrade;
- BIOS, SecureBoot, or firmware changes;
- NVIDIA-driver purge/removal;
- deletion of any Docker container, image, or volume;
- SSH, firewall, routing, DNS, or other network changes;
- deletion or ownership change of another user's directory;
- modification of shared CUDA paths or system Python;
- persistent GPU firmware, power-limit, clock, or overclock tuning.

Do not convert “not enough C16 disk space” into a storage reconfiguration. Do not convert a tool mismatch into a package purge. Report the condition with the audit evidence and stop.

## PRECHANGE receipt contract

Run the updated read-only `host_inventory.sh --collect` and retain a timestamped host-private receipt. It must contain at least:

- OS/current kernel; CPU/RAM; `lsblk -f`; `mount`/`findmnt`; free space; and basic non-waking SMART health where queryable;
- all GPU model/UUID/driver/compute-capability rows; CUDA `nvcc`/`nvdisasm`; CUDA symlink state;
- dpkg or rpm inventory for NVIDIA/CUDA/Docker/Container Toolkit; `/etc/modprobe.d` NVIDIA-related file paths and SHA256; loaded `/proc/driver/nvidia/params`;
- Docker version/info, `/etc/docker/daemon.json` (if present) plus SHA256, and existing container/image summaries;
- `/etc/fstab`; SecureBoot state if `mokutil` is available; NCU/NVBit compatibility observations; and the research user's security audit.

The audit receipt is an input to approval, not a disposable log. Sanitise secrets before any Git-adjacent publication; raw host receipts remain outside Git.

## Backup-before-write rule

Every intended host configuration write requires a unique change ID and a timestamped backup in an administrator-only directory before editing. Preserve the original bytes, mode, owner, group, path, and SHA256. The prechange manifest must also identify an absent original file as `ABSENT`—never fabricate a backup.

At minimum, back up the exact target file before modifying NVIDIA modprobe settings, Docker daemon configuration, or fstab. Record the postchange SHA256 separately. Never overwrite a prior C16 backup directory. Package inventories and Docker asset summaries are rollback evidence, not permission to remove or reinstall packages.

## Data filesystem policy

The preferred C16 data root is `/data/c16` on an **existing, mounted, sufficiently large filesystem** selected in the prechange receipt. The administrator may create that directory only after approval, with least-privilege ownership/mode, and must record the mount source, filesystem UUID/type, available bytes before/after, directory ownership, and SHA256 manifest location.

If no suitable existing mounted filesystem has adequate space, report `C16_DATA_ROOT_UNAVAILABLE_NO_DESTRUCTIVE_STORAGE_CHANGE`. Do not partition, format, modify LVM, or edit fstab for C16 without a new explicit authorization.

## NCU remains an approved capability

On a dedicated/trusted RTX4080 research host, `options nvidia NVreg_RestrictProfilingToAdminUsers=0` remains the recommended approved configuration. It exposes NVIDIA GPU performance counters only; it does not alter no-sudo/no-Docker/no-SYS_ADMIN research-account policy. The parameter's prior loaded value, backup SHA, post-reboot value, and rollback method are mandatory receipt fields. If the host becomes untrusted multi-user/shared, restore restricted profiling and suspend ordinary-user NCU acceptance pending review.
