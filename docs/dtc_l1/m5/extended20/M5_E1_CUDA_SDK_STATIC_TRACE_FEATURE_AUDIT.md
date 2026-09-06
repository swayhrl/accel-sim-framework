# M5.E1 — CUDA SDK 4.2 static trace-feature audit

Status: **STATIC_SOURCE_AUDIT_COMPLETE — NO V100 CAPTURE CLAIM**

Source: clean CUDA SDK 4.2 source commit
`b059fdae25c2aabf737486aada743fca114469ce`.  The selected sample directories
were scanned for atomics, CUDA streams, constant-memory declarations/transfers
and texture operations.  The legacy sm52 provenance build is intentionally not
an executable or trace identity for this audit.

| workload | selected source evidence | static classification | V100 capture consequence |
| --- | --- | --- | --- |
| BlackScholes | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | clean CUDA-11.8/sm70 build, input/output smoke and dynamic contract required |
| convolutionSeparable | `convolutionSeparable.cu` declares `__constant__ c_Kernel` and initializes it with `cudaMemcpyToSymbol` | RUNTIME_AUDIT_CONSTANT | prove dynamic constant-memory representation and ordering before trace capture |
| fastWalshTransform_11_19 | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | clean CUDA-11.8/sm70 build, input/output smoke and dynamic contract required |
| scalarProd_13920 | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | clean CUDA-11.8/sm70 build, input/output smoke and dynamic contract required |
| scan | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | clean CUDA-11.8/sm70 build, input/output smoke and dynamic contract required |
| sortingNetworks | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | clean CUDA-11.8/sm70 build, input/output smoke and dynamic contract required |
| transpose | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | clean CUDA-11.8/sm70 build, input/output smoke and dynamic contract required |
| vectorAdd_6000000 | selected CUDA source scan found no atomic, texture, constant-memory or stream API | STATIC_TRACE_CANDIDATE | clean CUDA-11.8/sm70 build, input/output smoke and dynamic contract required |

This is a conservative static screen.  `STATIC_TRACE_CANDIDATE` does not mean
`TRACE_CAPTURE_READY`; every row still needs its frozen V100 binary, input,
checker/reference and a dynamic NVBit/frontend semantic-contract audit.
