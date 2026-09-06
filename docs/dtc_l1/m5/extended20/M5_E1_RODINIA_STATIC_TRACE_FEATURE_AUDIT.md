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

`STATIC_TRACE_CANDIDATE` means only that the selected source scan found no
listed feature.  It does not establish trace compatibility or permit a
capture.  Runtime audit must prove the actual binary's operation, grouping,
address, ordering and cache semantics through the pinned NVBit/frontend path.
Any incompatibility remains workload-local and must be recorded before using an
execution-driven exception.
