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

`STATIC_TRACE_CANDIDATE` means only that the selected source scan found no
listed feature.  It does not establish trace compatibility or permit a
capture.  Runtime audit must prove the actual binary's operation, grouping,
address, ordering and cache semantics through the pinned NVBit/frontend path.
Any incompatibility remains workload-local and must be recorded before using an
execution-driven exception.
