# C16-G NVBit compatibility diagnostic

Status: `NVBIT_COMPATIBILITY_DIAGNOSTIC_COMPLETE`.

This is `NVBIT_COMPATIBILITY_DIAGNOSTIC_ONLY`, `NOT_SCIENTIFIC_CAPTURE`,
`NOT_FOR_C_SELECTOR`, and `NOT_FOR_H_MEMORY_FINGERPRINT`.  Every matrix row is
`scientific_eligible=false`.  C fixed-target authority
`d55075b7752380d6bd22328547db21a5e24eeed2` was neither executed nor changed.
The pre-existing formal terminal state remains
`C16_AUTODL_FINAL_G2_G3_COMPLETE_SAFE_TO_POWER_OFF`.

## Bounded result

The no-NVBit PyTorch CUDA elementwise and GEMM controls both passed through
CUDA synchronization and normal Python exit.  The first injection attempts
stopped at a missing `nvdisasm` PATH precondition.  A single, identical-workload
retry fixed only that PATH (`/usr/local/cuda-12.4/bin`); it changed no driver,
CUDA toolkit, package, model, target, or tracer binary.

After that fix, both the NVBit 1.7.6 release `instr_count` tool and the C16
memory tracer timed out (wrapper exit 124) after `TORCH_CUDA_INIT` and
`ELEMENTWISE_PREPARE` / `GEMM_PREPARE`, before the workload's first CUDA kernel
marker.  No trace was produced and no SIGABRT/SIGSEGV was reported.  Since the
official simple tool and the custom tracer fail at the same minimal PyTorch
boundary, the narrowest supported class is:

`NVBIT_PYTORCH_RUNTIME_OR_DRIVER_COMPATIBILITY_SUSPECTED`.

This is the user-specified Case D boundary—an environment/driver/runtime
compatibility suspicion—not evidence that the custom C16 tracer is the root
cause.  Driver 595.58.03 with NVBit 1.7.6 is recorded only as a
`SUPPORTED_COMPATIBILITY_HYPOTHESIS`; the diagnostic does not establish it as
the cause of the timeout.

## Stopping rule

D1 and D2 were the sole GPU diagnostic workloads.  D3--D7 were deliberately
not started: the basic NVBit/PyTorch route did not qualify and the 20-minute
wall-clock budget forbids jumping to Llama or AutoAWQ after the official-tool
failure.  In particular, this run makes no claim about AutoAWQ load or forward
compatibility.  It does not alter the prior G3 capability-limited disposition,
does not create a C target result, and does not emit a trace for H.

All 40 compact remote evidence files (19,333 bytes) were transferred and
matched locally under a deterministic bundle SHA256.  `raw_trace_file_count`
and `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT` are both zero; raw payloads are not
committed.

`RETRY_RECOMMENDATION = PROFILING_ENABLED_SM86_NODE_WITH_NVBIT_SUPPORTED_DRIVER`
