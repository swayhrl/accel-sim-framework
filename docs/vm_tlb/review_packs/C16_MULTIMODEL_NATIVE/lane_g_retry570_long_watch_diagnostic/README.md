# Retry570 one-shot NVBit long-watch diagnostic

Status: `NVBIT_LONG_WATCH_DIAGNOSTIC_INCONCLUSIVE_TOOL_STARTUP_CONFIGURATION_FAILURE`.

The retained exact-kernel microreproducer closeout is unchanged; its existing
six-plus-six bounded NVBit windows were not rerun. A clean-source, non-capture
parent harness first ran the same finite microreproducer with no NVBit. It
observed first CUDA-kernel completion in 2.820031 seconds. It then created a
durable one-shot authorization and performed exactly one NVBit1.8 map-only
watch with a 300-second maximum and 5-second sampler. The map-only tool was
the already hash-closed lifecycle-free/no-instrumentation/no-tool-CUDA-
allocation discriminator.

The injected process reached `FIRST_CUDA_KERNEL_SUBMISSION_BEGIN`, but exited
in about 2.87 seconds before its first CUDA kernel because NVBit reported
`ERROR: /usr/local/cuda-12.4/bin/nvdisasm not found on PATH!!!`. The executable
exists on the node; the evidence only establishes that this tool invocation
used a configuration its NVBit-side path resolver rejected. It did **not** run
to 300 seconds. Therefore this does not distinguish a short 60-second guard
from an NVBit/PyTorch pre-first-kernel stall, and it cannot support either
`NVBIT_PYTORCH_PRE_FIRST_KERNEL_STALL_CONFIRMED` or
`NVBIT_PYTORCH_EXTREME_STARTUP_OVERHEAD`.

The one-shot authorization is complete and forbids a second long-watch. No
trace, static map, model, Qwen, Llama, C frozen target, timing evidence, or
scientific capture resulted. All retained small diagnostic payloads are
locally SHA-closed; raw payloads remain outside Git.
