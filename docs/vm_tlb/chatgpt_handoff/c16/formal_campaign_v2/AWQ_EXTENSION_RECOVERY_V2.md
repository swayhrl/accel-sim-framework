# Qwen2.5-7B-AWQ Extension Recovery V2

## Goal

Recover a real CUDA AWQ kernel backend if practical, instead of silently profiling AutoAWQ's naive unfused fallback.

The existing unfused result remains valid as its own deployment identity. A fused backend is a separate deployment and must never be called equivalent without evidence.

## Background

AutoAWQ prefers `awq_ext` when the extension is importable. The official AutoAWQ kernels package contains the `awq_ext` CUDA extension and supports NVIDIA compute capability >= 7.5; RTX4080 is SM89.

Because AutoAWQ/AutoAWQ_kernels are archived upstream, binary-wheel compatibility with the active Torch/CUDA ABI cannot be assumed. Prefer an environment-matched source build.

## Step 1 — freeze current environment

Record before mutation:

```text
python --version
python -c 'import torch; print(torch.__version__, torch.version.cuda)'
nvcc --version
nvidia-smi
pip show autoawq autoawq-kernels transformers
python -c 'import awq; print(...)'
python -c 'import awq_ext'
```

Also record compiler versions and active virtual environment.

Do not upgrade/downgrade the base Torch stack merely to obtain a wheel.

## Step 2 — isolated source build

Build in an isolated staging/venv or wheel build directory, not by destructively mutating the working environment first.

Preferred build source:

```text
casper-hansen/AutoAWQ_kernels
```

Build against the exact active Torch/CUDA headers and target only the required architecture where possible:

```text
COMPUTE_CAPABILITIES=89
```

If the build system supports explicit Torch/CUDA version variables, bind them to the active environment rather than inventing another ABI.

Produce a local wheel or installable artifact and record its SHA256.

## Step 3 — import/link validation

Require:

```text
python -c 'import awq_ext; print(awq_ext)'
```

Then inspect linked CUDA/Torch symbols if needed (`ldd`, `nm`, import error text). Undefined-symbol failures are ABI failures, not reasons to silently fall back.

If source needs a small compatibility patch for the active Torch API, patch only the kernel build layer, document the diff, and keep the resulting deployment identity explicit.

## Step 4 — numerical microvalidation

Before whole-model use, compare the fused extension with the existing reference path on deterministic small tensors/weights:

- dequantization output where exposed;
- GEMM output;
- representative batch/token shapes;
- FP16 tolerance recorded explicitly.

Use deterministic seeds. Record max/mean absolute error and allclose result.

## Step 5 — model-path validation

Run frozen Qwen2.5-7B-AWQ S2_TEXT native/NSYS under the fused environment.

Require evidence that:

- `awq_ext` is imported;
- fused/extension kernels actually execute;
- model output token/checksum is stable;
- no CPU offload occurred;
- model revision/input binding are unchanged.

Create deployment identity such as:

```text
qwen25_7b_awq_autoawq_awqext_sm89
```

Do not overwrite `qwen25_7b_awq_autoawq_unfused`.

## Step 6 — target census

The fused backend has a different kernel population. Re-run bounded NSYS/static-MREF discovery for fused AWQ rather than reusing unfused launch selectors.

Prioritize:

- fused quantized GEMM/GEMV;
- dequant/metadata access if separate;
- attention;
- Decode early/late memory targets.

## Fallback hierarchy

1. source-built `awq_ext` on the existing Torch/CUDA environment;
2. compatible prebuilt `autoawq-kernels` only if exact ABI match is demonstrated;
3. Triton AWQ only as a separately named deployment if `awq_ext` cannot be repaired;
4. existing unfused AutoAWQ remains a control deployment.

A Triton or naive fallback must never be labeled as the fused `awq_ext` result.

## Final classifications

- `AWQ_EXT_PASS`
- `AWQ_EXT_PASS_WITH_LOCAL_COMPAT_PATCH`
- `AWQ_EXT_ABI_BLOCKED`
- `AWQ_TRITON_SEPARATE_DEPLOYMENT`
- `AWQ_UNFUSED_CONTROL_ONLY`

Failure to recover `awq_ext` does not block Qwen0 formal trace recovery.
