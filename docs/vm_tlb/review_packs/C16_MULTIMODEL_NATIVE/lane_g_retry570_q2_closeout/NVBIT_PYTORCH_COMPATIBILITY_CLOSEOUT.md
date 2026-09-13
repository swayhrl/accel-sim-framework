# C16-G Retry570 NVBit/PyTorch compatibility closeout

Final status: `C16_RETRY570_NVBIT_COMPATIBILITY_NOT_RESOLVED_SAFE_TO_POWER_OFF`.

This retry did not alter the earlier 595-node scientific closeout, the C
selector, `SELECTOR_R/B48`, or a target row.  Every Q0--Q2 result is a
compatibility diagnostic and is `scientific_eligible=false`.

The new observed node is an RTX3090 / SM86 with driver 570.124.04.  The exact
CPython3.10 / torch2.5.1+cu124 environment was recreated from the 66-wheel
hash-closed wheelhouse; its final offline resolver, install, `pip check`, and
imports passed.  NVBit 1.7.6, its official `instr_count` tool, and the C16
tracer were independently built/hash-closed for CUDA 12.4 / sm_86.

The direct CUDA vector-add fixture passed baseline, official NVBit, and C16
tracer.  The C16 trace is real and directly shows the add kernel, SM86 binary,
stream 0, `ffffffff` active masks, and 4-byte memory operations.  That proves
only the direct fixture path.

The controlling PyTorch elementwise control passed normally.  With the
official NVBit tool and with the C16 tracer, the same minimal program reached
`TORCH_CUDA_INIT` and `ELEMENTWISE_PREPARE` but timed out at 180 seconds before
the first workload-kernel marker.  Neither attempt emitted a trace.  Therefore
the narrow, non-causal result is:

`NVBIT_PYTORCH_RUNTIME_OR_DRIVER_COMPATIBILITY_NOT_RESOLVED`

It is not evidence that the custom tracer alone is defective, and the 570
comparison is not proof that driver 595 was the sole cause.  The fail-closed
guard stopped queued GEMM tool rows; its raced baseline output lacks an exit
receipt and is explicitly not a gate result.  No model was transferred, so
there is no Llama/Qwen/AWQ compatibility claim.

Separately, this instance has only 50 GiB total data disk and about 37.8 GiB
free at closeout, below the 100 GiB formal-capture gate.  Thus no frozen C G2
or G3 target could be run even if Q2 had passed.  G2 is additionally
current-instance capability-limited by the one-attempt `ERR_NVGPUCTRPERM`
canary.  All retained diagnostic raw is locally hash-closed; no raw is in Git,
and there are no active GPU processes or remote-only required artifacts.

Recommended next environment, if a retry is authorized:

`PROFILING_ENABLED_SM86_NODE_WITH_NVBIT_SUPPORTED_DRIVER_AND_100GIB_TRACE_STORAGE`
