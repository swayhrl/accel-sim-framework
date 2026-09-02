# Validation summary

Passed local/static checks after pilot fixes:

- `py_compile` for capture preflight, workload, and P4 diagnostic;
- `bash -n` for changed launch/bootstrap scripts;
- capture-ready toolchain provenance self-test;
- Llama wrapper/KV self-test;
- kernel classifier self-test.

Passed real-host checks:

- host-only preflight;
- selected CUDA 12.6 `nvcc`/`ptxas` identity;
- PyTorch sees four SM86 devices;
- checksum-verified NVBit bootstrap/build;
- capture-ready preflight;
- generic injection/postprocess/archive/integrity smoke;
- four-rank smoke and rank0-only trace-injection proof.

The absence of a usable gated-model credential is deliberately a BLOCKED
result, not a failed model or trace validation.
