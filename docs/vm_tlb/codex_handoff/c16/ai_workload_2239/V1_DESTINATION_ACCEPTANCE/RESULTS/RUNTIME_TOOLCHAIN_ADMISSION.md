# Destination runtime and toolchain admission

Observed at `2026-09-14T14:43:07Z`; read-only inventory only. No GPU command,
model invocation, profiler, tracer, or CUDA fixture was launched.

| Component | Destination observation | Admission |
|---|---|---|
| Python | `/usr/bin/python3`, Python `3.10.12`; binary SHA256 `a2f33a6e006989270f4340528eb61f8f97366e00a5d1b602ac8672ea44fc56ae` | present |
| PyTorch | distribution not installed; importing `torch` raises `ModuleNotFoundError` | absent |
| `torch.version.cuda` | unavailable because PyTorch is absent | unavailable |
| transformers | distribution not installed | absent |
| CUDA toolkit / nvcc | `nvcc` not found; no `/usr/local` or `/opt` candidate found | absent |
| nvdisasm | not found | absent |
| NCU | `ncu` not found | `REBUILD_OR_VERIFY_REQUIRED`; no permission fixture run |
| NVIDIA visibility | `nvidia-smi` absent; no `/dev/nvidia*` or `/proc/driver/nvidia/gpus` visible | GPU unavailable to this container |
| GPU model / UUID / compute capability | unavailable without a visible GPU | unavailable |
| NVBit 1.7.5 | no archive, core library, tracer binary, or verified release root found in bounded destination-visible locations | `REBUILD_OR_VERIFY_REQUIRED` |

## Environment closure

`CUDA_VISIBLE_DEVICES` and `CUDA_MODULE_LOADING` are both unset. `LD_LIBRARY_PATH`
is unset. The observed `PATH` contains standard system paths and no CUDA bin
directory. No credential-bearing environment dump was retained.

## R5 comparison

`NEW_DESTINATION_RUNTIME_NON_EQUIVALENT_TO_R5` applies. The historical R5
runtime receipt requires PyTorch `2.5.1+cu124`, `torch.version.cuda == 12.4`,
transformers `4.46.3`, CUDA/nvcc/nvdisasm, a bound RTX4080 UUID, and
`CUDA_MODULE_LOADING=EAGER`; this destination has none of the required GPU
runtime/toolchain closure. Future measurements must obtain a new destination
receipt and cannot claim R5 runtime equivalence.

## GPU non-interference result

Process-name inspection found no independent Llama/Python/Torch/CUDA/VLLM
process. Because this container exposes no NVIDIA device or diagnostic tool,
the optional capability fixture was not run:

```text
GPU_DIAGNOSTIC_NOT_RUN_GPU_NOT_VISIBLE
```

This is not a claim that an unobservable host workload is idle; no action was
taken against any process.

## NVBit / NCU boundary

Repository source files for NVBit tooling are present, but source alone is not
a destination NVBit installation. There is no hash-closed NVBit 1.7.5 archive,
core library, tracer binary, or NCU executable here. No rebuild, installation,
or profiling was attempted in V1.
