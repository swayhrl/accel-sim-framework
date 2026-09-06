# M5.0BT 2MM capture readiness

Status: **AUTODL_SOURCE_TRANSFER_VERIFIED; LAUNCH_PENDING_SPMV_PREDECESSOR**.

This prepares only the CPU-side prerequisites for the Paper-10 2MM physical
capture.  It does not launch, build, trace, archive, or register a 2MM result.

## Frozen workload contract

| field | verified value |
| --- | --- |
| canonical ID | `polybench_2mm_1024` |
| source | `polybenchGpu@5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c`; tree `ae42121e0eccd437e995ff86cb801746da410ce0` |
| source file | `CUDA/2MM/2mm.cu`; SHA-256 `dec4988b28f94c75dfdc3b3048e1dc01511fb8cfcdc0314552451002be9d4a0f` |
| dimensions header | `CUDA/2MM/2mm.cuh`; SHA-256 `9eba6b40d9a0ae23c5033ee5ce09b8c493f27d88e07f2e1244430e94b5075745`; standard `NI=NJ=NK=NL=1024` identity |
| clean source transfer object | deterministic Git-tree tarball, SHA-256 `70f245e0e8c387b2c9c28148433750bfcc1e3bf3945fdf7a747adc813886d90d`; 753 members; independent unpack/hash revalidation PASS |
| exact V100 build | `build_m5_polybench_cuda_trace_sm70.sh --workload twomm`; CUDA 11.8, `-arch=sm_70 -O2 -cudart shared` |
| correctness gate | `verify_m5_polybench_output.py 2mm <application-log>`; exactly one source CPU/GPU mismatch verdict and it must be zero |
| runtime contract | no external input arguments; expected generated dimensions `1024x1024x1024x1024`; default cache preference only |

`bash -n` accepts the dedicated sm70 builder and the checker exposes `2mm` as
an accepted workload.  The tarball is used rather than an unverified source
checkout: it was generated from the clean pinned Git tree and its extracted
2MM source and dimension-header hashes exactly match the committed Paper-10
manifest.

The exact tarball has also reached the isolated AutoDL source-transfer
staging area.  Its transfer SHA-256 and an independent remote unpack of its
top-level `polybenchGpu-5584aaa7/` directory reproduce both frozen 2MM source
and dimension-header hashes.  It is staged evidence only: no 2MM source path
has been substituted into a running controller and no 2MM capture has begun.

## Capture sequencing and admission

When AutoDL control returns, CPU-side preparation must not wait for SpMV
capture completion: transfer and verify the tarball in an isolated source
location, recheck the source/header/tar hashes above, and pre-create the
controller-owned isolated 2MM output namespace.  It remains fail-closed on:

1. the current capture lock and ordered predecessor (`SYR2K`, then SpMV);
2. one visible V100 / CUDA 11.8 / NVBit 1.8 preflight;
3. unchanged source and controller contracts;
4. source checker PASS after the actual 2MM execution; and
5. the existing storage-admission gate before capture and archive.

After SpMV reaches its safe bundle/archive state and the lock is free, the
existing supervisor may start 2MM immediately.  Archive/copyback of an
earlier workload may overlap this capture only under that admission gate.
