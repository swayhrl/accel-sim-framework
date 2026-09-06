# M5.E1 — Rodinia static trace-feature audit

Status: **STATIC_SOURCE_AUDIT_COMPLETE — NO V100 CAPTURE CLAIM**

Source: clean GPU-app-collection commit
`dad09cb0487845edc7524ded814c6cde9f0ef6a1`, selecting the approved Rodinia
3.1 CUDA application directories.  The scan covers direct CUDA/C++ sources
for atomics, CUDA streams, constant-memory transfers/declarations, and texture
operations.  It is source-only and does not freeze a V100 binary, input,
checker, trace or trace semantic contract.

| workload | selected source evidence | static classification | V100 capture consequence |
| --- | --- | --- | --- |
| cfd_097k | `cfd/euler3d.cu` declares `__constant__` flow/flux values and populates them with `cudaMemcpyToSymbol` | RUNTIME_AUDIT_CONSTANT | prove dynamic constant-memory representation and ordering before trace capture |
| btree | selected `b+tree` CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | still requires clean V100 build, frozen input/checker and dynamic trace contract |
| dwt2d | selected `dwt2d` CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | still requires clean V100 build, frozen input/checker and dynamic trace contract |
| gaussian | selected `gaussian` CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | still requires clean V100 build, frozen input/checker and dynamic trace contract |
| hotspot1 | selected `hotspot` CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | still requires clean V100 build, frozen input/checker and dynamic trace contract |
| lud | selected `lud` CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | still requires clean V100 build, frozen input/checker and dynamic trace contract |

## hotspot1 local `sm_70` build preflight (2026-09-06)

The exact Rodinia 3.1 source was independently materialized twice from clean
`gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1`, tree
`351b090ddbd315e40f1745895c2dffd51a79c98b`. CUDA 11.8.89 built both copies
with `-arch=sm_70 -O2 -cudart shared`; M5-E1-003 post-link normalization made
the two artifacts byte-identical. The only compiler diagnostic was the
pre-existing ignored `fgets` return value in the frozen source.

| item | identity / result |
| --- | --- |
| selected source | `hotspot.cu` SHA-256 `0f679be008be285d26ebd7d71eba47b164914dd52873c26ee63beecda2f68cc0` |
| canonical executable | two `strip --strip-unneeded` artifacts: SHA-256 `4afc60e5fb6f3bb1f2ae0d0d210573e62babd828c5f207ce90fad24476f4e6a0` |
| PTX | two artifacts: SHA-256 `d6d0305f324bd42f42709adaef61472275c5b3c12f24ad7b292aefa466b4ca21`; `.target sm_70`, `_Z14calculate_tempiPfS_S_iiiiffffff` entry |
| classification | `LOCAL_SM70_BUILD_PREFLIGHT_PASS`; retain `INPUT_READY`, not `BUILD_READY` |

This host-only preflight neither executes the source-defined real-device
checker nor freezes the V100 input/runtime/launch contract. It does not prove
the dynamic trace contract and does not make `hotspot1` eligible for capture;
the row remains outside the Paper-10 priority queue.

## btree local `sm_70` build preflight (2026-09-06)

The exact Rodinia 3.1 `b+tree` tree was independently materialized twice from
clean `gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1`, tree
`26cdc6bcb8332767f274a5ed7e0305862d8e1abf`. The original Makefile's full
source/object/link graph was retained. Its historical quoted multi-`gencode`
driver expansion is not accepted by CUDA 11.8, so the isolated build wrapper
supplied only an equivalent compiler-driver override:
`CUD_C='/usr/local/cuda-11.8/bin/nvcc -arch=sm_70'` and the CUDA 11.8 lib64
path. No workload source, object selection, launch source, input, or runtime
option was changed.

| item | identity / result |
| --- | --- |
| selected source set | `main.c` `f461ed1696a757de44b4d3453b5699e5cb8cc0b71ff06be8a650ce44f26ef918`; `kernel_gpu_cuda.cu` `4c79bdc48cc5bc03612e703ac86f13e190f7f5f3b6b1f32616447a12113fefb7`; `kernel_gpu_cuda_2.cu` `7b2da2312b0b7c38f6c83a5cb8a8ae5394be155f7d7dc6373a1d2b7b72267daa`; wrappers/utilities are bound by the tree above |
| canonical executable | two `strip --strip-unneeded` artifacts: SHA-256 `fbb22305a08e5d220ef44b55f5d7e8665d2db54fcc2fb252436f9fa51e91d445` |
| PTX kernel set | `findK` SHA-256 `d5f57379045a2ea7f0dc4eaa8e114128ad54caf97aca969b70baca5397d199fd`; `findRangeK` SHA-256 `8a229d085e1c3db557149f0fb850516318116289a0eb3dfbc59fd3ddc3e0934e`; both `.target sm_70` |
| classification | `LOCAL_SM70_BUILD_PREFLIGHT_PASS`; retain `INPUT_READY`, not `BUILD_READY` |

The raw linked ELFs differ only in nvcc-generated local temporary-name
metadata and normalize byte-identically under M5-E1-003. This is a host-only
build/selected-kernel PTX proof: the frozen btree input still needs its
real-V100 output/reference checker, launch/runtime freeze, and dynamic trace
semantic audit before capture eligibility is assessed.

## lud local `sm_70` build preflight (2026-09-06)

The exact Rodinia 3.1 `lud` source tree was independently materialized twice
from clean `gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1`,
tree `ac7c71d010fa1e51f8bd5a50e192a6d9e114ac15`. CUDA 11.8.89 built the
original source/object/link graph with `-arch=sm_70 -O3 -use_fast_math`; the
historical unsupported architecture flags were omitted while retaining the
source-defined optimization and math mode. M5-E1-003 normalization makes both
linked artifacts byte-identical.

| item | identity / result |
| --- | --- |
| selected source set | `cuda/lud.cu` `ef26e175c582210a7b55bba1ed9ea45cce4c8ba2ede17e89b0f4bac9aa7b6757`; `cuda/lud_kernel.cu` `fe3d0a5f06c82947f54cbf6fd9a75342b61263808a1587ead929fc3f8763fdc0`; `common/common.c` `8a6cca89c03be97a690a5fc0a657810dabd451e86c34bf97857785a36eb28e5c` |
| canonical executable | two `strip --strip-unneeded` artifacts: SHA-256 `49e05942e6159f80bbda0450e8d2bd92236525f4f9f7b639c1edac5a123f0965` |
| PTX | two artifacts: SHA-256 `5b0544b22b7f1af5c30cd40afd253bfd28968106da2fc5d85346b54da5d052eb`; `.target sm_70`; `lud_diagonal`, `lud_perimeter`, and `lud_internal` entries |
| classification | `LOCAL_SM70_BUILD_PREFLIGHT_PASS`; retain `INPUT_READY`, not `BUILD_READY` |

This build has not executed the source-defined V100 verifier, frozen the
runtime/input/launch identity, or undergone a dynamic trace-semantic audit.
It is not a capture authorization and leaves the Paper-10 capture priority and
the E1 readiness counts unchanged.

`STATIC_TRACE_CANDIDATE` means only that the selected source scan found no
listed feature.  It does not establish trace compatibility or permit a
capture.  Runtime audit must prove the actual binary's operation, grouping,
address, ordering and cache semantics through the pinned NVBit/frontend path.
Any incompatibility remains workload-local and must be recorded before using an
execution-driven exception.
