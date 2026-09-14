# C16 RTX4080 userspace capability audit (U0)

Status: `PASS_USERSPACE_BUILD_PATH_AVAILABLE`.

The audit was run as `huangrulin` (UID/GID `1004:1004`) without sudo or Docker
access.  No host configuration was changed.

| Capability | Observation | U-stage decision |
| --- | --- | --- |
| Build tools | GCC/G++ 13.3.0, GNU Make 4.3, CMake 3.28.3, Ninja 1.11.1, Git, curl/wget, tar/bzip2/xz and pkg-config are present. | Sufficient for userspace builds. |
| System dev headers | OpenSSL and zlib headers are present; bzip2, ffi, readline, sqlite3, ncurses and lzma headers are absent. | Not a root blocker: build private dependencies under `/data/c16/env/build-deps-cpython310`. |
| CUDA tooling | `/usr/local/cuda-12.8/bin/nvcc` 12.8.93 and nvdisasm 12.8.90 are present. | Available for userspace CUDA/NVBit work. |
| Data capacity | `/data/c16` is on the existing root ext4 filesystem with about 648 GiB available. | Sufficient for the userspace runtime/wheelhouse stages. |
| Existing wheelhouse | No C16 wheels were present initially. | Materialize the exact 66-wheel closure as the research user. |

The missing system headers were handled entirely in userspace. No `apt`, sudo,
driver, CUDA, kernel, Docker, network configuration, mount, or reboot operation
was requested or performed.
