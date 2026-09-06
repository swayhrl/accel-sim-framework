# M5.0BT SpMV exact capture closeout

Status: **ARCHIVE_PASS; COPYBACK_SHA_PASS; LOCAL_IMMUTABLE_PASS**.

This closes physical capture and immutable transfer of the exact Paper-10
SpMV payload.  It is not a replay result or a formal performance row.

| field | evidence |
| --- | --- |
| canonical workload | `parboil_spmv_medium_bcsstk18` |
| wrapper / support source | `gpgpu-workloads@de9cf4293f418877aa9cdb6a2395338ca06674a6`; `parboil@4e0fc54866546efa44fe93af57c9cef62f6c8eb9` |
| required wrapper source | `main.cu`, `jds_kernels.cu`, `gpu_info.cc`, `file.cc`, `convert_dataset.c`, `mmio.c`; all capture-time SHA-256 values are in `CAPTURE_RESULT.json` |
| input / checker | matrix `abbe1909...c82ec9`, vector `d155de2...2e49061`, reference `69314cf6...0c4c4f1`; binary checker PASS |
| build / tracer | CUDA 11.8, sm70, `-O2`, shared cudart; NVBit-v1.8 |
| capture geometry | 50 captured invocations, 50 raw traces, 50 grouped `.traceg` traces |
| trace identity | bundle `d8790ea7279aa79345650ffaafc61835187d8b1e6c4b10a6e6e2cc24891db270`; `kernelslist.g` `a3ef80aa...5817fbf`; traceg set `7ff88da2...736cb28` |
| archive | `spmv.tar.zst`, 53,292,499 bytes, SHA-256 `5d7d92ca08d6a3c2b8f5e4b7085428dcaa1ec5bdae330816132113eefb3f0852` |
| SIM_HOST receipt | resumed archive SHA PASS, unpacked `SHA256SUMS` PASS, controller `valid_bundle()` PASS, `LOCAL_IMMUTABLE_PASS.json` written |

## Tree-identity terminology

The transferred clean wrapper repository is frozen at Git root tree
`5b8b3a8ea5121d89d451c54e4ec68dd300d0d5c2`.  The capture result additionally
records its controller-produced wrapper index fingerprint
`5ff073c349bd3f5080b2fac64c473e18d3852732d8a24c0cbd6d87c1d94f48f5`.
They are distinct fields and must not be compared as if both were Git tree
objects.  The commit, required source-file hashes, clean-source gate, and
capture-time fingerprint together bind the actual build surface.

The ordered queue has advanced to the already prepared 2MM workload. Its
controller has reached `ARCHIVE_PENDING` after capture/postprocess; no 2MM
archive, transfer, or result is claimed until its independent gates close.
