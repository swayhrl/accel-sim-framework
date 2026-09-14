# C16 RTX4080 security model

## Principal separation

| Principal | Permitted role | Explicitly not granted |
| --- | --- | --- |
| Administrator | Host setup/maintenance, driver/module configuration, image/mount approval, Docker container creation | Scientific workload execution as root or a reason to broaden research privileges |
| Research user | Ordinary UID/GID process inside the administrator-created container; NCU only after N0 acceptance | sudo, Docker group, Docker socket, `CAP_SYS_ADMIN`, `--privileged`, host-root/high-privilege mounts |
| Container | Fixed image digest, fixed GPU UUID, fixed mount whitelist, numeric research UID:GID | Docker daemon control, host namespace/control-plane access, capability additions |

Docker group membership is equivalent to high host control and is forbidden for the research user. Docker is an administrator control plane, never a research in-container dependency.

## Container requirements

- The administrator records image digest, image inspection hash, container create command hash, selected GPU UUID, UID:GID, and each mount source/destination/mode.
- `--privileged` is forbidden. No `CAP_SYS_ADMIN` is added; use `--cap-drop=ALL` unless an administrator-reviewed minimal exception is documented.
- `/var/run/docker.sock`, `/`, `/etc`, `/root`, `/proc` and `/sys` broad host binds are forbidden. Do not add a device-broad bind as a substitute for NVIDIA Container Toolkit GPU selection.
- Mount only reviewed model, wheelhouse, output/raw, and read-only source locations. The raw/output mount must not include a Git worktree if it can cause unreviewed commits or asset mutation.
- Never place NCU and NVBit in one formal model process. NCU is a separate formal run; NVBit is a separate formal run with no NCU injection/profile active.

## NCU profiling permission policy

For this dedicated/trusted RTX4080 research host, the recommended administrator-owned configuration for driver `570.124.04` is:

```conf
options nvidia NVreg_RestrictProfilingToAdminUsers=0
```

This makes NVIDIA GPU performance counters available to non-admin users. It does not confer any other authority. N0 proves the research user remains non-root, has no sudo/Docker membership/SYS_ADMIN, and sees the loaded unrestricted profiling state before N1 is allowed.

This is unsuitable for an untrusted multi-user host because performance counters can expose cross-workload information. On a future untrusted/shared host, restore restricted profiling (`NVreg_RestrictProfilingToAdminUsers=1` or remove the override), apply the host's module reload/reboot procedure, retain a receipt, and block ordinary-user NCU acceptance.

## Audit failure handling

Any unexpected Docker group/sudo membership, Docker socket mount, privileged/capability addition, UUID drift, image-digest drift, mount-whitelist drift, restricted/unknown NCU state, or stale measurement process is a hard stop. Fix the policy under the administrator account, write a new receipt, and restart acceptance from the affected gate. Do not work around a failure by using root inside the research container.
