# C16 RTX4080 administrator bootstrap

This is a host-arrival runbook, not an authorization to change a host now. It inherits the source closure in [C16_4080_MIGRATION_SOURCE_RECEIPT.md](C16_4080_MIGRATION_SOURCE_RECEIPT.md). All historical commands absent from that receipt remain `UNKNOWN`; the commands below are new-host administration steps, not claims about the Retry570 host.

## Roles and immutable boundary

The administrator account performs host initialization, NVIDIA driver/module maintenance, image acquisition, mount approval, and Docker container creation. The research account runs ordinary research processes as its own unprivileged UID/GID. It has no sudo access, is not in the `docker` group, and receives neither `CAP_SYS_ADMIN` nor a privileged container.

Only the administrator may use Docker on the host. Containers are created from a digest, one recorded GPU UUID, and a reviewed mount whitelist. Never use `--privileged`, never mount `/var/run/docker.sock` into a research container, and never bind host `/`, `/etc`, `/root`, or an equivalent high-privilege subtree.

## A. PRECHANGE AUDIT — no host-state change

This phase is read-only. Do not install packages, edit modprobe files, reboot, create users, alter Docker configuration, or launch any GPU workload.

1. Have the administrator run `util/vm_tlb/c16/host_4080/host_inventory.sh --collect --output <new-receipt>` and retain the output outside Git until sanitised.
2. Have the proposed research user run `ncu_permission_preflight.sh --collect --research-user <user> --output <new-receipt>`. This is N0 only: it queries state and must not profile a kernel.
3. Have the administrator run `host_security_audit.sh --audit --research-user <user> --output <new-receipt>` and `docker_runtime_preflight.sh --plan ...`; do not create a container yet.
4. Review the receipts for: selected RTX4080 UUID; OS/kernel; driver; CUDA, nvcc and nvdisasm; NCU version; NVIDIA Container Toolkit; storage; current profiling state; absence of research-user sudo/docker membership/SYS_ADMIN; and an explicit mount whitelist.
5. Record all actual values that were `UNKNOWN` in the source receipt. In particular, record image digest, `CUDA_VISIBLE_DEVICES` UUID mapping, PATH, LD_LIBRARY_PATH, Docker/runtime versions, and all new build/install argv.

The A receipt must be approved by the host owner before B begins. A failed or incomplete receipt is a stop, not a reason to experiment with privileges or profiler flags.

## B. APPROVED INSTALL/CONFIGURATION — administrator only

Perform these only after the approved A receipt is present.

1. Create or verify the research account with a fixed numeric UID/GID. Do not grant sudo and do not add it to `docker` or any administrator-equivalent group.
2. Install the approved NVIDIA driver `570.124.04`, CUDA/Nsight package set, Docker Engine, and NVIDIA Container Toolkit using host-owner-approved package provenance. Record package versions and image digest; do not infer them from this document.
3. For the dedicated/trusted RTX4080 research host, create the administrator-owned modprobe configuration:

   ```conf
   # /etc/modprobe.d/c16-nvidia-profiling.conf
   options nvidia NVreg_RestrictProfilingToAdminUsers=0
   ```

   Apply the distribution-required initramfs/module reload/reboot procedure, then rerun A and prove that the loaded NVIDIA profiling state is unrestricted. This setting exposes only NVIDIA GPU performance counters. It does not grant sudo, Docker-daemon access, `CAP_SYS_ADMIN`, root filesystem access, or a privileged container.
4. If the host becomes an untrusted multi-user/shared machine, immediately restore restricted profiling: remove/disable the C16 override or set `NVreg_RestrictProfilingToAdminUsers=1`, apply the distribution-required reload/reboot procedure, and record the new loaded state. Suspend ordinary-user NCU acceptance until reviewed.
5. The administrator obtains the fixed image by digest, prepares approved model/wheelhouse/raw directories with least-privilege ownership, and writes a mount whitelist. The whitelist must reject `/var/run/docker.sock`, `/`, `/etc`, `/root`, device-broad binds, and writable host source trees.
6. The administrator creates the research container with fixed image digest, one explicit RTX4080 UUID, the reviewed mount list, numeric research UID:GID, `no-new-privileges`, no added capabilities, and no `--privileged`. Record the complete `docker inspect` output/hash in a host-private receipt.
7. Run `docker_runtime_preflight.sh --audit-container <name> ...` and the N0 preflight as the research UID. Any policy failure blocks N1 and all model work.

## Explicitly unresolved at source freeze

The source closure does not contain historical CPython/NVBit/tracer build argv or a final-model `LD_LIBRARY_PATH`. Capture them as new 4080 evidence if rebuilt. A new RTX4080 code object also requires a new static map and target binding; never reuse an RTX3090 kernel ID, static range, or `DYNAMIC_KERNEL_RANGE`.
