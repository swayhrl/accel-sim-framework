# Retry570 exact-target discovery boundary closeout

Status: `NVBIT_RETRY570_EXACT_TARGET_DISCOVERY_INCONCLUSIVE_PRE_LAUNCH_CALLBACK_BOUNDARY`.

This is a bounded, diagnostic-only replay of the historical exact
`indexSelectLargeIndex` PyTorch candidate. It ran no Llama/Qwen model, trace,
scientific capture, C target, insertion, or `nvbit_enable_instrumented`; the
closed 300-second watch and the historical 6+6 windows were not rerun.

Both 60-second attempts used the same frozen R2_D0_I64_A input and runtime
identity. Each emitted `EXACT_TARGET_SUBMISSION_BEGIN` then timed out, with no
`TARGET_CALLBACK_ENTER`, related-function, per-function `get_instrs`,
insertion, enable, launch-return, or same-process reuse marker. Thus the only
supported boundary is **after PyTorch's exact target submission marker and
before this NVBit tool's CUDA-launch callback entry**. It is not evidence that
any A--E stage caused the historical delay.

The newer pre-lookup control completed four preceding function-name lookups in
at most 1 microseconds each. The exact target emitted
neither a pre-lookup BEGIN nor a target-callback marker. Across its
12 post-submission samples, the process remained
CPU-active (104--156%), GPU
utilization was 0%, the CUDA-attached process used 335 MiB, and no child
`nvdisasm` process was observed. Non-destructive status/wchan/syscall snapshots
were retained; kernel-stack access was denied by node policy, so this report
does not claim a symbolized native stack.

The prior C4 GEMM result (89 related functions, 88 enumerated, 66,032 static
instructions, 19.969523 s cumulative `nvbit_get_instrs`) remains a useful
general mechanism reference, but it cannot be mapped to this exact target:
the exact target callback never arrived. Therefore no related-function count,
unique count, static-instruction count, per-function timing distribution,
pathology, duplicate-discovery result, or first-vs-second reuse result exists
for the historical target.

The next smallest informative experiment is **not authorized by this
publication**: one bounded exact-input, no-op NVBit CUDA-launch-callback arrival
probe with no name lookup, `get_related_functions`, `get_instrs`, insertion,
enable, trace, model, or C target. Until explicitly authorized and successful,
the Lane-G Llama state remains
`NVBIT_RETRY570_LLAMA_MODEL_CANARY_INCONCLUSIVE_FILTERING_NOT_DISAMBIGUATED`.
