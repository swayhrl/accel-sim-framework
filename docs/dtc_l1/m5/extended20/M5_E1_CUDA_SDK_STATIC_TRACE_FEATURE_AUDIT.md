# M5.E1 — CUDA SDK 4.2 static trace-feature audit

Status: **STATIC_SOURCE_AUDIT_COMPLETE — NO V100 CAPTURE CLAIM**

Source: clean CUDA SDK 4.2 source commit
`b059fdae25c2aabf737486aada743fca114469ce`.  The selected sample directories
were scanned for atomics, CUDA streams, constant-memory declarations/transfers
and texture operations.  All eight rows also have recorded local CUDA-11.8
`sm_70` build/PTX reproducibility preflights in
`CUDA_SDK_E1_SOURCE_AUDIT.md` (FWT additionally in
`FWT_11_19_E1_RECOVERY.md`).  Those local artifacts are available provenance,
not a real-V100 executable/runtime/trace identity.

| workload | selected source evidence | static classification | V100 capture consequence |
| --- | --- | --- | --- |
| BlackScholes | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | local CUDA-11.8/sm70 preflight recorded; real-V100 output smoke, checker verdict, input/launch/runtime freeze and dynamic contract required |
| convolutionSeparable | `convolutionSeparable.cu` declares `__constant__ c_Kernel` and initializes it with `cudaMemcpyToSymbol` | RUNTIME_AUDIT_CONSTANT | local CUDA-11.8/sm70 preflight recorded; real-V100 smoke/checker/freeze required, then prove dynamic constant-memory representation and ordering |
| fastWalshTransform_11_19 | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | local CUDA-11.8/sm70 preflight recorded; real-V100 output smoke, checker verdict, input/launch/runtime freeze and dynamic contract required |
| scalarProd_13920 | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | local CUDA-11.8/sm70 preflight recorded; real-V100 output smoke, checker verdict, input/launch/runtime freeze and dynamic contract required |
| scan | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | local CUDA-11.8/sm70 preflight recorded; real-V100 output smoke, checker verdict, input/launch/runtime freeze and dynamic contract required |
| sortingNetworks | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | local CUDA-11.8/sm70 preflight recorded; real-V100 output smoke, checker verdict, input/launch/runtime freeze and dynamic contract required |
| transpose | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | local CUDA-11.8/sm70 preflight recorded; real-V100 output smoke, checker verdict, input/launch/runtime freeze and dynamic contract required |
| vectorAdd_6000000 | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | local CUDA-11.8/sm70 preflight recorded; real-V100 output smoke, checker verdict, input/launch/runtime freeze and dynamic contract required |

This is a conservative static screen.  `STATIC_TRACE_CANDIDATE` does not mean
`TRACE_CAPTURE_READY`; every row still needs its frozen real-V100 runtime
identity, source-defined checker/reference verdict, input/launch freeze and a
dynamic NVBit/frontend semantic-contract audit.  E2 remains locked until its
existing M5.2 authority permits it.
