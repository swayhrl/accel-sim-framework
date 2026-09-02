# Capture hardware compatibility matrix

Status: `M4A-P_PREPARED`.  The table is capture-source policy, not a claim that
the frozen simulator supports every listed GPU.

| Route | GPU class | Use | Classification |
|---|---|---|---|
| Preferred formal Route E | 4 x same-model SM86 GPUs on one node, ideally 24 GiB+ each | real TP=4; trace rank 0 only | `PAPER_COMPATIBLE_SELF_CAPTURE` |
| Route A, approval required | 1 x 24 GiB+ SM86 | local one-rank operator/weight-shard emulation only | `DOCUMENTED_APPROX` after explicit approval |
| Rejected formal default | 1 x SM86 with full Llama-3.2 1B | full-model single-GPU trace | rejected; diagnostic only |
| Not interchangeable | V100/SM70, A100/A800/SM80, Ada/SM89, Hopper/SM90, Blackwell/SM120 | Do not replay as an RTX3070 trace | unsupported for this paper route |
| Future research | H100/H200 (SM90) | separate Accel-Sim 2.0 Hopper-oriented study | outside M4A-P |
| Tool/metadata smoke only | RTX5090/Blackwell | NVBit tool experimentation, never formal H100/H200 or RTX3070 input | outside paper route |

## Rental recommendation

For the preferred formal route, rent one exclusive **4 x SM86** node (same
model/driver image; 24 GiB+ per GPU) with 500 GiB free local NVMe before
formal tracing and persistent copy-back capacity. This has higher availability,
coordination, NCCL, and tracing complexity than Route A. A single RTX3090 is
not a formal recommendation unless Route A is later selected and approved.
The disk gate is conservative and must be recalibrated after the tiny trace.

The source tracer presently pinned in this Framework downloads NVBit 1.7.6.
The rental environment must record the actual NVBit archive digest, driver,
CUDA runtime/toolkit, GPU name, compute capability, and selected SASS route.
