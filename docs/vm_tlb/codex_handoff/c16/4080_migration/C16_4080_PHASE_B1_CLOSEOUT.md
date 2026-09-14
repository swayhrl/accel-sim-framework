# C16 RTX4080 Phase B1 closeout

## Status

`PASS_WITH_PREEXISTING_KERNEL_BOOT_SELECTION`

This receipt closes only the approved Phase B1 host preparation.  It does not
authorize model profiling, NVBit, Docker use by the research user, driver/CUDA
changes, or a further reboot.

## Authority and evidence interface

| Item | Value |
| --- | --- |
| Source authority branch | `hrl/c16-4080-host-protection-rollback-guard` |
| Source authority commit | `42353a6aa9c12ac8d6f1def65b1f97dbeace6933` |
| Execution branch | `hrl/c16-4080-phase-b1-closeout-ncu-n1` |
| Administrator evidence interface | `/home/huangrulin/C16_B1_ROOT_RECEIPT_AUDIT_20260914T092621Z.txt` |
| Interface SHA256 | `10d68dabf152e5f04117eea09cd3c35139092a144eb0f091be80e4572287451f` (`VERIFIED_RUN`) |
| Post-reboot ordinary-user inventory | `/home/huangrulin/c16_host_private_receipts/C16_4080_HOST_ADMISSION_PHASE_B1_POST_REBOOT_20260914T091806Z/POST_REBOOT_HOST_INVENTORY.txt` |

The root-private receipt directories were not accessed.  The SHA-closed
administrator-provided audit summary is the authority for their contents.

## Phase B1 closure

| Area | Result | Evidence |
| --- | --- | --- |
| Data root | `PASS` | `/data/c16` is on `/dev/nvme0n1p2` (`ext4`, UUID `b126b69a-3b55-443e-a282-4207be2a1022`), owned by `huangrulin:huangrulin`, mode `0750`; all eight approved child directories exist with the same ownership/mode. The administrator audit says both `/data` and `/data/c16` were originally absent. |
| Destructive storage/fstab | `NO_EVIDENCE_OF_CHANGE` | The administrator audit identifies only additive data-root evidence; no partition/LVM/mkfs/fstab operation is recorded. |
| NCU permission | `PASS` | `/etc/modprobe.d/c16-nvidia-profiling.conf` exists with exactly `options nvidia NVreg_RestrictProfilingToAdminUsers=0`; its current SHA256 is `82e888430290632fb6a5941f545a22ab31cffcc56268b57a211526698a1471ad`; the audit proves the prechange loaded state was `RmProfilingAdminOnly: 1`, an `UPDATE_INITRAMFS.log` was retained, and current loaded state is `RmProfilingAdminOnly: 0`. |
| Driver/CUDA preservation | `PASS` | Current GPU is RTX 4080 UUID `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`, driver `580.178.04`; `/usr/local/cuda` resolves to `/usr/local/cuda-12.8`. B1 package simulation/install evidence names only the four expected Toolkit packages. |
| NVIDIA Container Toolkit | `PASS` | `libnvidia-container1`, `libnvidia-container-tools`, `nvidia-container-toolkit-base`, and `nvidia-container-toolkit` are each `1.20.0-1`; `nvidia` Docker runtime is registered. The audit records an absent prechange daemon configuration and the resulting runtime configuration. |
| Docker assets | `NO_EVIDENCE_OF_DELETION` | Administrator audit contains asset summaries and no deletion command/result. The research user remains unable to access the Docker socket. A prior GPU passthrough canary is `USER_CONFIRMED`; its raw administrator artifact is not exposed through the supplied audit interface. |
| Network/DNS/proxy changes | `NO_EVIDENCE_OF_PROHIBITED_CHANGE` | The audit shows the approved NVIDIA package repository setup. It provides no evidence of DNS, proxy, routing, firewall, or SSH configuration change. |
| Privilege boundary | `PASS` | N0 records UID/GID `1004`, no sudo group, no docker group, and `Current: =` effective capabilities. The user-level Docker client is denied the socket. |

## Kernel -28 to -31 read-only investigation

Classification: `PREEXISTING_KERNEL_BOOT_SELECTION`.

`/var/log/dpkg.log*` records installation of `linux-modules-7.0.0-31-generic`,
`linux-image-7.0.0-31-generic`, and its headers on **2026-09-05 06:48–06:49**.
The corresponding `/boot/vmlinuz-7.0.0-31-generic` birth timestamp is
2026-09-05 06:48:25 +0800.  Phase A/B1 activity was on 2026-09-14, while the
machine was still running `7.0.0-28-generic` before reboot. Both `-28` and `-31`
image/header/modules packages remain installed now. Therefore `-31` was already
installed and available before B1 began; the later reboot selected the already
installed HWE default kernel.

The B1 administrator audit records `update-initramfs -u -k all`, which rebuilds
initramfs for installed kernels. It does not itself install a kernel package.
The B1 Toolkit simulation/install evidence lists only the four expected Toolkit
packages; no B1 evidence records an `apt`/`dpkg` kernel installation. Driver
`580.178.04` is currently loaded on `7.0.0-31-generic`: `nvidia-smi` succeeds,
`modinfo -F version nvidia` returns `580.178.04`, and NVIDIA modules are loaded.

## Open/unknown items

- The administrator audit interface does not expose a hash-closed standalone
  Docker GPU-passthrough-canary artifact; the canary claim remains
  `USER_CONFIRMED` in this closeout.
- No claim is made about why the normal package update of 2026-09-05 occurred;
  only its timestamp and its pre-B1 ordering are `VERIFIED_RUN`.
