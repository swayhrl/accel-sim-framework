# Capture hardware compatibility matrix

Status: `M4A-P_PREPARED`.  The table is capture-source policy, not a claim that
the frozen simulator supports every listed GPU.

| Route | GPU class | Use | Classification |
|---|---|---|---|
| Recommended paper route | RTX 3070, 3080 Ti, or 3090; compute capability 8.6 (SM86) | Llama short-context trace for the RTX3070-class paper target | `PAPER_COMPATIBLE_SELF_CAPTURE` unless author artifacts prove otherwise |
| Acceptable only with approval | another verified SM86 device | Same route after kernel/library identity is recorded | `DOCUMENTED_APPROX` unless shown equivalent |
| Not interchangeable | V100/SM70, A100/A800/SM80, Ada/SM89, Hopper/SM90, Blackwell/SM120 | Do not replay as an RTX3070 trace | unsupported for this paper route |
| Future research | H100/H200 (SM90) | separate Accel-Sim 2.0 Hopper-oriented study | outside M4A-P |
| Tool/metadata smoke only | RTX5090/Blackwell | NVBit tool experimentation, never formal H100/H200 or RTX3070 input | outside paper route |

## Rental recommendation

Rent one exclusive SM86 GPU with at least 24 GiB VRAM (RTX 3090 preferred for
headroom), CUDA toolkit compatible with the selected NVBit build, at least
500 GiB free local NVMe before formal tracing, and persistent storage or SSH
copy-back capacity.  The formal trace begins only after a tiny measured trace
updates the disk projection.  The 500 GiB is a conservative preparation gate,
not a measured Llama trace-size claim.

The source tracer presently pinned in this Framework downloads NVBit 1.7.6.
The rental environment must record the actual NVBit archive digest, driver,
CUDA runtime/toolkit, GPU name, compute capability, and selected SASS route.
