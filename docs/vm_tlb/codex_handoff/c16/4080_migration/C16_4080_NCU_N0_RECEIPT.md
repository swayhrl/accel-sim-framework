# C16 RTX4080 NCU N0 receipt

Status: `NCU_N0_ORDINARY_USER_PERMISSION_PASS`

| Field | Value |
| --- | --- |
| Raw N0 receipt | `/data/c16/ncu/canary/C16_NCU_N0_20260914T093737Z.txt` |
| Raw N0 SHA256 | `56cebcfdc9b61ff89bf682c427b20653edb0804b8ca38ab74dc69bae10aedf8d` |
| Research identity | `huangrulin`, UID/GID `1004:1004`, groups `huangrulin users` |
| sudo/docker group | `NO` / `NO` |
| Effective capabilities | `Current: =` |
| GPU | RTX 4080, `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`, CC `8.9` |
| Driver / kernel | `580.178.04` / `7.0.0-31-generic` |
| CUDA | `/usr/local/cuda -> /usr/local/cuda-12.8`; nvcc `12.8.93` |
| nvcc SHA256 | `59e4e55f9a38b78c590df1e28a69dad91052958f18a03868ca4a547c043fbba7` |
| Frozen NCU | `/opt/nvidia/nsight-compute/2025.1.1/ncu`, `2025.1.1.0` |
| NCU SHA256 | `a44ff2c735c4dcf66c78f3f430155805d6a0b1f74f26331f98ecec03bfbf3f1a` |
| Loaded profiling state | `RmProfilingAdminOnly: 0` |

N0 performed no CUDA workload, NCU capture, Docker command, NVBit injection, or
host mutation. It establishes the ordinary-user permission gate for N1.
